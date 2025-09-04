"""
Test quorum consensus mechanics.

Tests validator opinion collection, quorum determination, and receipt generation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

from ai_ledger import params
from ai_ledger.quorum import QuorumManager, MerkleTree, QuorumError, Receipt, QuorumOutcome
from ai_ledger.validator import Validator, ValidatorOpinion
from ai_ledger.transaction import Transaction
from ai_ledger.account import AccountManager


class TestMerkleTree:
    """Test Merkle tree implementation."""
    
    def test_empty_tree(self):
        """Test Merkle root for empty tree."""
        root = MerkleTree.compute_root([])
        # Should be hash of empty string
        from ai_ledger.canonical_json import compute_hash
        expected = compute_hash("")
        assert root == expected
    
    def test_single_leaf(self):
        """Test Merkle root for single leaf."""
        leaves = ["abc123"]
        root = MerkleTree.compute_root(leaves)
        
        assert root == "abc123"  # Single leaf is its own root
    
    def test_two_leaves(self):
        """Test Merkle root for two leaves."""
        leaves = ["leaf1", "leaf2"]
        root = MerkleTree.compute_root(leaves)
        
        # Should be hash of concatenated leaves
        from ai_ledger.canonical_json import compute_hash
        expected = compute_hash("leaf1leaf2")
        assert root == expected
    
    def test_deterministic_ordering(self):
        """Test that leaf order doesn't affect root."""
        leaves1 = ["c", "a", "b"]
        leaves2 = ["a", "b", "c"]
        
        root1 = MerkleTree.compute_root(leaves1)
        root2 = MerkleTree.compute_root(leaves2)
        
        assert root1 == root2  # Should be same due to sorting
    
    def test_odd_number_leaves(self):
        """Test Merkle tree with odd number of leaves."""
        leaves = ["a", "b", "c"]
        root = MerkleTree.compute_root(leaves)
        
        # Should handle odd leaf promotion correctly
        assert len(root) == 64  # Valid hash
    
    def test_inclusion_proof_valid(self):
        """Test Merkle inclusion proof for valid leaf."""
        leaves = ["leaf1", "leaf2", "leaf3", "leaf4"]
        
        proof = MerkleTree.create_inclusion_proof("leaf2", leaves)
        
        assert proof["valid"] == True
        assert proof["leaf"] == "leaf2"
        assert "proof_path" in proof
        assert "root" in proof
    
    def test_inclusion_proof_invalid(self):
        """Test Merkle inclusion proof for invalid leaf."""
        leaves = ["leaf1", "leaf2", "leaf3"]
        
        proof = MerkleTree.create_inclusion_proof("nonexistent", leaves)
        
        assert proof["valid"] == False
        assert "error" in proof
    
    def test_verify_inclusion_proof(self):
        """Test verification of Merkle inclusion proof."""
        leaves = ["a", "b", "c", "d"]
        
        proof = MerkleTree.create_inclusion_proof("b", leaves)
        verified = MerkleTree.verify_inclusion_proof(proof)
        
        assert verified == True


