"""
Cryptographic operations for the AI Ledger system.

Provides Ed25519 signatures with domain separation to prevent cross-protocol attacks.
"""

import nacl.signing
import nacl.encoding
from typing import Tuple
import os

from . import canonical_json
from . import params


def generate_keypair() -> Tuple[bytes, bytes]:
    """
    Generate Ed25519 keypair.
    
    Returns:
        Tuple of (private_key_bytes, public_key_bytes)
    """
    signing_key = nacl.signing.SigningKey.generate()
    return bytes(signing_key), bytes(signing_key.verify_key)


def sign_message(message_dict: dict, privkey: bytes) -> str:
    """
    Sign a message with domain separation.
    
    Adds version and domain to prevent cross-protocol attacks.
    
    Args:
        message_dict: Dictionary to sign
        privkey: Private key bytes
        
    Returns:
        Hex-encoded signature
    """
    # Add domain separation
    signed_payload = {
        "v": params.SIGNATURE_VERSION,
        "domain": params.REQUIRE_SIGNATURE_DOMAIN,
        **message_dict
    }
    
    message_bytes = canonical_json.to_canonical_bytes(signed_payload)
    signing_key = nacl.signing.SigningKey(privkey)
    signed = signing_key.sign(message_bytes)
    return signed.signature.hex()


def verify_signature(sig_hex: str, message_dict: dict, pubkey: bytes) -> bool:
    """
    Verify signature with domain checking.
    
    Args:
        sig_hex: Hex-encoded signature
        message_dict: Original message dictionary
        pubkey: Public key bytes
        
    Returns:
        True if signature is valid
    """
    try:
        signed_payload = {
            "v": params.SIGNATURE_VERSION,
            "domain": params.REQUIRE_SIGNATURE_DOMAIN,
            **message_dict
        }
        
        message_bytes = canonical_json.to_canonical_bytes(signed_payload)
        verify_key = nacl.signing.VerifyKey(pubkey)
        verify_key.verify(message_bytes, bytes.fromhex(sig_hex))
        return True
    except Exception:
        return False


def create_opinion_signature(
    tx_id: str, 
    validator_id: str, 
    valid: bool,
    risk_score: float, 
    reasons: list[str], 
    privkey: bytes, 
    params_hash: str
) -> str:
    """
    Create signature for validator opinion.
    
    Args:
        tx_id: Transaction ID being validated
        validator_id: ID of the validator
        valid: Whether transaction is valid
        risk_score: Risk score (0.0 to 1.0)
        reasons: List of validation reasons
        privkey: Validator's private key
        params_hash: Hash of consensus parameters
        
    Returns:
        Hex-encoded signature
    """
    message = {
        "kind": "opinion",
        "tx_id": tx_id,
        "validator_id": validator_id,
        "valid": valid,
        "risk_score": f"{risk_score:.6f}",
        "reasons_hash": canonical_json.compute_hash(canonical_json.sort_reasons(reasons)),
        "params_hash": params_hash
    }
    return sign_message(message, privkey)


def create_receipt_signature(
    tx_id: str, 
    quorum_outcome: dict, 
    validator_sigs: list[str], 
    privkey: bytes,
    params_hash: str
) -> str:
    """
    Create signature for receipt.
    
    Args:
        tx_id: Transaction ID
        quorum_outcome: Quorum decision outcome
        validator_sigs: List of validator signatures
        privkey: Receipt signer's private key  
        params_hash: Hash of consensus parameters
        
    Returns:
        Hex-encoded signature
    """
    message = {
        "kind": "receipt",
        "tx_id": tx_id,
        "receipt_id": "",  # Will be filled with actual receipt hash
        "quorum": quorum_outcome,
        "validator_sigs_hash": canonical_json.compute_hash(sorted(validator_sigs)),
        "params_hash": params_hash
    }
    return sign_message(message, privkey)


def pubkey_to_hex(pubkey: bytes) -> str:
    """
    Convert public key bytes to hex string.
    
    Args:
        pubkey: Public key bytes
        
    Returns:
        Hex-encoded public key
    """
    return pubkey.hex()


def hex_to_pubkey(hex_str: str) -> bytes:
    """
    Convert hex string to public key bytes.
    
    Args:
        hex_str: Hex-encoded public key
        
    Returns:
        Public key bytes
    """
    return bytes.fromhex(hex_str)


def generate_secure_nonce() -> int:
    """
    Generate a cryptographically secure nonce.
    
    Returns:
        Random 64-bit integer
    """
    return int.from_bytes(os.urandom(8), byteorder='big')


def create_validator_id(pubkey: bytes) -> str:
    """
    Create a validator ID from public key.
    
    Args:
        pubkey: Public key bytes
        
    Returns:
        Validator ID (first 16 hex chars of pubkey hash)
    """
    pubkey_hash = canonical_json.compute_hash(pubkey.hex())
    return pubkey_hash[:16]


def verify_opinion_signature(
    sig_hex: str,
    tx_id: str,
    validator_id: str,
    valid: bool,
    risk_score: float,
    reasons: list[str],
    pubkey: bytes,
    params_hash: str
) -> bool:
    """
    Verify a validator opinion signature.
    
    Args:
        sig_hex: Signature to verify
        tx_id: Transaction ID
        validator_id: Validator ID
        valid: Validity decision
        risk_score: Risk score
        reasons: List of reasons
        pubkey: Validator's public key
        params_hash: Parameters hash
        
    Returns:
        True if signature is valid
    """
    message = {
        "kind": "opinion",
        "tx_id": tx_id,
        "validator_id": validator_id,
        "valid": valid,
        "risk_score": f"{risk_score:.6f}",
        "reasons_hash": canonical_json.compute_hash(canonical_json.sort_reasons(reasons)),
        "params_hash": params_hash
    }
    return verify_signature(sig_hex, message, pubkey)