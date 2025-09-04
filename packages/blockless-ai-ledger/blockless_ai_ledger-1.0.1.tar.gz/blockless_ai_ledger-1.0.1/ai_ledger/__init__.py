"""
Blockless AI Ledger - Distributed AI-validated ledger system

A revolutionary blockchain replacement that uses AI validators for consensus
instead of traditional mining or staking.
"""

__version__ = "1.0.1"
__author__ = "Nethara Labs"
__email__ = "contact@netharalabs.com"

# Package metadata
name = "blockless-ai-ledger"
description = "Distributed AI-validated ledger system - Blockless blockchain with AI consensus"

from .params import *
from .canonical_json import compute_hash, to_canonical_bytes
from .transaction import Transaction
from .account import Account, AccountManager
from .validator import Validator, ValidatorOpinion
from .quorum import QuorumOutcome, QuorumManager
from .storage import Storage, StorageError

__all__ = [
    "Transaction",
    "Account", 
    "AccountManager",
    "Validator",
    "ValidatorOpinion",
    "QuorumOutcome",
    "QuorumManager", 
    "Storage",
    "StorageError",
    "compute_hash",
    "to_canonical_bytes",
    "SCHEMA_VERSION",
    "N_VALIDATORS",
    "QUORUM_K",
    "DEFAULT_ASSET"
]