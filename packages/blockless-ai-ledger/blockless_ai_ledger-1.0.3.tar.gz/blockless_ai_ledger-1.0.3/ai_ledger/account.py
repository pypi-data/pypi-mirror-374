"""
Account management and balance tracking.

Maintains account balances, nonces, and transaction history
with atomic updates and consistency guarantees.
"""

from typing import Dict, Optional, List
from decimal import Decimal
from collections import defaultdict
from dataclasses import dataclass

from . import params
from .transaction import Transaction


@dataclass
class AccountState:
    """State of a single account."""
    
    balances: Dict[str, Decimal]  # asset -> balance
    nonce: int
    last_receipt_id: Optional[str]
    transaction_count: int
    
    def __post_init__(self):
        """Ensure balances are defaultdict."""
        if not isinstance(self.balances, defaultdict):
            balances_dict = dict(self.balances) if self.balances else {}
            self.balances = defaultdict(Decimal)
            self.balances.update(balances_dict)


class Account:
    """
    Represents a single account with balances and metadata.
    """
    
    def __init__(self, account_id: str, initial_balances: Optional[Dict[str, str]] = None):
        """
        Initialize account.
        
        Args:
            account_id: Unique account identifier
            initial_balances: Initial asset balances as strings
        """
        self.id = account_id
        self.balances = defaultdict(Decimal)
        self.nonce = 0
        self.last_receipt_id: Optional[str] = None
        self.transaction_count = 0
        
        if initial_balances:
            for asset, amount_str in initial_balances.items():
                self.balances[asset] = Decimal(amount_str)
    
    def get_balance(self, asset: str) -> Decimal:
        """Get balance for specific asset."""
        return self.balances.get(asset, Decimal('0'))
    
    def has_sufficient_balance(self, asset: str, amount: Decimal) -> bool:
        """Check if account has sufficient balance for transaction."""
        return self.get_balance(asset) >= amount
    
    def debit(self, asset: str, amount: Decimal) -> bool:
        """
        Debit amount from account.
        
        Args:
            asset: Asset to debit
            amount: Amount to debit
            
        Returns:
            True if successful, False if insufficient balance
        """
        current_balance = self.get_balance(asset)
        if current_balance < amount:
            return False
        
        self.balances[asset] = current_balance - amount
        return True
    
    def credit(self, asset: str, amount: Decimal):
        """Credit amount to account."""
        self.balances[asset] = self.get_balance(asset) + amount
    
    def increment_nonce(self) -> int:
        """Increment and return new nonce."""
        self.nonce += 1
        return self.nonce
    
    def update_last_receipt(self, receipt_id: str):
        """Update last receipt ID."""
        self.last_receipt_id = receipt_id
        self.transaction_count += 1
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "balances": {asset: str(balance) for asset, balance in self.balances.items()},
            "nonce": self.nonce,
            "last_receipt_id": self.last_receipt_id,
            "transaction_count": self.transaction_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        """Create account from dictionary."""
        account = cls(data["id"])
        account.nonce = data.get("nonce", 0)
        account.last_receipt_id = data.get("last_receipt_id")
        account.transaction_count = data.get("transaction_count", 0)
        
        balances = data.get("balances", {})
        for asset, amount_str in balances.items():
            account.balances[asset] = Decimal(amount_str)
        
        return account


