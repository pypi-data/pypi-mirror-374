"""
Transaction model with comprehensive validation.

Handles natural language transactions with proper decimal math,
timestamp validation, and security features.
"""

from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional
import re

from . import params
from . import canonical_json


class Transaction(BaseModel):
    """
    A transaction in the AI Ledger system.
    
    Represents a transfer with natural language description,
    cryptographic integrity, and comprehensive validation.
    """
    
    schema_version: int = params.SCHEMA_VERSION
    id: str = ""  # Computed via canonical hash
    timestamp: str  # RFC3339 with timezone
    nl_description: str = Field(max_length=params.MAX_NL_DESCRIPTION_LEN)
    from_acct: str = Field(pattern="^[a-z0-9_]{3,32}$")
    to_acct: str = Field(pattern="^[a-z0-9_]{3,32}$")
    asset: str = Field(pattern="^[A-Z]{3,10}$")
    amount: str  # String representation of decimal
    nonce: int = Field(ge=0)
    prev_receipt_id_hint: Optional[str] = None
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure RFC3339 with timezone and check clock skew."""
        try:
            # Parse timestamp with timezone
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                raise ValueError("Timestamp must include timezone")
            
            # Check clock skew
            now = datetime.now(timezone.utc)
            skew_seconds = abs((now - dt).total_seconds())
            if skew_seconds > params.MAX_CLOCK_SKEW_SECS:
                raise ValueError(f"Clock skew {skew_seconds}s exceeds {params.MAX_CLOCK_SKEW_SECS}s")
            
            return v
        except Exception as e:
            raise ValueError(f"Invalid timestamp: {e}")
    
    @validator('amount')
    def validate_amount(cls, v, values):
        """Validate amount as proper decimal with asset-specific precision."""
        try:
            amount = Decimal(v)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            if 'e' in v.lower() or 'E' in v:
                raise ValueError("Scientific notation not allowed")
            
            # Check decimal places for the asset
            asset = values.get('asset', params.DEFAULT_ASSET)
            max_decimals = params.ASSET_DECIMALS.get(asset, 18)
            
            # Count decimal places
            if '.' in v:
                decimal_places = len(v.split('.')[1])
                if decimal_places > max_decimals:
                    raise ValueError(f"Too many decimal places for {asset}: max {max_decimals}")
            
            return v
        except Exception as e:
            raise ValueError(f"Invalid amount: {e}")
    
    @validator('nl_description')
    def sanitize_description(cls, v):
        """Remove potential prompt injections and validate content."""
        if params.PROMPT_SANITIZE:
            # Strip control characters
            v = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', v)
            
            # Reject base64-like content (likely encoded attacks)
            if re.search(r'[A-Za-z0-9+/]{50,}={0,2}', v):
                raise ValueError("Suspected base64 content")
            
            # Reject URLs (potential for external references)
            if re.search(r'https?://|www\.', v, re.IGNORECASE):
                raise ValueError("URLs not allowed in descriptions")
            
            # Reject abnormally long words (likely garbage/attacks)
            words = v.split()
            if any(len(w) > 50 for w in words):
                raise ValueError("Abnormally long words detected")
            
            # Reject excessive whitespace
            if len(v) - len(v.strip()) > 10:
                raise ValueError("Excessive whitespace detected")
        
        return v.strip()
    
    @validator('from_acct', 'to_acct')
    def validate_accounts(cls, v):
        """Validate account identifiers."""
        if not v:
            raise ValueError("Account cannot be empty")
        
        # Check for reserved account names
        reserved = {'system', 'genesis', 'null', 'void'}
        if v.lower() in reserved:
            raise ValueError(f"Account name '{v}' is reserved")
        
        return v
    
    @validator('nonce')
    def validate_nonce(cls, v):
        """Validate nonce is reasonable."""
        if v < 0:
            raise ValueError("Nonce cannot be negative")
        if v > 2**63 - 1:  # Max signed 64-bit int
            raise ValueError("Nonce too large")
        return v
    
    def compute_id(self) -> str:
        """
        Compute deterministic transaction ID from canonical hash.
        
        Returns:
            Transaction ID as hex string
        """
        # Create dict without the id field for hashing
        tx_dict = self.dict(exclude={'id'})
        return canonical_json.compute_hash(tx_dict)
    
    def get_amount_decimal(self) -> Decimal:
        """
        Get amount as Decimal for precise calculations.
        
        Returns:
            Amount as Decimal object
        """
        return Decimal(self.amount)
    
    def validate_account_different(self) -> bool:
        """
        Ensure from_acct and to_acct are different.
        
        Returns:
            True if accounts are different
        """
        return self.from_acct != self.to_acct
    
    def estimate_size(self) -> int:
        """
        Estimate transaction size in bytes.
        
        Returns:
            Estimated size in bytes
        """
        return len(self.json().encode('utf-8'))
    
    def is_valid_format(self) -> bool:
        """
        Check if transaction has valid basic format.
        
        Returns:
            True if format is valid
        """
        try:
            # Basic validation checks
            if not self.validate_account_different():
                return False
            
            if self.get_amount_decimal() <= 0:
                return False
            
            if len(self.nl_description.strip()) == 0:
                return False
            
            return True
        except Exception:
            return False
    
    def to_display_dict(self) -> dict:
        """
        Create display-friendly dictionary.
        
        Returns:
            Dictionary with readable formatting
        """
        return {
            "id": self.id[:16] + "..." if len(self.id) > 16 else self.id,
            "timestamp": self.timestamp,
            "description": self.nl_description,
            "from": self.from_acct,
            "to": self.to_acct,
            "amount": f"{self.amount} {self.asset}",
            "nonce": self.nonce
        }


class SubmitRequest(BaseModel):
    """Request to submit a new transaction."""
    
    nl_description: str = Field(max_length=params.MAX_NL_DESCRIPTION_LEN)
    from_acct: str = Field(pattern="^[a-z0-9_]{3,32}$")
    to_acct: str = Field(pattern="^[a-z0-9_]{3,32}$")
    asset: str = Field(default=params.DEFAULT_ASSET, pattern="^[A-Z]{3,10}$")
    amount: str
    nonce: int = Field(ge=0)
    prev_receipt_id_hint: Optional[str] = None


class SubmitResponse(BaseModel):
    """Response from transaction submission."""
    
    transaction_id: str
    status: str  # "pending", "already_pending", "rejected"
    message: Optional[str] = None
    estimated_finality_time: Optional[float] = None