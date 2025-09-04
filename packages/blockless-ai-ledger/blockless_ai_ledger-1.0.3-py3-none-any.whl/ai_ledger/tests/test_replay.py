"""
Test replay attack protection.

Ensures the system prevents duplicate transactions and nonce reuse attacks.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal

from ai_ledger.transaction import Transaction
from ai_ledger.account import AccountManager
from ai_ledger.storage import Storage
from ai_ledger.quorum import Receipt, QuorumOutcome
from ai_ledger.validator import ValidatorOpinion
from ai_ledger import params


class TestReplayProtection:
    """Test replay attack protection mechanisms."""
    
    @pytest.fixture
    def account_manager(self):
        """Create account manager with initial balances."""
        manager = AccountManager()
        # Set up accounts with balances
        alice = manager.get_account("alice")
        alice.balances[params.DEFAULT_ASSET] = Decimal("100.0")
        alice.nonce = 0
        
        bob = manager.get_account("bob")
        bob.balances[params.DEFAULT_ASSET] = Decimal("0.0")
        bob.nonce = 0
        
        return manager
    
    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction."""
        return Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="Alice pays Bob 10 LABS for lunch",
            from_acct="alice",
            to_acct="bob",
            asset=params.DEFAULT_ASSET,
            amount="10.0",
            nonce=1
        )
    
    def test_nonce_sequence_validation(self, account_manager, sample_transaction):
        """Test that nonces must be sequential."""
        # First transaction should be valid (nonce 1, current nonce 0)
        is_valid, error = account_manager.validate_transaction(sample_transaction)
        assert is_valid == True
        
        # Apply the transaction
        account_manager.apply_transaction(sample_transaction, "receipt_1")
        
        # Same nonce should now be invalid
        duplicate_tx = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="Different description but same nonce",
            from_acct="alice",
            to_acct="bob",
            asset=params.DEFAULT_ASSET,
            amount="5.0",
            nonce=1  # Same nonce as before
        )
        
        is_valid, error = account_manager.validate_transaction(duplicate_tx)
        assert is_valid == False
        assert "nonce" in error.lower()
    
    def test_transaction_id_uniqueness(self):
        """Test that identical transactions have identical IDs."""
        tx1 = Transaction(
            timestamp="2025-01-01T12:00:00Z",
            nl_description="Test payment",
            from_acct="alice",
            to_acct="bob",
            asset="LABS",
            amount="10.0",
            nonce=1
        )
        
        tx2 = Transaction(
            timestamp="2025-01-01T12:00:00Z",
            nl_description="Test payment",
            from_acct="alice", 
            to_acct="bob",
            asset="LABS",
            amount="10.0",
            nonce=1
        )
        
        tx1.id = tx1.compute_id()
        tx2.id = tx2.compute_id()
        
        assert tx1.id == tx2.id
    
    def test_transaction_id_difference(self):
        """Test that different transactions have different IDs."""
        base_tx = Transaction(
            timestamp="2025-01-01T12:00:00Z",
            nl_description="Test payment",
            from_acct="alice",
            to_acct="bob", 
            asset="LABS",
            amount="10.0",
            nonce=1
        )
        
        # Different amount
        different_amount = Transaction(
            timestamp="2025-01-01T12:00:00Z",
            nl_description="Test payment",
            from_acct="alice",
            to_acct="bob",
            asset="LABS",
            amount="20.0",  # Different
            nonce=1
        )
        
        # Different nonce
        different_nonce = Transaction(
            timestamp="2025-01-01T12:00:00Z",
            nl_description="Test payment",
            from_acct="alice",
            to_acct="bob",
            asset="LABS",
            amount="10.0",
            nonce=2  # Different
        )
        
        # Different description
        different_desc = Transaction(
            timestamp="2025-01-01T12:00:00Z",
            nl_description="Different description",  # Different
            from_acct="alice",
            to_acct="bob",
            asset="LABS", 
            amount="10.0",
            nonce=1
        )
        
        base_id = base_tx.compute_id()
        amount_id = different_amount.compute_id()
        nonce_id = different_nonce.compute_id()
        desc_id = different_desc.compute_id()
        
        # All should be different
        assert base_id != amount_id
        assert base_id != nonce_id
        assert base_id != desc_id
        assert amount_id != nonce_id
        assert amount_id != desc_id
        assert nonce_id != desc_id
    
    def test_nonce_must_increment(self, account_manager):
        """Test that nonce must increment properly."""
        alice = account_manager.get_account("alice")
        
        # Start at nonce 0
        assert alice.nonce == 0
        
        # Transaction with nonce 1 should be valid
        tx1 = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="First transaction",
            from_acct="alice",
            to_acct="bob",
            asset=params.DEFAULT_ASSET,
            amount="10.0",
            nonce=1
        )
        
        is_valid, _ = account_manager.validate_transaction(tx1)
        assert is_valid == True
        
        # Apply transaction
        account_manager.apply_transaction(tx1, "receipt_1")
        assert alice.nonce == 1
        
        # Transaction with nonce 3 (skipping 2) should be invalid
        tx3 = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="Skipped nonce transaction",
            from_acct="alice",
            to_acct="bob",
            asset=params.DEFAULT_ASSET,
            amount="10.0",
            nonce=3
        )
        
        is_valid, error = account_manager.validate_transaction(tx3)
        assert is_valid == False
        assert "nonce" in error.lower()
        
        # Transaction with nonce 2 should be valid
        tx2 = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="Correct next transaction",
            from_acct="alice",
            to_acct="bob",
            asset=params.DEFAULT_ASSET,
            amount="10.0",
            nonce=2
        )
        
        is_valid, _ = account_manager.validate_transaction(tx2)
        assert is_valid == True
    
    def test_old_nonce_rejection(self, account_manager):
        """Test that old nonces are always rejected."""
        alice = account_manager.get_account("alice")
        
        # Apply several transactions to advance nonce
        for nonce in range(1, 6):
            tx = Transaction(
                timestamp=datetime.now(timezone.utc).isoformat(),
                nl_description=f"Transaction {nonce}",
                from_acct="alice",
                to_acct="bob",
                asset=params.DEFAULT_ASSET,
                amount="1.0",
                nonce=nonce
            )
            account_manager.apply_transaction(tx, f"receipt_{nonce}")
        
        # Alice's nonce should now be 5
        assert alice.nonce == 5
        
        # Try to submit transaction with old nonce
        old_tx = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="Old nonce attack",
            from_acct="alice",
            to_acct="bob", 
            asset=params.DEFAULT_ASSET,
            amount="50.0",  # Large amount
            nonce=3  # Old nonce
        )
        
        is_valid, error = account_manager.validate_transaction(old_tx)
        assert is_valid == False
        assert "nonce" in error.lower()
    
    def test_zero_nonce_rejection(self, account_manager):
        """Test that nonce 0 is always rejected."""
        tx = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="Zero nonce transaction",
            from_acct="alice",
            to_acct="bob",
            asset=params.DEFAULT_ASSET,
            amount="10.0",
            nonce=0  # Invalid nonce
        )
        
        is_valid, error = account_manager.validate_transaction(tx)
        assert is_valid == False
        assert "nonce" in error.lower()
    
    def test_receipt_uniqueness(self):
        """Test that identical receipts have identical IDs."""
        # Create identical receipts
        opinions = [ValidatorOpinion(
            validator_id="validator_1",
            tx_id="tx_123",
            valid=True,
            risk_score=0.1,
            reasons=["Test reason"]
        )]
        
        outcome = QuorumOutcome(
            approved=True,
            valid_count=1,
            total_count=1,
            risk_avg="0.100000",
            params_hash="test_hash"
        )
        
        account_heads = {"alice": "head_1", "bob": "head_2"}
        
        receipt1 = Receipt(
            tx_id="tx_123",
            validator_opinions=opinions,
            quorum_outcome=outcome,
            account_heads=account_heads,
            merkle_root="merkle_root",
            finalized_at="2025-01-01T12:00:00Z",
            params_hash="test_hash"
        )
        
        receipt2 = Receipt(
            tx_id="tx_123", 
            validator_opinions=opinions,
            quorum_outcome=outcome,
            account_heads=account_heads,
            merkle_root="merkle_root",
            finalized_at="2025-01-01T12:00:00Z",
            params_hash="test_hash"
        )
        
        receipt1.receipt_id = receipt1.compute_receipt_id()
        receipt2.receipt_id = receipt2.compute_receipt_id()
        
        assert receipt1.receipt_id == receipt2.receipt_id
    
    def test_timestamp_replay_detection(self):
        """Test detection of transactions with very old timestamps."""
        from datetime import timedelta
        
        # Transaction with very old timestamp
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        
        with pytest.raises(ValueError, match="Clock skew"):
            Transaction(
                timestamp=old_timestamp.isoformat(),
                nl_description="Old transaction",
                from_acct="alice",
                to_acct="bob",
                asset=params.DEFAULT_ASSET,
                amount="10.0",
                nonce=1
            )
    
    def test_future_timestamp_detection(self):
        """Test detection of transactions with future timestamps."""
        from datetime import timedelta
        
        # Transaction with future timestamp
        future_timestamp = datetime.now(timezone.utc) + timedelta(hours=1)
        
        with pytest.raises(ValueError, match="Clock skew"):
            Transaction(
                timestamp=future_timestamp.isoformat(),
                nl_description="Future transaction", 
                from_acct="alice",
                to_acct="bob",
                asset=params.DEFAULT_ASSET,
                amount="10.0",
                nonce=1
            )
    
    def test_concurrent_transaction_protection(self, account_manager):
        """Test protection against concurrent transactions with same nonce."""
        # This simulates what would happen if two transactions with same nonce
        # were submitted concurrently
        
        tx1 = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="First concurrent transaction",
            from_acct="alice",
            to_acct="bob",
            asset=params.DEFAULT_ASSET,
            amount="10.0",
            nonce=1
        )
        
        tx2 = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="Second concurrent transaction",
            from_acct="alice",
            to_acct="bob",
            asset=params.DEFAULT_ASSET,
            amount="20.0",
            nonce=1  # Same nonce
        )
        
        # Both should initially validate (before either is applied)
        is_valid1, _ = account_manager.validate_transaction(tx1)
        is_valid2, _ = account_manager.validate_transaction(tx2)
        
        assert is_valid1 == True
        assert is_valid2 == True
        
        # Apply first transaction
        success1 = account_manager.apply_transaction(tx1, "receipt_1")
        assert success1 == True
        
        # Second transaction should now fail validation
        is_valid2_after, error = account_manager.validate_transaction(tx2)
        assert is_valid2_after == False
        assert "nonce" in error.lower()