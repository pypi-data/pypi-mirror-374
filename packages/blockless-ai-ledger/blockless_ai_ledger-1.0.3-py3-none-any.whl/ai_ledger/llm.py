"""
LLM backend integrations with safety rails and fallbacks.

Supports OpenAI, stub testing, and rule-only modes with comprehensive
error handling and fail-closed security posture.
"""

from abc import ABC, abstractmethod
import json
import re
import os
import logging
from typing import Dict, List, Optional, Any

from . import params

logger = logging.getLogger(__name__)


class LLMBackend(ABC):
    """Abstract base class for LLM backends."""
    
    @abstractmethod
    async def evaluate(self, tx: Dict, history: List[Dict], rules: Dict) -> Dict:
        """
        Evaluate a transaction using the LLM backend.
        
        Args:
            tx: Transaction data dictionary
            history: Recent transaction history
            rules: Rule-based validation results
            
        Returns:
            Dictionary with evaluation results
        """
        pass


class OpenAIBackend(LLMBackend):
    """Production OpenAI integration with comprehensive safety measures."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable required")
            
            self.client = openai.AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI backend initialized successfully")
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai>=1.0.0")
    
    def _truncate_for_tokens(self, text: str, max_chars: int = 200) -> str:
        """
        Truncate text to fit within token limits.
        
        Args:
            text: Text to truncate
            max_chars: Maximum characters to keep
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) > max_chars:
            return text[:max_chars-3] + "..."
        return text
    
    def _sanitize_for_prompt(self, text: str) -> str:
        """Additional sanitization for LLM prompts."""
        # Remove potential prompt injections
        text = re.sub(r'(ignore|forget|override).*(previous|above|instructions)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(act as|pretend to be|roleplay)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```[^`]*```', '[code block removed]', text)
        
        return text.strip()
    
    async def evaluate(self, tx: Dict, history: List[Dict], rules: Dict) -> Dict:
        """
        Call OpenAI with deterministic settings and safety measures.
        
        Args:
            tx: Transaction data
            history: Recent history
            rules: Rule validation results
            
        Returns:
            Structured evaluation result
        """
        system_prompt = """You are a conservative transaction validator for an AI-first ledger system.
Your role is to add human-like judgment on top of deterministic rule checking.

Core principles:
- CONSERVATIVE: Reject ambiguous or suspicious requests
- CONSISTENT: Apply the same standards to similar transactions  
- PROTECTIVE: Flag unusual patterns that might indicate fraud or mistakes
- EXPLAINABLE: Provide clear, actionable reasons for decisions

You must respond with valid JSON only, using this exact structure:
{
  "valid": boolean,
  "reasons": [string array, maximum 3 concise reasons],
  "risk_score": float between 0.0 and 1.0,
  "evidence": {
    "pattern_match": string or null,
    "anomaly_detected": boolean,
    "confidence": float between 0.0 and 1.0
  }
}

Risk scoring guidelines:
- 0.0-0.2: Normal, expected transaction
- 0.2-0.4: Minor concerns, likely legitimate  
- 0.4-0.6: Moderate risk, requires attention
- 0.6-0.8: High risk, likely problematic
- 0.8-1.0: Very high risk, almost certainly invalid"""

        # Prepare truncated transaction for LLM
        tx_for_llm = tx.copy()
        if 'description' in tx_for_llm:
            original_desc = tx_for_llm['description']
            tx_for_llm['description'] = self._truncate_for_tokens(
                self._sanitize_for_prompt(original_desc), 
                max_chars=200
            )
        
        # Build user prompt with context
        user_prompt = f"""Evaluate this transaction:

Transaction:
{json.dumps(tx_for_llm, indent=2)}

Recent transaction history (last 5):
{json.dumps(history[-5:] if history else [], indent=2)}

Rule validation results:
{json.dumps(rules, indent=2)}

Please evaluate this transaction and respond with the required JSON structure."""

        try:
            # Make API call with strict parameters
            response = await self.client.chat.completions.create(
                model=params.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=params.LLM_TEMPERATURE,
                max_tokens=params.LLM_MAX_TOKENS,
                response_format={"type": "json_object"},
                timeout=5.0  # 5 second timeout
            )
            
            # Parse and validate response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Validate response schema
            required_fields = ['valid', 'reasons', 'risk_score', 'evidence']
            if not all(field in result for field in required_fields):
                raise ValueError(f"Missing required fields. Got: {list(result.keys())}")
            
            # Validate and clamp risk score
            risk_score = float(result['risk_score'])
            result['risk_score'] = max(0.0, min(1.0, risk_score))
            
            # Validate reasons format
            reasons = result['reasons']
            if not isinstance(reasons, list) or len(reasons) > 5:
                result['reasons'] = reasons[:3] if isinstance(reasons, list) else ["Invalid reasons format"]
            
            # Ensure evidence structure
            if not isinstance(result.get('evidence'), dict):
                result['evidence'] = {
                    "pattern_match": None,
                    "anomaly_detected": False,
                    "confidence": 0.5
                }
            
            # Add metadata
            result['evidence']['api_model'] = params.OPENAI_MODEL
            result['evidence']['response_time_ms'] = getattr(response, 'response_ms', None)
            
            logger.debug(f"OpenAI evaluation: valid={result['valid']}, risk={result['risk_score']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"OpenAI returned invalid JSON: {e}")
            
            # Try once more with explicit JSON request
            try:
                retry_response = await self._retry_with_explicit_json(system_prompt, user_prompt)
                return json.loads(retry_response)
            except Exception as retry_e:
                logger.error(f"OpenAI retry also failed: {retry_e}")
                return self._create_failure_response("AI response parsing failed")
        
        except Exception as e:
            logger.error(f"OpenAI evaluation failed: {e}")
            return self._create_failure_response(f"AI evaluation error: {str(e)}")
    
    async def _retry_with_explicit_json(self, system_prompt: str, user_prompt: str) -> str:
        """Retry with explicit JSON formatting request."""
        retry_prompt = user_prompt + "\n\nIMPORTANT: Respond with valid JSON only, no other text."
        
        response = await self.client.chat.completions.create(
            model=params.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": retry_prompt}
            ],
            temperature=0.0,  # Even more deterministic for retry
            max_tokens=150,   # Shorter response for retry
            timeout=3.0
        )
        
        return response.choices[0].message.content
    
    def _create_failure_response(self, error_msg: str) -> Dict:
        """Create standardized failure response."""
        return {
            "valid": False,
            "reasons": ["AI evaluation failed - failing closed for safety"],
            "risk_score": 0.9,
            "evidence": {
                "pattern_match": None,
                "anomaly_detected": True,
                "confidence": 0.1,
                "error": error_msg,
                "backend": "openai"
            }
        }


