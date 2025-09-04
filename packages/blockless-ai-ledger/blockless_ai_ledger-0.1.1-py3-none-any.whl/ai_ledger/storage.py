"""
Durable storage with checksums and atomic operations.

Provides append-only logs with per-line integrity checking,
fsync for durability, and state reconstruction capabilities.
"""

import os
import json
import fcntl
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from . import canonical_json
from . import params
from .transaction import Transaction
from .quorum import Receipt
from .account import AccountManager, Account

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Exception raised for storage-related errors."""
    pass


class Storage:
    """
    Append-only storage with integrity checking and durability guarantees.
    
    Features:
    - Per-line checksums for corruption detection
    - File locking for concurrent access
    - Optional fsync for durability
    - Atomic operations where possible
    """
    
    def __init__(self, log_dir: Path):
        """
        Initialize storage system.
        
        Args:
            log_dir: Directory for storage files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage files
        self.tx_log = self.log_dir / "transactions.jsonl"
        self.receipt_log = self.log_dir / "receipts.jsonl"
        self.state_backup = self.log_dir / "state_backup.json"
        
        # File locks for thread safety
        self._locks = {}
        
        logger.info(f"Storage initialized in {self.log_dir}")
    
    def _get_lock(self, filepath: Path) -> fcntl:
        """Get or create lock for file."""
        if filepath not in self._locks:
            self._locks[filepath] = None
        return self._locks[filepath]
    
    def _write_line(
        self, 
        filepath: Path, 
        obj: dict, 
        fsync: bool = False
    ):
        """
        Write single line with checksum and optional fsync.
        
        Format: checksum|json_data\n
        
        Args:
            filepath: File to write to
            obj: Object to serialize
            fsync: Whether to fsync after write
        """
        # Serialize object to canonical JSON
        line = json.dumps(obj, separators=(',', ':'), sort_keys=True)
        
        # Compute checksum of the JSON line
        checksum = canonical_json.compute_hash(line)
        
        # Format: checksum|data\n
        full_line = f"{checksum}|{line}\n"
        
        # Write with file locking
        with open(filepath, 'ab') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(full_line.encode('utf-8'))
                if fsync:
                    os.fsync(f.fileno())  # Force write to disk
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        logger.debug(f"Wrote line to {filepath}: {len(line)} bytes")
    
    def _read_lines(self, filepath: Path) -> List[dict]:
        """
        Read and verify all lines from log file.
        
        Args:
            filepath: File to read from
            
        Returns:
            List of deserialized objects
            
        Raises:
            StorageError: If file is corrupted or unreadable
        """
        if not filepath.exists():
            return []
        
        objects = []
        
        with open(filepath, 'rb') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
            try:
                for line_num, line in enumerate(f, 1):
                    try:
                        line = line.decode('utf-8').strip()
                        if not line:
                            continue
                        
                        # Parse checksum|data format
                        if '|' not in line:
                            raise ValueError(f"Invalid format at line {line_num}: missing separator")
                        
                        checksum, data = line.split('|', 1)
                        
                        # Verify checksum
                        computed = canonical_json.compute_hash(data)
                        if computed != checksum:
                            raise ValueError(f"Checksum mismatch at line {line_num}")
                        
                        # Parse JSON
                        objects.append(json.loads(data))
                        
                    except Exception as e:
                        error_msg = f"Failed to read {filepath} at line {line_num}: {e}"
                        logger.error(error_msg)
                        raise StorageError(error_msg)
            
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        logger.debug(f"Read {len(objects)} objects from {filepath}")
        return objects
    
    def append_transaction(self, tx: Transaction):
        """
        Append transaction to log.
        
        Args:
            tx: Transaction to append
        """
        tx_dict = tx.dict()
        tx_dict['stored_at'] = datetime.now(timezone.utc).isoformat()
        
        self._write_line(self.tx_log, tx_dict, fsync=False)
        logger.debug(f"Stored transaction {tx.id}")
    
    def append_receipt(self, receipt: Receipt):
        """
        Append receipt with fsync for durability.
        
        Args:
            receipt: Receipt to append
        """
        receipt_dict = receipt.dict()
        receipt_dict['stored_at'] = datetime.now(timezone.utc).isoformat()
        
        # Receipts are critical - always fsync
        self._write_line(self.receipt_log, receipt_dict, fsync=params.FSYNC_RECEIPTS)
        logger.info(f"Stored receipt {receipt.receipt_id} for tx {receipt.tx_id}")
    
    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """
        Get transaction by ID.
        
        Args:
            tx_id: Transaction ID to find
            
        Returns:
            Transaction if found, None otherwise
        """
        transactions = self._read_lines(self.tx_log)
        
        for tx_dict in transactions:
            if tx_dict.get('id') == tx_id:
                # Remove storage metadata before creating Transaction
                tx_dict.pop('stored_at', None)
                return Transaction(**tx_dict)
        
        return None
    
    def get_receipt(self, tx_id: str) -> Optional[Receipt]:
        """
        Get receipt by transaction ID.
        
        Args:
            tx_id: Transaction ID to find receipt for
            
        Returns:
            Receipt if found, None otherwise
        """
        receipts = self._read_lines(self.receipt_log)
        
        for receipt_dict in receipts:
            if receipt_dict.get('tx_id') == tx_id:
                # Remove storage metadata before creating Receipt
                receipt_dict.pop('stored_at', None)
                return Receipt(**receipt_dict)
        
        return None
    
    def get_recent_receipts(
        self, 
        account_id: Optional[str] = None, 
        limit: int = 10
    ) -> List[Receipt]:
        """
        Get recent receipts, optionally filtered by account.
        
        Args:
            account_id: Account to filter by (None for all)
            limit: Maximum number of receipts to return
            
        Returns:
            List of recent receipts
        """
        receipts = self._read_lines(self.receipt_log)
        
        # Filter by account if specified
        if account_id:
            # This is simplified - in a real system you'd have indexed lookups
            filtered_receipts = []
            for receipt_dict in receipts:
                account_heads = receipt_dict.get('account_heads', {})
                if account_id in account_heads:
                    receipt_dict.pop('stored_at', None)
                    filtered_receipts.append(Receipt(**receipt_dict))
            receipts = filtered_receipts
        else:
            receipts = [Receipt(**{k: v for k, v in r.items() if k != 'stored_at'}) 
                       for r in receipts]
        
        # Return most recent first
        receipts.sort(key=lambda r: r.finalized_at, reverse=True)
        return receipts[:limit]
    
    def rebuild_state(self) -> AccountManager:
        """
        Rebuild account state from receipts only.
        
        This is the source of truth - only finalized receipts affect state.
        
        Returns:
            Reconstructed AccountManager
        """
        logger.info("Rebuilding state from receipts...")
        
        manager = AccountManager()
        receipts = self._read_lines(self.receipt_log)
        
        applied_count = 0
        
        for receipt_dict in receipts:
            try:
                receipt_dict.pop('stored_at', None)
                receipt = Receipt(**receipt_dict)
                
                # Only apply approved receipts
                if receipt.quorum_outcome.approved:
                    # Find corresponding transaction
                    tx = self.get_transaction(receipt.tx_id)
                    if tx:
                        success = manager.apply_transaction(tx, receipt.receipt_id)
                        if success:
                            applied_count += 1
                        else:
                            logger.warning(f"Failed to apply transaction {receipt.tx_id}")
                    else:
                        logger.warning(f"Transaction {receipt.tx_id} not found for approved receipt")
                        
            except Exception as e:
                logger.error(f"Error processing receipt: {e}")
                continue
        
        logger.info(f"Rebuilt state with {applied_count} applied receipts")
        return manager
    
    def get_pending_transactions(self) -> List[Transaction]:
        """
        Load transactions for mempool initialization.
        
        Returns:
            List of all stored transactions
        """
        transactions = []
        tx_dicts = self._read_lines(self.tx_log)
        
        for tx_dict in tx_dicts:
            try:
                tx_dict.pop('stored_at', None)
                transactions.append(Transaction(**tx_dict))
            except Exception as e:
                logger.error(f"Error loading transaction: {e}")
                continue
        
        logger.info(f"Loaded {len(transactions)} transactions from storage")
        return transactions
    
    def create_state_backup(self, account_manager: AccountManager):
        """
        Create backup of current account state.
        
        Args:
            account_manager: Current account state to backup
        """
        backup_data = {
            "backup_timestamp": datetime.now(timezone.utc).isoformat(),
            "schema_version": params.SCHEMA_VERSION,
            "accounts": {
                acc_id: acc.to_dict() 
                for acc_id, acc in account_manager.accounts.items()
            },
            "total_accounts": len(account_manager.accounts),
            "integrity_check": account_manager.verify_integrity()
        }
        
        # Write backup atomically
        temp_backup = self.state_backup.with_suffix('.tmp')
        try:
            with open(temp_backup, 'w') as f:
                json.dump(backup_data, f, indent=2, sort_keys=True)
                os.fsync(f.fileno())
            
            # Atomic rename
            temp_backup.rename(self.state_backup)
            logger.info(f"Created state backup with {len(account_manager.accounts)} accounts")
            
        except Exception as e:
            logger.error(f"Failed to create state backup: {e}")
            if temp_backup.exists():
                temp_backup.unlink()
            raise StorageError(f"Backup creation failed: {e}")
    
    def verify_storage_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of all storage files.
        
        Returns:
            Dictionary with integrity check results
        """
        results = {
            "overall_valid": True,
            "checks": {},
            "errors": []
        }
        
        # Check transaction log
        try:
            tx_count = len(self._read_lines(self.tx_log))
            results["checks"]["transactions"] = {
                "valid": True,
                "count": tx_count,
                "file_size": self.tx_log.stat().st_size if self.tx_log.exists() else 0
            }
        except Exception as e:
            results["overall_valid"] = False
            results["errors"].append(f"Transaction log error: {e}")
            results["checks"]["transactions"] = {"valid": False, "error": str(e)}
        
        # Check receipt log
        try:
            receipt_count = len(self._read_lines(self.receipt_log))
            results["checks"]["receipts"] = {
                "valid": True,
                "count": receipt_count,
                "file_size": self.receipt_log.stat().st_size if self.receipt_log.exists() else 0
            }
        except Exception as e:
            results["overall_valid"] = False
            results["errors"].append(f"Receipt log error: {e}")
            results["checks"]["receipts"] = {"valid": False, "error": str(e)}
        
        # Check state consistency
        try:
            manager = self.rebuild_state()
            is_valid, errors = manager.verify_integrity()
            
            results["checks"]["state_integrity"] = {
                "valid": is_valid,
                "errors": errors,
                "account_count": len(manager.accounts)
            }
            
            if not is_valid:
                results["overall_valid"] = False
                results["errors"].extend(errors)
                
        except Exception as e:
            results["overall_valid"] = False
            results["errors"].append(f"State rebuild error: {e}")
            results["checks"]["state_integrity"] = {"valid": False, "error": str(e)}
        
        return results
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            "log_directory": str(self.log_dir),
            "files": {}
        }
        
        # Transaction log stats
        if self.tx_log.exists():
            tx_count = len(self._read_lines(self.tx_log))
            stats["files"]["transactions"] = {
                "exists": True,
                "size_bytes": self.tx_log.stat().st_size,
                "record_count": tx_count,
                "last_modified": self.tx_log.stat().st_mtime
            }
        else:
            stats["files"]["transactions"] = {"exists": False}
        
        # Receipt log stats
        if self.receipt_log.exists():
            receipt_count = len(self._read_lines(self.receipt_log))
            stats["files"]["receipts"] = {
                "exists": True,
                "size_bytes": self.receipt_log.stat().st_size,
                "record_count": receipt_count,
                "last_modified": self.receipt_log.stat().st_mtime
            }
        else:
            stats["files"]["receipts"] = {"exists": False}
        
        # State backup stats
        if self.state_backup.exists():
            stats["files"]["state_backup"] = {
                "exists": True,
                "size_bytes": self.state_backup.stat().st_size,
                "last_modified": self.state_backup.stat().st_mtime
            }
        else:
            stats["files"]["state_backup"] = {"exists": False}
        
        return stats
    
    def cleanup_old_data(self, keep_days: int = 30):
        """
        Cleanup old data (placeholder for production systems).
        
        Args:
            keep_days: Days of data to keep
        """
        # In production, you'd implement log rotation, archival, etc.
        # For now, just log the request
        logger.info(f"Cleanup requested for data older than {keep_days} days")
        # TODO: Implement actual cleanup logic