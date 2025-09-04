"""
Validator system for AI-powered transaction validation.

Handles AI model integration, rule-based validation, and opinion aggregation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
import asyncio
import logging

from . import params
from .transaction import Transaction

logger = logging.getLogger(__name__)


class ValidatorOpinion(BaseModel):
    """Opinion from a validator about a transaction."""
    
    schema_version: int = params.SCHEMA_VERSION
    validator_id: str
    tx_id: str
    valid: bool
    risk_score: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = Field(max_items=5)
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)
    evaluation_time_ms: Optional[int] = None
    llm_evidence: Optional[Dict[str, Any]] = None
    signature: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_display_dict(self) -> dict:
        """Create display-friendly dictionary."""
        return {
            "validator": self.validator_id[:8] + "..." if len(self.validator_id) > 8 else self.validator_id,
            "valid": "✓" if self.valid else "✗",
            "risk": f"{self.risk_score:.2f}",
            "reasons": self.reasons[:2],  # Show first 2 reasons
            "confidence": f"{self.confidence:.2f}"
        }


class Validator(BaseModel):
    """AI validator that evaluates transactions."""
    
    id: str
    pubkey_hex: str
    privkey_hex: Optional[str] = None  # Only for local validators
    endpoint: Optional[str] = None
    reputation: float = Field(default=params.INITIAL_VALIDATOR_REPUTATION, ge=0.0, le=1.0)
    is_active: bool = True
    last_seen: Optional[str] = None
    total_evaluations: int = 0
    successful_evaluations: int = 0
    
    async def evaluate_transaction(
        self, 
        tx: Transaction, 
        account_manager,
        recent_history: List[Dict] = None
    ) -> ValidatorOpinion:
        """
        Evaluate a transaction using rule-based + AI validation.
        
        Args:
            tx: Transaction to evaluate
            account_manager: Account state manager
            recent_history: Recent transactions for context
            
        Returns:
            Validator opinion
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Rule-based validation
            rule_results = await self._check_rules(tx, account_manager)
            
            # Step 2: AI evaluation (if enabled)
            llm_results = await self._evaluate_with_llm(
                tx, 
                recent_history or [], 
                rule_results
            )
            
            # Step 3: Combine results
            opinion = self._combine_evaluations(
                tx, 
                rule_results, 
                llm_results,
                start_time
            )
            
            # Step 4: Sign opinion (if we have private key)
            if self.privkey_hex:
                opinion.signature = self._sign_opinion(opinion)
            
            self.total_evaluations += 1
            if opinion.valid:
                self.successful_evaluations += 1
            
            return opinion
            
        except Exception as e:
            logger.error(f"Validator {self.id} evaluation failed: {e}")
            
            # Fail closed with high risk
            evaluation_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ValidatorOpinion(
                validator_id=self.id,
                tx_id=tx.id,
                valid=False,
                risk_score=0.9,
                reasons=["Validator evaluation failed - failing closed for safety"],
                confidence=0.1,
                evaluation_time_ms=int(evaluation_time),
                llm_evidence={"error": str(e)}
            )
    
    async def _check_rules(self, tx: Transaction, account_manager) -> dict:
        """Run rule-based validation checks."""
        rules = {}
        
        # Basic format validation
        rules["valid_format"] = tx.is_valid_format()
        
        # Account validation
        is_valid, error_msg = account_manager.validate_transaction(tx)
        rules["sufficient_balance"] = is_valid
        rules["valid_nonce"] = "nonce" not in error_msg.lower() if not is_valid else True
        rules["different_accounts"] = tx.from_acct != tx.to_acct
        
        # Amount validation
        amount = tx.get_amount_decimal()
        rules["positive_amount"] = amount > 0
        rules["reasonable_amount"] = amount <= params.GENESIS_SUPPLY  # Basic sanity check
        
        # Description validation
        desc = tx.nl_description.lower()
        rules["has_description"] = len(desc.strip()) > 0
        rules["reasonable_length"] = len(desc) <= params.MAX_NL_DESCRIPTION_LEN
        
        # Suspicious pattern detection
        suspicious_words = ["test", "hack", "exploit", "steal", "fraud"]
        rules["no_suspicious_words"] = not any(word in desc for word in suspicious_words)
        
        return rules
    
    async def _evaluate_with_llm(
        self, 
        tx: Transaction, 
        history: List[Dict], 
        rules: Dict
    ) -> dict:
        """Evaluate transaction using LLM backend."""
        try:
            from .llm import get_llm
            
            llm = get_llm()
            
            # Prepare transaction data for LLM
            tx_data = {
                "id": tx.id[:16] + "...",
                "description": tx.nl_description,
                "from_account": tx.from_acct,
                "to_account": tx.to_acct,
                "amount": f"{tx.amount} {tx.asset}",
                "nonce": tx.nonce
            }
            
            result = await llm.evaluate(tx_data, history, rules)
            return result
            
        except ImportError:
            # LLM backend not available, use rule-only
            all_rules_pass = all(rules.values())
            return {
                "valid": all_rules_pass,
                "reasons": ["All rules passed"] if all_rules_pass else ["Rule violations detected"],
                "risk_score": 0.1 if all_rules_pass else 0.7,
                "evidence": {
                    "pattern_match": None,
                    "anomaly_detected": not all_rules_pass,
                    "confidence": 1.0,
                    "llm_unavailable": True
                }
            }
        except Exception as e:
            logger.warning(f"LLM evaluation failed: {e}")
            # Fail with moderate risk
            return {
                "valid": False,
                "reasons": ["LLM evaluation failed"],
                "risk_score": 0.8,
                "evidence": {
                    "error": str(e),
                    "confidence": 0.1
                }
            }
    
    def _combine_evaluations(
        self, 
        tx: Transaction, 
        rules: Dict, 
        llm: Dict,
        start_time: datetime
    ) -> ValidatorOpinion:
        """Combine rule-based and LLM evaluations into final opinion."""
        
        # Rules must pass for transaction to be valid
        rules_pass = all(rules.values())
        llm_valid = llm.get("valid", False)
        
        # Final validity is AND of rules and LLM
        final_valid = rules_pass and llm_valid
        
        # Risk score is max of rule risk and LLM risk
        rule_risk = 0.1 if rules_pass else 0.8
        llm_risk = llm.get("risk_score", 0.5)
        final_risk = max(rule_risk, llm_risk)
        
        # Combine reasons
        reasons = []
        if not rules_pass:
            failed_rules = [rule for rule, passed in rules.items() if not passed]
            reasons.extend([f"Rule failed: {rule}" for rule in failed_rules[:2]])
        
        llm_reasons = llm.get("reasons", [])
        reasons.extend(llm_reasons[:3])  # Add up to 3 LLM reasons
        
        # Limit total reasons
        reasons = reasons[:5]
        
        # Calculate confidence
        rule_confidence = 1.0 if rules_pass else 0.8
        llm_confidence = llm.get("evidence", {}).get("confidence", 0.5)
        final_confidence = min(rule_confidence, llm_confidence)
        
        evaluation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ValidatorOpinion(
            validator_id=self.id,
            tx_id=tx.id,
            valid=final_valid,
            risk_score=final_risk,
            reasons=reasons,
            confidence=final_confidence,
            evaluation_time_ms=int(evaluation_time),
            llm_evidence=llm.get("evidence")
        )
    
    def _sign_opinion(self, opinion: ValidatorOpinion) -> str:
        """Sign the validator opinion."""
        try:
            from . import crypto
            
            privkey = bytes.fromhex(self.privkey_hex)
            
            # Create params hash for signature
            params_hash = self._get_params_hash()
            
            return crypto.create_opinion_signature(
                tx_id=opinion.tx_id,
                validator_id=opinion.validator_id,
                valid=opinion.valid,
                risk_score=opinion.risk_score,
                reasons=opinion.reasons,
                privkey=privkey,
                params_hash=params_hash
            )
        except Exception as e:
            logger.error(f"Failed to sign opinion: {e}")
            return ""
    
    def _get_params_hash(self) -> str:
        """Get hash of consensus parameters."""
        from . import canonical_json
        
        params_dict = {
            "schema_version": params.SCHEMA_VERSION,
            "n_validators": params.N_VALIDATORS,
            "quorum_k": params.QUORUM_K,
            "max_risk_avg": str(params.MAX_RISK_AVG)
        }
        return canonical_json.compute_hash(params_dict)
    
    def update_reputation(self, success: bool, weight: float = 1.0):
        """Update validator reputation based on performance."""
        if success:
            self.reputation = min(1.0, self.reputation + (weight * 0.1))
        else:
            self.reputation = max(0.0, self.reputation - (weight * 0.2))
    
    def is_eligible(self) -> bool:
        """Check if validator is eligible for selection."""
        return (
            self.is_active and
            self.reputation >= params.MIN_REPUTATION_FOR_SELECTION
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "pubkey_hex": self.pubkey_hex,
            "endpoint": self.endpoint,
            "reputation": self.reputation,
            "is_active": self.is_active,
            "last_seen": self.last_seen,
            "total_evaluations": self.total_evaluations,
            "successful_evaluations": self.successful_evaluations
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Validator":
        """Create validator from dictionary."""
        return cls(**data)


class ValidatorPool:
    """Manages pool of available validators."""
    
    def __init__(self):
        """Initialize empty validator pool."""
        self.validators: Dict[str, Validator] = {}
    
    def add_validator(self, validator: Validator):
        """Add validator to pool."""
        self.validators[validator.id] = validator
    
    def remove_validator(self, validator_id: str):
        """Remove validator from pool."""
        if validator_id in self.validators:
            del self.validators[validator_id]
    
    def get_validator(self, validator_id: str) -> Optional[Validator]:
        """Get validator by ID."""
        return self.validators.get(validator_id)
    
    def select_validators(self, count: int = params.N_VALIDATORS) -> List[Validator]:
        """
        Select validators for evaluation.
        
        Uses reputation-weighted selection.
        
        Args:
            count: Number of validators to select
            
        Returns:
            List of selected validators
        """
        eligible = [v for v in self.validators.values() if v.is_eligible()]
        
        if len(eligible) < count:
            logger.warning(f"Only {len(eligible)} eligible validators, need {count}")
            return eligible
        
        # Sort by reputation (higher first) and select top N
        eligible.sort(key=lambda v: v.reputation, reverse=True)
        return eligible[:count]
    
    def get_active_validators(self) -> List[Validator]:
        """Get all active validators."""
        return [v for v in self.validators.values() if v.is_active]
    
    def update_all_reputations(self, decay_factor: float = params.REPUTATION_DECAY_FACTOR):
        """Apply reputation decay to all validators."""
        for validator in self.validators.values():
            validator.reputation *= decay_factor
    
    def get_pool_stats(self) -> dict:
        """Get statistics about validator pool."""
        validators = list(self.validators.values())
        active = [v for v in validators if v.is_active]
        eligible = [v for v in active if v.is_eligible()]
        
        avg_reputation = sum(v.reputation for v in active) / len(active) if active else 0
        
        return {
            "total_validators": len(validators),
            "active_validators": len(active),
            "eligible_validators": len(eligible),
            "average_reputation": avg_reputation,
            "min_reputation": min(v.reputation for v in active) if active else 0,
            "max_reputation": max(v.reputation for v in active) if active else 0
        }