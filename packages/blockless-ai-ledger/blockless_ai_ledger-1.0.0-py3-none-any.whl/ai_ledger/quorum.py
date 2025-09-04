"""
Quorum management with Merkle trees and consensus logic.

Handles validator opinion collection, quorum determination,
and tamper-evident receipt generation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timezone
import asyncio
import logging

from . import params
from . import canonical_json
from .transaction import Transaction
from .validator import Validator, ValidatorOpinion

logger = logging.getLogger(__name__)


class QuorumOutcome(BaseModel):
    """Result of quorum consensus process."""
    
    approved: bool
    valid_count: int
    total_count: int
    risk_avg: str  # String representation of average risk
    k_threshold: int = params.QUORUM_K
    params_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Receipt(BaseModel):
    """Tamper-evident receipt for a finalized transaction."""
    
    schema_version: int = params.SCHEMA_VERSION
    tx_id: str
    receipt_id: str = ""  # Computed from receipt content
    validator_opinions: List[ValidatorOpinion]
    quorum_outcome: QuorumOutcome
    account_heads: Dict[str, str]  # account_id -> head_receipt_id
    merkle_root: str  # Root of account heads Merkle tree
    finalized_at: str
    params_hash: str
    
    def compute_receipt_id(self) -> str:
        """Compute deterministic receipt ID."""
        receipt_dict = self.dict(exclude={'receipt_id'})
        return canonical_json.compute_hash(receipt_dict)


class MerkleTree:
    """Proper Merkle tree implementation for account state."""
    
    @staticmethod
    def compute_root(leaves: List[str]) -> str:
        """
        Compute Merkle root from leaf hashes.
        
        Algorithm:
        - Sort leaves lexicographically for deterministic results
        - Pairwise hash until single root remains
        - Odd leaves are promoted to next level
        
        Args:
            leaves: List of hex-encoded leaf hashes
            
        Returns:
            Merkle root as hex string
        """
        if not leaves:
            return canonical_json.compute_hash("")
        
        # Sort leaves for deterministic root
        current_level = sorted(leaves)
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    # Hash pair
                    combined = current_level[i] + current_level[i + 1]
                    next_level.append(canonical_json.compute_hash(combined))
                else:
                    # Odd leaf promoted to next level
                    next_level.append(current_level[i])
            
            current_level = sorted(next_level)
        
        return current_level[0]
    
    @staticmethod
    def create_inclusion_proof(leaf: str, leaves: List[str]) -> Dict:
        """
        Create Merkle inclusion proof for verification.
        
        Args:
            leaf: Target leaf to prove inclusion
            leaves: All leaves in the tree
            
        Returns:
            Dictionary containing proof path and siblings
        """
        if leaf not in leaves:
            return {"valid": False, "error": "Leaf not found"}
        
        sorted_leaves = sorted(leaves)
        leaf_index = sorted_leaves.index(leaf)
        
        proof_path = []
        current_level = sorted_leaves[:]
        current_index = leaf_index
        
        while len(current_level) > 1:
            next_level = []
            
            # Find sibling
            if current_index % 2 == 0:
                # Even index - sibling is to the right
                if current_index + 1 < len(current_level):
                    sibling = current_level[current_index + 1]
                    proof_path.append({"side": "right", "hash": sibling})
                else:
                    # No sibling (odd leaf case)
                    proof_path.append({"side": "none", "hash": None})
            else:
                # Odd index - sibling is to the left
                sibling = current_level[current_index - 1]
                proof_path.append({"side": "left", "hash": sibling})
            
            # Build next level
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                    next_level.append(canonical_json.compute_hash(combined))
                else:
                    next_level.append(current_level[i])
            
            current_level = sorted(next_level)
            current_index = current_index // 2
        
        return {
            "valid": True,
            "leaf": leaf,
            "root": current_level[0],
            "proof_path": proof_path
        }
    
    @staticmethod
    def verify_inclusion_proof(proof: Dict) -> bool:
        """Verify a Merkle inclusion proof."""
        if not proof.get("valid", False):
            return False
        
        current_hash = proof["leaf"]
        
        for step in proof["proof_path"]:
            if step["side"] == "left":
                combined = step["hash"] + current_hash
            elif step["side"] == "right":
                combined = current_hash + step["hash"]
            else:  # side == "none" (odd leaf case)
                combined = current_hash
            
            current_hash = canonical_json.compute_hash(combined)
        
        return current_hash == proof["root"]


class QuorumError(Exception):
    """Exception raised during quorum processing."""
    pass


class QuorumManager:
    """Manages quorum consensus process."""
    
    def __init__(self, validators: List[Validator]):
        """
        Initialize quorum manager.
        
        Args:
            validators: List of validators to use for consensus
        """
        self.validators = validators
        self.params_hash = self._compute_params_hash()
        self._opinion_cache: Dict[str, List[ValidatorOpinion]] = {}
    
    def _compute_params_hash(self) -> str:
        """Hash current consensus parameters."""
        params_dict = {
            "version": params.SCHEMA_VERSION,
            "n_validators": params.N_VALIDATORS,
            "quorum_k": params.QUORUM_K,
            "max_risk_avg": str(params.MAX_RISK_AVG),
            "asset_decimals": params.ASSET_DECIMALS
        }
        return canonical_json.compute_hash(params_dict)
    
    async def collect_opinions(
        self, 
        tx: Transaction, 
        account_manager,
        timeout: float = params.OPINION_TIMEOUT_SECS
    ) -> List[ValidatorOpinion]:
        """
        Collect validator opinions with timeouts and minimum requirements.
        
        Args:
            tx: Transaction to evaluate
            account_manager: Account state manager
            timeout: Per-validator timeout in seconds
            
        Returns:
            List of validator opinions
            
        Raises:
            QuorumError: If minimum validators don't respond
        """
        opinions = []
        tasks = []
        
        # Create evaluation tasks with individual timeouts
        for validator in self.validators:
            task = asyncio.create_task(
                self._get_opinion_with_timeout(validator, tx, account_manager, timeout)
            )
            tasks.append((validator.id, task))
        
        # Collect results as they come in
        collected_validators = set()
        
        for validator_id, task in tasks:
            try:
                opinion = await task
                if opinion and validator_id not in collected_validators:
                    opinions.append(opinion)
                    collected_validators.add(validator_id)
                    
                    logger.debug(f"Got opinion from {validator_id}: "
                               f"valid={opinion.valid}, risk={opinion.risk_score}")
                    
            except asyncio.TimeoutError:
                logger.warning(f"Validator {validator_id} timed out")
            except Exception as e:
                logger.error(f"Validator {validator_id} evaluation failed: {e}")
        
        # Check minimum distinct validators requirement
        if len(collected_validators) < params.MIN_DISTINCT_VALIDATORS:
            raise QuorumError(
                f"Only {len(collected_validators)} validators responded, "
                f"need {params.MIN_DISTINCT_VALIDATORS}"
            )
        
        # Cache opinions for potential reuse
        self._opinion_cache[tx.id] = opinions
        
        return opinions
    
    async def _get_opinion_with_timeout(
        self, 
        validator: Validator, 
        tx: Transaction,
        account_manager,
        timeout: float
    ) -> Optional[ValidatorOpinion]:
        """Get opinion from single validator with timeout."""
        try:
            return await asyncio.wait_for(
                validator.evaluate_transaction(tx, account_manager),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Validator {validator.id} timed out")
            return None
        except Exception as e:
            logger.error(f"Validator {validator.id} failed: {e}")
            return None
    
    def check_quorum(self, opinions: List[ValidatorOpinion]) -> QuorumOutcome:
        """
        Determine quorum outcome from validator opinions.
        
        Args:
            opinions: List of validator opinions
            
        Returns:
            Quorum decision outcome
        """
        if not opinions:
            return QuorumOutcome(
                approved=False,
                valid_count=0,
                total_count=0,
                risk_avg="1.000000",
                params_hash=self.params_hash
            )
        
        valid_count = sum(1 for op in opinions if op.valid)
        total_count = len(opinions)
        
        # Calculate average risk score
        risk_scores = [op.risk_score for op in opinions]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 1.0
        
        # Approval requires K-of-N valid opinions AND low average risk
        approved = (
            valid_count >= params.QUORUM_K and 
            avg_risk <= params.MAX_RISK_AVG
        )
        
        logger.info(f"Quorum result: {valid_count}/{total_count} valid, "
                   f"avg_risk={avg_risk:.3f}, approved={approved}")
        
        return QuorumOutcome(
            approved=approved,
            valid_count=valid_count,
            total_count=total_count,
            risk_avg=f"{avg_risk:.6f}",
            k_threshold=params.QUORUM_K,
            params_hash=self.params_hash
        )
    
    def create_receipt(
        self, 
        tx: Transaction, 
        outcome: QuorumOutcome, 
        opinions: List[ValidatorOpinion], 
        account_heads: Dict[str, str]
    ) -> Receipt:
        """
        Create tamper-evident receipt with Merkle root.
        
        Args:
            tx: Transaction being finalized
            outcome: Quorum decision outcome
            opinions: Validator opinions
            account_heads: Current account head receipt IDs
            
        Returns:
            Finalized receipt
        """
        # Create Merkle tree from account heads
        if account_heads:
            # Sort account heads for deterministic Merkle tree
            sorted_items = sorted(account_heads.items())
            head_ids = [head_id for _, head_id in sorted_items]
            merkle_root = MerkleTree.compute_root(head_ids)
        else:
            merkle_root = MerkleTree.compute_root([])
        
        # Create receipt
        receipt = Receipt(
            tx_id=tx.id,
            validator_opinions=opinions,
            quorum_outcome=outcome,
            account_heads=account_heads,
            merkle_root=merkle_root,
            finalized_at=datetime.now(timezone.utc).isoformat(),
            params_hash=self.params_hash
        )
        
        # Compute and set receipt ID
        receipt.receipt_id = receipt.compute_receipt_id()
        
        return receipt
    
    def verify_receipt(self, receipt: Receipt) -> tuple[bool, List[str]]:
        """
        Verify receipt integrity.
        
        Args:
            receipt: Receipt to verify
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Verify receipt ID
        expected_id = receipt.compute_receipt_id()
        if receipt.receipt_id != expected_id:
            errors.append(f"Receipt ID mismatch: {receipt.receipt_id} != {expected_id}")
        
        # Verify Merkle root
        if receipt.account_heads:
            sorted_items = sorted(receipt.account_heads.items())
            head_ids = [head_id for _, head_id in sorted_items]
            expected_root = MerkleTree.compute_root(head_ids)
            if receipt.merkle_root != expected_root:
                errors.append(f"Merkle root mismatch: {receipt.merkle_root} != {expected_root}")
        
        # Verify quorum logic
        valid_count = sum(1 for op in receipt.validator_opinions if op.valid)
        if receipt.quorum_outcome.valid_count != valid_count:
            errors.append(f"Valid count mismatch: {receipt.quorum_outcome.valid_count} != {valid_count}")
        
        # Verify risk calculation
        if receipt.validator_opinions:
            risk_scores = [op.risk_score for op in receipt.validator_opinions]
            avg_risk = sum(risk_scores) / len(risk_scores)
            expected_risk = f"{avg_risk:.6f}"
            if receipt.quorum_outcome.risk_avg != expected_risk:
                errors.append(f"Risk average mismatch: {receipt.quorum_outcome.risk_avg} != {expected_risk}")
        
        # Verify approval logic
        expected_approval = (
            valid_count >= params.QUORUM_K and
            float(receipt.quorum_outcome.risk_avg) <= params.MAX_RISK_AVG
        )
        if receipt.quorum_outcome.approved != expected_approval:
            errors.append(f"Approval mismatch: {receipt.quorum_outcome.approved} != {expected_approval}")
        
        return len(errors) == 0, errors
    
    def get_quorum_stats(self) -> dict:
        """Get statistics about quorum performance."""
        cache_size = len(self._opinion_cache)
        
        return {
            "validators_count": len(self.validators),
            "active_validators": sum(1 for v in self.validators if v.is_active),
            "quorum_threshold": params.QUORUM_K,
            "max_risk_threshold": params.MAX_RISK_AVG,
            "opinion_cache_size": cache_size,
            "params_hash": self.params_hash
        }
    
    def clear_opinion_cache(self, tx_id: Optional[str] = None):
        """Clear opinion cache for memory management."""
        if tx_id:
            self._opinion_cache.pop(tx_id, None)
        else:
            self._opinion_cache.clear()
    
    def get_cached_opinions(self, tx_id: str) -> Optional[List[ValidatorOpinion]]:
        """Get cached opinions for a transaction."""
        return self._opinion_cache.get(tx_id)