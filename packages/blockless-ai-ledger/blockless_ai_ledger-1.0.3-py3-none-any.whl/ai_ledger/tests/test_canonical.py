"""
Test canonical JSON serialization for deterministic hashing.

Ensures that identical data structures always produce identical hashes.
"""

import pytest
from decimal import Decimal

from ai_ledger.canonical_json import (
    to_canonical_bytes,
    compute_hash,
    sort_reasons,
    verify_canonical_format,
    compute_merkle_pair_hash
)


class TestCanonicalJSON:
    """Test canonical JSON functionality."""
    
    def test_deterministic_serialization(self):
        """Test that serialization is deterministic."""
        data1 = {"b": 2, "a": 1, "c": 3}
        data2 = {"a": 1, "c": 3, "b": 2}
        
        bytes1 = to_canonical_bytes(data1)
        bytes2 = to_canonical_bytes(data2)
        
        assert bytes1 == bytes2
        assert bytes1 == b'{"a":1,"b":2,"c":3}'
    
    def test_null_omission(self):
        """Test that null values are omitted."""
        data = {"a": 1, "b": None, "c": 3}
        canonical = to_canonical_bytes(data)
        
        assert canonical == b'{"a":1,"c":3}'
    
    def test_decimal_formatting(self):
        """Test decimal number formatting."""
        data = {"amount": Decimal("123.456789")}
        canonical = to_canonical_bytes(data)
        
        # Should be formatted with fixed precision
        assert b'"123.456789"' in canonical
        assert b'1.23456' in canonical  # After quantization
    
    def test_float_formatting(self):
        """Test float formatting consistency."""
        data = {"risk": 0.123456789}
        canonical = to_canonical_bytes(data)
        
        assert b'"0.123457"' in canonical  # 6 decimal places
    
    def test_nested_structures(self):
        """Test nested data structure canonicalization."""
        data = {
            "outer": {
                "z": 3,
                "a": 1,
                "nested": {
                    "list": [3, 1, 2],
                    "decimal": Decimal("10.5")
                }
            }
        }
        
        canonical = to_canonical_bytes(data)
        expected = b'{"outer":{"a":1,"nested":{"decimal":"10.500000","list":[3,1,2]},"z":3}}'
        
        assert canonical == expected
    
    def test_list_preservation(self):
        """Test that list order is preserved (not sorted)."""
        data = {"items": [3, 1, 2]}
        canonical = to_canonical_bytes(data)
        
        assert canonical == b'{"items":[3,1,2]}'
    
    def test_hash_consistency(self):
        """Test that identical objects produce identical hashes."""
        data = {"test": "value", "number": 42}
        
        hash1 = compute_hash(data)
        hash2 = compute_hash(data)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # blake3 produces 256-bit hashes (64 hex chars)
    
    def test_hash_difference(self):
        """Test that different objects produce different hashes."""
        data1 = {"value": 1}
        data2 = {"value": 2}
        
        hash1 = compute_hash(data1)
        hash2 = compute_hash(data2)
        
        assert hash1 != hash2
    
    def test_sort_reasons(self):
        """Test reason sorting functionality."""
        reasons = ["third reason", "first reason", "second reason"]
        sorted_reasons = sort_reasons(reasons)
        
        expected = ["first reason", "second reason", "third reason"]
        assert sorted_reasons == expected
    
    def test_verify_canonical_format_valid(self):
        """Test canonical format verification with valid data."""
        data = {"b": 2, "a": 1}
        canonical_bytes = to_canonical_bytes(data)
        
        assert verify_canonical_format(canonical_bytes) == True
    
    def test_verify_canonical_format_invalid(self):
        """Test canonical format verification with invalid data."""
        # Non-canonical JSON (wrong key order)
        invalid_json = b'{"b":2,"a":1}'
        
        assert verify_canonical_format(invalid_json) == False
    
    def test_merkle_pair_hash(self):
        """Test Merkle tree pair hashing."""
        left = "abc123"
        right = "def456"
        
        pair_hash = compute_merkle_pair_hash(left, right)
        
        # Should be deterministic
        assert pair_hash == compute_merkle_pair_hash(left, right)
        
        # Should be different from individual hashes
        assert pair_hash != compute_hash(left)
        assert pair_hash != compute_hash(right)
    
    def test_unicode_handling(self):
        """Test Unicode string handling."""
        data = {"message": "Hello 世界 🌍"}
        canonical = to_canonical_bytes(data)
        
        # Should be valid UTF-8
        canonical_str = canonical.decode('utf-8')
        assert "Hello 世界 🌍" in canonical_str
    
    def test_boolean_values(self):
        """Test boolean value serialization."""
        data = {"true_val": True, "false_val": False}
        canonical = to_canonical_bytes(data)
        
        assert canonical == b'{"false_val":false,"true_val":true}'
    
    def test_scientific_notation_avoided(self):
        """Test that scientific notation is avoided for decimals."""
        # Large decimal that might trigger scientific notation
        data = {"large": Decimal("1234567890.123456")}
        canonical = to_canonical_bytes(data)
        
        canonical_str = canonical.decode('utf-8')
        assert 'e' not in canonical_str.lower()  # No scientific notation
        assert '1234567890.123456' in canonical_str