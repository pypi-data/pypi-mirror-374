"""
Canonical JSON serialization for deterministic hashing.

Ensures that identical data structures always produce identical hashes,
regardless of key ordering or other variations.
"""

import json
from decimal import Decimal
from typing import Any
import blake3


def to_canonical_bytes(obj: Any) -> bytes:
    """
    Convert any object to canonical JSON bytes.
    
    Canonicalization rules:
    - Keys sorted lexicographically
    - No whitespace, UTF-8 encoding
    - Decimals/floats formatted as strings with fixed precision
    - Lists sorted where order is not semantic (e.g., reasons)
    - No nulls - omit absent fields
    - Recursive canonicalization
    
    Args:
        obj: Any JSON-serializable object
        
    Returns:
        Canonical JSON bytes
    """
    def canonicalize(o):
        if isinstance(o, dict):
            # Sort keys and omit null values
            return {k: canonicalize(v) for k, v in sorted(o.items()) if v is not None}
        elif isinstance(o, list):
            return [canonicalize(item) for item in o]
        elif isinstance(o, Decimal):
            # Format with fixed precision, no scientific notation
            return str(o.quantize(Decimal('0.000001')))
        elif isinstance(o, float):
            # Format floats consistently
            return f"{o:.6f}"
        elif isinstance(o, bool):
            return o
        elif o is None:
            return None
        else:
            return str(o)
    
    canonical = canonicalize(obj)
    return json.dumps(canonical, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def compute_hash(obj: Any) -> str:
    """
    Compute blake3 hash of canonical JSON representation.
    
    Args:
        obj: Any JSON-serializable object
        
    Returns:
        Hex-encoded blake3 hash
    """
    return blake3.blake3(to_canonical_bytes(obj)).hexdigest()


def sort_reasons(reasons: list[str]) -> list[str]:
    """
    Sort reasons list for consistent hashing.
    
    Args:
        reasons: List of reason strings
        
    Returns:
        Sorted list of reasons
    """
    return sorted(reasons)


def verify_canonical_format(data: bytes) -> bool:
    """
    Verify that data is in canonical JSON format.
    
    Args:
        data: JSON bytes to verify
        
    Returns:
        True if canonical, False otherwise
    """
    try:
        # Parse the JSON
        obj = json.loads(data.decode('utf-8'))
        
        # Re-canonicalize and compare
        canonical = to_canonical_bytes(obj)
        
        return data == canonical
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False


def compute_merkle_pair_hash(left: str, right: str) -> str:
    """
    Compute hash of a Merkle tree pair.
    
    Args:
        left: Left hash (hex string)
        right: Right hash (hex string)
        
    Returns:
        Combined hash (hex string)
    """
    combined = left + right
    return compute_hash(combined)