class TestQuorumManager:
    """Test quorum management functionality."""
    
    @pytest.fixture
    def mock_validators(self):
        """Create mock validators for testing."""
        validators = []
        for i in range(params.N_VALIDATORS):
            validator = Mock(spec=Validator)
            validator.id = f"validator_{i}"
            validator.is_active = True
            validators.append(validator)
        return validators
    
    @pytest.fixture
    def quorum_manager(self, mock_validators):
        """Create QuorumManager with mock validators."""
        return QuorumManager(mock_validators)
    
    @pytest.fixture
    def sample_transaction(self):
        """Create sample transaction for testing."""
        return Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            nl_description="Test transaction",
            from_acct="alice",
            to_acct="bob",
            asset="LABS",
            amount="10.0",
            nonce=1
        )
    
    @pytest.fixture
    def account_manager(self):
        """Create account manager for testing."""
        manager = AccountManager()
        # Create accounts with balances
        manager.get_account("alice").balances["LABS"] = Decimal("100.0")
        manager.get_account("bob").balances["LABS"] = Decimal("0.0")
        return manager
    
    def test_params_hash_computation(self, quorum_manager):
        """Test consensus parameters hash computation."""
        params_hash = quorum_manager.params_hash
        
        assert len(params_hash) == 64  # Blake3 hash length
        assert params_hash == quorum_manager._compute_params_hash()
    
    @pytest.mark.asyncio
    async def test_collect_opinions_success(self, quorum_manager, sample_transaction, account_manager):
        """Test successful opinion collection."""
        # Mock validator opinions
        mock_opinions = []
        for i, validator in enumerate(quorum_manager.validators):
            opinion = ValidatorOpinion(
                validator_id=validator.id,
                tx_id=sample_transaction.id,
                valid=True,
                risk_score=0.1,
                reasons=["Test validation"]
            )
            mock_opinions.append(opinion)
            
            # Mock the async evaluate method
            validator.evaluate_transaction = AsyncMock(return_value=opinion)
        
        opinions = await quorum_manager.collect_opinions(sample_transaction, account_manager)
        
        assert len(opinions) >= params.MIN_DISTINCT_VALIDATORS
        assert all(op.tx_id == sample_transaction.id for op in opinions)
    
    @pytest.mark.asyncio
    async def test_collect_opinions_timeout(self, quorum_manager, sample_transaction, account_manager):
        """Test opinion collection with validator timeouts."""
        # Mock some validators to timeout
        for i, validator in enumerate(quorum_manager.validators):
            if i < 3:
                # These validators timeout
                validator.evaluate_transaction = AsyncMock(side_effect=asyncio.TimeoutError())
            else:
                # These validators respond
                opinion = ValidatorOpinion(
                    validator_id=validator.id,
                    tx_id=sample_transaction.id,
                    valid=True,
                    risk_score=0.2,
                    reasons=["Test validation"]
                )
                validator.evaluate_transaction = AsyncMock(return_value=opinion)
        
        opinions = await quorum_manager.collect_opinions(sample_transaction, account_manager)
        
        # Should still get enough opinions
        assert len(opinions) >= params.MIN_DISTINCT_VALIDATORS
    
    @pytest.mark.asyncio
    async def test_collect_opinions_insufficient_validators(self, quorum_manager, sample_transaction, account_manager):
        """Test opinion collection with insufficient responsive validators."""
        # Mock all validators to timeout or fail
        for validator in quorum_manager.validators:
            validator.evaluate_transaction = AsyncMock(side_effect=asyncio.TimeoutError())
        
        with pytest.raises(QuorumError):
            await quorum_manager.collect_opinions(sample_transaction, account_manager)
    
    def test_check_quorum_approved(self, quorum_manager):
        """Test quorum approval with sufficient valid opinions."""
        opinions = []
        for i in range(params.QUORUM_K):
            opinion = ValidatorOpinion(
                validator_id=f"validator_{i}",
                tx_id="test_tx",
                valid=True,
                risk_score=0.1,  # Low risk
                reasons=["Valid transaction"]
            )
            opinions.append(opinion)
        
        outcome = quorum_manager.check_quorum(opinions)
        
        assert outcome.approved == True
        assert outcome.valid_count == params.QUORUM_K
        assert outcome.total_count == params.QUORUM_K
        assert float(outcome.risk_avg) <= params.MAX_RISK_AVG
    
    def test_check_quorum_rejected_insufficient_valid(self, quorum_manager):
        """Test quorum rejection due to insufficient valid opinions."""
        opinions = []
        for i in range(params.QUORUM_K - 1):  # One less than needed
            opinion = ValidatorOpinion(
                validator_id=f"validator_{i}",
                tx_id="test_tx",
                valid=True,
                risk_score=0.1,
                reasons=["Valid transaction"]
            )
            opinions.append(opinion)
        
        # Add one invalid opinion
        opinion = ValidatorOpinion(
            validator_id="validator_invalid",
            tx_id="test_tx",
            valid=False,
            risk_score=0.8,
            reasons=["Invalid transaction"]
        )
        opinions.append(opinion)
        
        outcome = quorum_manager.check_quorum(opinions)
        
        assert outcome.approved == False
        assert outcome.valid_count < params.QUORUM_K
    
    def test_check_quorum_rejected_high_risk(self, quorum_manager):
        """Test quorum rejection due to high average risk."""
        opinions = []
        for i in range(params.QUORUM_K):
            opinion = ValidatorOpinion(
                validator_id=f"validator_{i}",
                tx_id="test_tx",
                valid=True,
                risk_score=0.8,  # High risk
                reasons=["High risk transaction"]
            )
            opinions.append(opinion)
        
        outcome = quorum_manager.check_quorum(opinions)
        
        assert outcome.approved == False
        assert outcome.valid_count == params.QUORUM_K
        assert float(outcome.risk_avg) > params.MAX_RISK_AVG
    
    def test_create_receipt(self, quorum_manager, sample_transaction):
        """Test receipt creation."""
        # Create mock opinions
        opinions = []
        for i in range(params.QUORUM_K):
            opinion = ValidatorOpinion(
                validator_id=f"validator_{i}",
                tx_id=sample_transaction.id,
                valid=True,
                risk_score=0.1,
                reasons=["Valid transaction"]
            )
            opinions.append(opinion)
        
        # Create quorum outcome
        outcome = quorum_manager.check_quorum(opinions)
        
        # Create account heads
        account_heads = {
            "alice": "prev_receipt_alice",
            "bob": "prev_receipt_bob"
        }
        
        receipt = quorum_manager.create_receipt(
            sample_transaction,
            outcome,
            opinions,
            account_heads
        )
        
        assert receipt.tx_id == sample_transaction.id
        assert receipt.quorum_outcome.approved == outcome.approved
        assert len(receipt.validator_opinions) == len(opinions)
        assert receipt.account_heads == account_heads
        assert receipt.merkle_root is not None
        assert receipt.receipt_id is not None
        assert len(receipt.receipt_id) == 64  # Blake3 hash
    
    def test_verify_receipt_valid(self, quorum_manager, sample_transaction):
        """Test verification of valid receipt."""
        # Create valid receipt
        opinions = []
        for i in range(params.QUORUM_K):
            opinion = ValidatorOpinion(
                validator_id=f"validator_{i}",
                tx_id=sample_transaction.id,
                valid=True,
                risk_score=0.1,
                reasons=["Valid transaction"]
            )
            opinions.append(opinion)
        
        outcome = quorum_manager.check_quorum(opinions)
        account_heads = {"alice": "head1", "bob": "head2"}
        
        receipt = quorum_manager.create_receipt(
            sample_transaction,
            outcome,
            opinions,
            account_heads
        )
        
        is_valid, errors = quorum_manager.verify_receipt(receipt)
        
        assert is_valid == True
        assert len(errors) == 0
    
    def test_verify_receipt_invalid_id(self, quorum_manager, sample_transaction):
        """Test verification of receipt with invalid ID."""
        # Create receipt and corrupt ID
        opinions = [ValidatorOpinion(
            validator_id="validator_1",
            tx_id=sample_transaction.id,
            valid=True,
            risk_score=0.1,
            reasons=["Valid transaction"]
        )]
        
        outcome = quorum_manager.check_quorum(opinions)
        receipt = quorum_manager.create_receipt(
            sample_transaction,
            outcome,
            opinions,
            {}
        )
        
        # Corrupt the receipt ID
        receipt.receipt_id = "corrupted_id"
        
        is_valid, errors = quorum_manager.verify_receipt(receipt)
        
        assert is_valid == False
        assert len(errors) > 0
        assert "Receipt ID mismatch" in errors[0]