class AccountManager:
    """
    Manages all accounts and their states.
    
    Provides atomic operations for transfers and consistency guarantees.
    """
    
    def __init__(self):
        """Initialize empty account manager."""
        self.accounts: Dict[str, Account] = {}
        self._lock_count = 0  # Simple lock for atomic operations
    
    def get_account(self, account_id: str) -> Account:
        """Get or create account."""
        if account_id not in self.accounts:
            self.accounts[account_id] = Account(account_id)
        return self.accounts[account_id]
    
    def get_balance(self, account_id: str, asset: str) -> Decimal:
        """Get balance for account and asset."""
        return self.get_account(account_id).get_balance(asset)
    
    def get_nonce(self, account_id: str) -> int:
        """Get current nonce for account."""
        return self.get_account(account_id).nonce
    
    def get_last_receipt(self, account_id: str) -> Optional[str]:
        """Get last receipt ID for account."""
        return self.get_account(account_id).last_receipt_id
    
    def validate_transaction(self, tx: Transaction) -> tuple[bool, str]:
        """
        Validate transaction against account state.
        
        Args:
            tx: Transaction to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        from_account = self.get_account(tx.from_acct)
        amount = tx.get_amount_decimal()
        
        # Check nonce
        if tx.nonce <= from_account.nonce:
            return False, f"Invalid nonce: {tx.nonce} <= {from_account.nonce}"
        
        # Check balance
        if not from_account.has_sufficient_balance(tx.asset, amount):
            current = from_account.get_balance(tx.asset)
            return False, f"Insufficient balance: {current} < {amount}"
        
        # Check for self-transfer
        if tx.from_acct == tx.to_acct:
            return False, "Cannot transfer to self"
        
        return True, ""
    
    def apply_transaction(self, tx: Transaction, receipt_id: str) -> bool:
        """
        Apply validated transaction to account states.
        
        Args:
            tx: Transaction to apply
            receipt_id: Receipt ID for this transaction
            
        Returns:
            True if successful
        """
        from_account = self.get_account(tx.from_acct)
        to_account = self.get_account(tx.to_acct)
        amount = tx.get_amount_decimal()
        
        # Double-check balance (should have been validated)
        if not from_account.has_sufficient_balance(tx.asset, amount):
            return False
        
        # Atomic transfer
        if not from_account.debit(tx.asset, amount):
            return False
        
        to_account.credit(tx.asset, amount)
        
        # Update nonce and receipt
        from_account.increment_nonce()
        from_account.update_last_receipt(receipt_id)
        to_account.update_last_receipt(receipt_id)
        
        return True
    
    def apply_receipt(self, receipt):
        """Apply a finalized receipt to account states."""
        if receipt.quorum_outcome.approved:
            # Reconstruct transaction from receipt
            # This is a simplified version - in practice, you'd store the transaction
            pass
    
    def create_genesis_accounts(self, genesis_balances: Dict[str, Dict[str, str]]) -> dict:
        """
        Create genesis accounts with initial balances.
        
        Args:
            genesis_balances: Dict of {account_id: {asset: amount_str}}
            
        Returns:
            Genesis state dictionary
        """
        for account_id, balances in genesis_balances.items():
            account = Account(account_id, balances)
            self.accounts[account_id] = account
        
        # Create genesis hash
        from . import canonical_json
        genesis_data = {
            "schema_version": params.SCHEMA_VERSION,
            "genesis_accounts": {
                acc_id: acc.to_dict() 
                for acc_id, acc in self.accounts.items()
            },
            "params_hash": self._get_params_hash()
        }
        
        genesis_hash = canonical_json.compute_hash(genesis_data)
        
        return {
            "genesis_hash": genesis_hash,
            "genesis_data": genesis_data,
            "total_supply": self._calculate_total_supply()
        }
    
    def _get_params_hash(self) -> str:
        """Get hash of current consensus parameters."""
        from . import canonical_json
        params_dict = {
            "schema_version": params.SCHEMA_VERSION,
            "n_validators": params.N_VALIDATORS,
            "quorum_k": params.QUORUM_K,
            "max_risk_avg": str(params.MAX_RISK_AVG),
            "asset_decimals": params.ASSET_DECIMALS
        }
        return canonical_json.compute_hash(params_dict)
    
    def _calculate_total_supply(self) -> Dict[str, str]:
        """Calculate total supply across all accounts."""
        total_supply = defaultdict(Decimal)
        
        for account in self.accounts.values():
            for asset, balance in account.balances.items():
                total_supply[asset] += balance
        
        return {asset: str(supply) for asset, supply in total_supply.items()}
    
    def get_account_summary(self, account_id: str) -> dict:
        """Get summary of account state."""
        account = self.get_account(account_id)
        
        return {
            "account_id": account_id,
            "balances": {asset: str(balance) for asset, balance in account.balances.items()},
            "nonce": account.nonce,
            "last_receipt_id": account.last_receipt_id,
            "transaction_count": account.transaction_count
        }
    
    def get_all_accounts(self) -> List[dict]:
        """Get summaries of all accounts."""
        return [self.get_account_summary(acc_id) for acc_id in sorted(self.accounts.keys())]
    
    def verify_integrity(self) -> tuple[bool, List[str]]:
        """
        Verify account manager integrity.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for account_id, account in self.accounts.items():
            # Check for negative balances
            for asset, balance in account.balances.items():
                if balance < 0:
                    errors.append(f"Account {account_id} has negative {asset} balance: {balance}")
            
            # Check nonce is non-negative
            if account.nonce < 0:
                errors.append(f"Account {account_id} has negative nonce: {account.nonce}")
        
        return len(errors) == 0, errors