class StubBackend(LLMBackend):
    """Deterministic stub backend for testing and development."""
    
    async def evaluate(self, tx: Dict, history: List[Dict], rules: Dict) -> Dict:
        """
        Deterministic evaluation based on transaction content.
        
        Args:
            tx: Transaction data
            history: Recent history (unused in stub)
            rules: Rule results
            
        Returns:
            Deterministic evaluation result
        """
        description = tx.get('description', '').lower()
        amount_str = str(tx.get('amount', '0'))
        
        # Extract numeric amount if it includes asset (e.g., "25.0 LABS" -> "25.0")
        if ' ' in amount_str:
            amount_str = amount_str.split()[0]
        
        # Deterministic risk calculation
        risk = 0.1  # Base risk
        reasons = ["Stub validation"]
        
        # Pattern-based risk adjustments
        if any(word in description for word in ['lunch', 'coffee', 'meal']):
            risk = 0.15
            reasons = ["Normal meal transaction"]
        elif any(word in description for word in ['suspicious', 'hack', 'steal']):
            risk = 0.8
            reasons = ["Suspicious pattern detected"]
        elif any(word in description for word in ['urgent', 'emergency', 'asap']):
            risk = 0.3
            reasons = ["Urgent transaction pattern"]
        elif any(word in description for word in ['refund', 'return']):
            risk = 0.2
            reasons = ["Refund transaction"]
        
        # Amount-based adjustments
        try:
            from decimal import Decimal
            amount = Decimal(amount_str)
            if amount > Decimal('100'):
                risk = min(1.0, risk + 0.1)
                reasons.append("Large amount")
            elif amount < Decimal('1'):
                risk = min(1.0, risk + 0.05)
                reasons.append("Very small amount")
        except:
            risk = 0.7
            reasons = ["Invalid amount format"]
        
        # Rule-based adjustments
        all_rules_pass = all(rules.values()) if rules else True
        if not all_rules_pass:
            risk = max(0.6, risk)
            reasons = ["Rule violations detected"]
        
        valid = risk < 0.5
        
        return {
            "valid": valid,
            "reasons": reasons[:3],
            "risk_score": round(risk, 3),
            "evidence": {
                "pattern_match": "normal" if risk < 0.3 else "suspicious" if risk > 0.6 else "moderate",
                "anomaly_detected": risk > 0.4,
                "confidence": 0.95,
                "backend": "stub",
                "deterministic": True
            }
        }


