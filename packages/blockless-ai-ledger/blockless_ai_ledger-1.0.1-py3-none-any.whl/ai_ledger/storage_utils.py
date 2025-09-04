"""
Cross-platform storage utilities with file locking and log rotation.

Provides platform-independent file locking and log management.
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

# Cross-platform file locking
try:
    import portalocker
    HAS_PORTALOCKER = True
except ImportError:
    HAS_PORTALOCKER = False
    import fcntl if os.name == 'posix' else None

logger = logging.getLogger(__name__)


class CrossPlatformFileLock:
    """Cross-platform file locking utility."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.file_handle = None
        self.is_locked = False
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
    
    def acquire(self):
        """Acquire exclusive lock on file."""
        if self.is_locked:
            return
        
        self.file_handle = open(self.filepath, 'ab')
        
        if HAS_PORTALOCKER:
            # Use portalocker for cross-platform support
            portalocker.lock(self.file_handle, portalocker.LOCK_EX)
        elif os.name == 'posix' and fcntl:
            # Use fcntl on Unix-like systems
            fcntl.flock(self.file_handle.fileno(), fcntl.LOCK_EX)
        elif os.name == 'nt':
            # Windows file locking fallback
            try:
                import msvcrt
                while True:
                    try:
                        msvcrt.locking(self.file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except IOError:
                        time.sleep(0.01)
            except ImportError:
                logger.warning("No file locking available on Windows - proceeding without lock")
        else:
            logger.warning(f"File locking not supported on {os.name}")
        
        self.is_locked = True
    
    def release(self):
        """Release file lock."""
        if not self.is_locked or not self.file_handle:
            return
        
        try:
            if HAS_PORTALOCKER:
                portalocker.unlock(self.file_handle)
            elif os.name == 'posix' and fcntl:
                fcntl.flock(self.file_handle.fileno(), fcntl.LOCK_UN)
            elif os.name == 'nt':
                try:
                    import msvcrt
                    msvcrt.locking(self.file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                except ImportError:
                    pass
            
            self.file_handle.close()
        except Exception as e:
            logger.error(f"Error releasing file lock: {e}")
        finally:
            self.file_handle = None
            self.is_locked = False


class LogRotationManager:
    """Manages log file rotation and cleanup."""
    
    def __init__(self, log_dir: Path, max_file_size: int = 100 * 1024 * 1024):  # 100MB
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.max_backup_count = 10
    
    def should_rotate(self, filepath: Path) -> bool:
        """Check if log file should be rotated."""
        if not filepath.exists():
            return False
        
        try:
            file_size = filepath.stat().st_size
            return file_size >= self.max_file_size
        except Exception:
            return False
    
    def rotate_log(self, filepath: Path):
        """Rotate log file by renaming to .1, .2, etc."""
        try:
            # Shift existing backups
            for i in range(self.max_backup_count - 1, 0, -1):
                old_backup = filepath.with_suffix(f"{filepath.suffix}.{i}")
                new_backup = filepath.with_suffix(f"{filepath.suffix}.{i + 1}")
                
                if old_backup.exists():
                    if new_backup.exists():
                        new_backup.unlink()
                    old_backup.rename(new_backup)
            
            # Rename current log to .1
            if filepath.exists():
                backup = filepath.with_suffix(f"{filepath.suffix}.1")
                if backup.exists():
                    backup.unlink()
                filepath.rename(backup)
            
            logger.info(f"Rotated log file: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to rotate log {filepath}: {e}")
    
    def cleanup_old_logs(self, keep_days: int = 30):
        """Clean up log files older than specified days."""
        if not self.log_dir.exists():
            return
        
        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
        cleaned_count = 0
        
        try:
            for log_file in self.log_dir.glob("*.jsonl*"):
                try:
                    if log_file.stat().st_mtime < cutoff_time:
                        log_file.unlink()
                        cleaned_count += 1
                except Exception:
                    continue
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old log files")
                
        except Exception as e:
            logger.error(f"Error during log cleanup: {e}")
    
    def get_log_stats(self) -> dict:
        """Get statistics about log files."""
        if not self.log_dir.exists():
            return {"total_files": 0, "total_size": 0}
        
        total_files = 0
        total_size = 0
        
        try:
            for log_file in self.log_dir.glob("*.jsonl*"):
                try:
                    total_files += 1
                    total_size += log_file.stat().st_size
                except Exception:
                    continue
        except Exception:
            pass
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }


def ensure_directory(path: Path):
    """Ensure directory exists, create if it doesn't."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise


def safe_write_json_line(filepath: Path, data: dict, fsync: bool = False):
    """Safely write JSON line to file with atomic operation."""
    import json
    from . import canonical_json
    
    # Serialize with checksum
    line = json.dumps(data, separators=(',', ':'), sort_keys=True)
    checksum = canonical_json.compute_hash(line)
    full_line = f"{checksum}|{line}\n"
    
    # Write atomically using temporary file
    temp_file = filepath.with_suffix(filepath.suffix + '.tmp')
    
    try:
        with CrossPlatformFileLock(temp_file):
            with open(temp_file, 'ab') as f:
                f.write(full_line.encode('utf-8'))
                if fsync:
                    os.fsync(f.fileno())
        
        # Atomic rename
        if filepath.exists():
            # Append to existing file
            with open(filepath, 'ab') as dest:
                with open(temp_file, 'rb') as src:
                    dest.write(src.read())
            temp_file.unlink()
        else:
            # Rename temp file to final name
            temp_file.rename(filepath)
        
    except Exception as e:
        # Clean up temp file on failure
        if temp_file.exists():
            temp_file.unlink()
        raise e


def read_json_lines_safely(filepath: Path) -> list:
    """Safely read JSON lines with checksum verification."""
    import json
    from . import canonical_json
    
    if not filepath.exists():
        return []
    
    objects = []
    
    try:
        with CrossPlatformFileLock(filepath):
            with open(filepath, 'rb') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        line = line.decode('utf-8').strip()
                        if not line:
                            continue
                        
                        if '|' not in line:
                            logger.warning(f"Invalid format at {filepath}:{line_num}")
                            continue
                        
                        checksum, data = line.split('|', 1)
                        
                        # Verify checksum
                        computed = canonical_json.compute_hash(data)
                        if computed != checksum:
                            logger.error(f"Checksum mismatch at {filepath}:{line_num}")
                            continue
                        
                        objects.append(json.loads(data))
                        
                    except Exception as e:
                        logger.error(f"Failed to read {filepath}:{line_num}: {e}")
                        continue
    
    except Exception as e:
        logger.error(f"Failed to read file {filepath}: {e}")
    
    return objects


def get_disk_usage(path: Path) -> dict:
    """Get disk usage statistics for path."""
    try:
        if os.name == 'posix':
            statvfs = os.statvfs(path)
            total = statvfs.f_frsize * statvfs.f_blocks
            free = statvfs.f_frsize * statvfs.f_bavail
            used = total - free
        else:  # Windows
            import shutil
            total, used, free = shutil.disk_usage(path)
        
        return {
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "used_percent": round((used / total) * 100, 1) if total > 0 else 0,
            "free_percent": round((free / total) * 100, 1) if total > 0 else 0
        }
    except Exception as e:
        logger.error(f"Failed to get disk usage for {path}: {e}")
        return {
            "total_bytes": 0,
            "used_bytes": 0, 
            "free_bytes": 0,
            "used_percent": 0,
            "free_percent": 0
        }


def create_backup_with_timestamp(filepath: Path, backup_dir: Optional[Path] = None) -> Path:
    """Create timestamped backup of file."""
    if backup_dir is None:
        backup_dir = filepath.parent / "backups"
    
    ensure_directory(backup_dir)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
    backup_path = backup_dir / backup_name
    
    try:
        import shutil
        shutil.copy2(filepath, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup of {filepath}: {e}")
        raise