class RuleOnlyBackend(LLMBackend):
    """Pure rule-based validation without AI components."""
    
    async def evaluate(self, tx: Dict, history: List[Dict], rules: Dict) -> Dict:
        """
        Evaluation based purely on rule results.
        
        Args:
            tx: Transaction data (used for logging only)
            history: History (unused)
            rules: Rule validation results
            
        Returns:
            Rule-based evaluation
        """
        if not rules:
            return {
                "valid": False,
                "reasons": ["No rules provided"],
                "risk_score": 1.0,
                "evidence": {
                    "pattern_match": None,
                    "anomaly_detected": True,
                    "confidence": 1.0,
                    "backend": "rule_only"
                }
            }
        
        all_rules_pass = all(rules.values())
        failed_rules = [rule for rule, passed in rules.items() if not passed]
        
        if all_rules_pass:
            return {
                "valid": True,
                "reasons": ["All validation rules passed"],
                "risk_score": 0.1,
                "evidence": {
                    "pattern_match": "rule_compliant",
                    "anomaly_detected": False,
                    "confidence": 1.0,
                    "backend": "rule_only",
                    "rules_passed": len(rules)
                }
            }
        else:
            return {
                "valid": False,
                "reasons": [f"Failed rules: {', '.join(failed_rules[:3])}"],
                "risk_score": 0.7,
                "evidence": {
                    "pattern_match": "rule_violation",
                    "anomaly_detected": True,
                    "confidence": 1.0,
                    "backend": "rule_only",
                    "failed_rules": failed_rules[:5]
                }
            }


def get_llm() -> LLMBackend:
    """
    Factory function to get appropriate LLM backend.
    
    Returns:
        LLM backend instance based on configuration
        
    Raises:
        ValueError: If LLM_MODE is invalid
    """
    mode = params.LLM_MODE.lower()
    
    if mode == "openai":
        return OpenAIBackend()
    elif mode == "stub":
        return StubBackend()
    elif mode == "rule_only":
        return RuleOnlyBackend()
    else:
        raise ValueError(f"Unknown LLM_MODE: {params.LLM_MODE}. Use 'openai', 'stub', or 'rule_only'")


async def test_llm_backend(backend: LLMBackend) -> Dict[str, Any]:
    """
    Test an LLM backend with sample data.
    
    Args:
        backend: LLM backend to test
        
    Returns:
        Test results dictionary
    """
    test_tx = {
        "id": "test123",
        "description": "Alice pays Bob 25 LABS for lunch",
        "from_account": "alice",
        "to_account": "bob",
        "amount": "25.0",
        "nonce": 1
    }
    
    test_rules = {
        "valid_format": True,
        "sufficient_balance": True,
        "valid_nonce": True,
        "different_accounts": True,
        "positive_amount": True
    }
    
    test_history = [
        {"description": "Previous transaction", "amount": "10.0"}
    ]
    
    try:
        start_time = datetime.now()
        result = await backend.evaluate(test_tx, test_history, test_rules)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "success": True,
            "response_time_ms": response_time,
            "result": result,
            "backend_type": result.get("evidence", {}).get("backend", "unknown")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "backend_type": "unknown"
        }


# Import datetime for test function
from datetime import datetime