"""
Verification utilities for AI Ledger system.

Provides tools to verify receipts, account chains, and system integrity.
"""

import json
import typer
from pathlib import Path
from typing import List, Dict, Optional
from colorama import init, Fore

from . import params
from .storage import Storage
from .quorum import Receipt, MerkleTree
from .account import AccountManager

init(autoreset=True)

app = typer.Typer()


class VerificationResult:
    """Result of a verification operation."""
    
    def __init__(self, valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def summary(self) -> str:
        if self.valid:
            status = f"{Fore.GREEN}VALID"
        else:
            status = f"{Fore.RED}INVALID"
        
        summary = f"{status} - {len(self.errors)} errors, {len(self.warnings)} warnings"
        return summary


def verify_receipt(receipt: Receipt) -> VerificationResult:
    """Verify a single receipt's integrity."""
    result = VerificationResult(True)
    
    # Verify receipt ID
    expected_id = receipt.compute_receipt_id()
    if receipt.receipt_id != expected_id:
        result.add_error(f"Receipt ID mismatch: {receipt.receipt_id} != {expected_id}")
    
    # Verify Merkle root
    if receipt.account_heads:
        sorted_items = sorted(receipt.account_heads.items())
        head_ids = [head_id for _, head_id in sorted_items]
        expected_root = MerkleTree.compute_root(head_ids)
        if receipt.merkle_root != expected_root:
            result.add_error(f"Merkle root mismatch: {receipt.merkle_root} != {expected_root}")
    
    # Verify quorum logic
    opinions = receipt.validator_opinions
    valid_count = sum(1 for op in opinions if op.valid)
    
    if receipt.quorum_outcome.valid_count != valid_count:
        result.add_error(f"Valid count mismatch: {receipt.quorum_outcome.valid_count} != {valid_count}")
    
    # Verify risk calculation
    if opinions:
        risk_scores = [op.risk_score for op in opinions]
        avg_risk = sum(risk_scores) / len(risk_scores)
        expected_risk = f"{avg_risk:.6f}"
        if receipt.quorum_outcome.risk_avg != expected_risk:
            result.add_error(f"Risk average mismatch: {receipt.quorum_outcome.risk_avg} != {expected_risk}")
    
    # Verify approval logic
    expected_approval = (
        valid_count >= params.QUORUM_K and
        float(receipt.quorum_outcome.risk_avg) <= params.MAX_RISK_AVG
    )
    if receipt.quorum_outcome.approved != expected_approval:
        result.add_error(f"Approval logic mismatch: {receipt.quorum_outcome.approved} != {expected_approval}")
    
    # Check for sufficient validator opinions
    if len(opinions) < params.MIN_DISTINCT_VALIDATORS:
        result.add_warning(f"Only {len(opinions)} validator opinions, need {params.MIN_DISTINCT_VALIDATORS}")
    
    return result


def verify_account_chain(storage: Storage, account_id: str) -> VerificationResult:
    """Verify the integrity of an account's transaction chain."""
    result = VerificationResult(True)
    
    # Get all receipts involving this account
    receipts = storage.get_recent_receipts(account_id, limit=1000)
    
    if not receipts:
        result.add_warning(f"No receipts found for account {account_id}")
        return result
    
    # Sort by finalization time
    receipts.sort(key=lambda r: r.finalized_at)
    
    # Verify each receipt
    for i, receipt in enumerate(receipts):
        receipt_result = verify_receipt(receipt)
        if not receipt_result.valid:
            result.add_error(f"Receipt {i+1} ({receipt.receipt_id[:8]}...): {receipt_result.errors[0]}")
    
    # Verify chain consistency
    prev_receipt_id = None
    for receipt in receipts:
        # In a full implementation, you'd verify the chain of prev_receipt_id_hint
        # For now, just check that account heads are consistent
        if account_id in receipt.account_heads:
            current_head = receipt.account_heads[account_id]
            if prev_receipt_id and current_head != receipt.receipt_id:
                result.add_warning(f"Account head inconsistency in receipt {receipt.receipt_id[:8]}...")
            prev_receipt_id = receipt.receipt_id
    
    return result


@app.command()
def receipt(
    receipt_id: str = typer.Argument(help="Receipt ID to verify"),
    log_dir: str = typer.Option("logs", "--log-dir", "-l", help="Log directory")
):
    """Verify a specific receipt's integrity."""
    
    try:
        storage = Storage(Path(log_dir))
        
        # Find receipt by ID
        # This is inefficient but works for demo
        receipts = storage._read_lines(storage.receipt_log)
        
        target_receipt = None
        for receipt_dict in receipts:
            if receipt_dict.get("receipt_id", "").startswith(receipt_id):
                receipt_dict.pop("stored_at", None)
                target_receipt = Receipt(**receipt_dict)
                break
        
        if not target_receipt:
            print(f"{Fore.RED}Receipt not found: {receipt_id}")
            raise typer.Exit(1)
        
        print(f"{Fore.CYAN}Verifying receipt: {target_receipt.receipt_id[:16]}...")
        
        result = verify_receipt(target_receipt)
        print(f"\n{result.summary()}")
        
        if result.errors:
            print(f"\n{Fore.RED}Errors:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print(f"\n{Fore.YELLOW}Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.valid:
            print(f"\n{Fore.GREEN}✓ Receipt is valid")
            
            # Show receipt details
            print(f"\nReceipt Details:")
            print(f"  Transaction: {target_receipt.tx_id}")
            print(f"  Approved: {target_receipt.quorum_outcome.approved}")
            print(f"  Validators: {target_receipt.quorum_outcome.valid_count}/{target_receipt.quorum_outcome.total_count}")
            print(f"  Risk Score: {target_receipt.quorum_outcome.risk_avg}")
            print(f"  Finalized: {target_receipt.finalized_at}")
        
    except Exception as e:
        print(f"{Fore.RED}Verification failed: {e}")
        raise typer.Exit(1)


@app.command()
def account(
    account_id: str = typer.Argument(help="Account ID to verify"),
    log_dir: str = typer.Option("logs", "--log-dir", "-l", help="Log directory")
):
    """Verify an account's transaction chain integrity."""
    
    try:
        storage = Storage(Path(log_dir))
        
        print(f"{Fore.CYAN}Verifying account chain: {account_id}")
        
        result = verify_account_chain(storage, account_id)
        print(f"\n{result.summary()}")
        
        if result.errors:
            print(f"\n{Fore.RED}Errors:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print(f"\n{Fore.YELLOW}Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.valid:
            print(f"\n{Fore.GREEN}✓ Account chain is valid")
    
    except Exception as e:
        print(f"{Fore.RED}Verification failed: {e}")
        raise typer.Exit(1)


@app.command()
def storage_integrity(
    log_dir: str = typer.Option("logs", "--log-dir", "-l", help="Log directory")
):
    """Verify complete storage integrity."""
    
    try:
        storage = Storage(Path(log_dir))
        
        print(f"{Fore.CYAN}Verifying storage integrity...")
        
        # Run built-in integrity check
        integrity_result = storage.verify_storage_integrity()
        
        if integrity_result["overall_valid"]:
            print(f"\n{Fore.GREEN}✓ Storage integrity verified")
        else:
            print(f"\n{Fore.RED}✗ Storage integrity issues found")
        
        # Show check details
        checks = integrity_result.get("checks", {})
        for check_name, check_result in checks.items():
            if check_result.get("valid", False):
                print(f"  {Fore.GREEN}✓ {check_name.replace('_', ' ').title()}")
                if "count" in check_result:
                    print(f"    Records: {check_result['count']}")
            else:
                print(f"  {Fore.RED}✗ {check_name.replace('_', ' ').title()}")
                if "error" in check_result:
                    print(f"    Error: {check_result['error']}")
        
        # Show any overall errors
        errors = integrity_result.get("errors", [])
        if errors:
            print(f"\n{Fore.RED}Overall Errors:")
            for error in errors:
                print(f"  - {error}")
        
        # Show storage stats
        stats = storage.get_storage_stats()
        print(f"\n{Fore.CYAN}Storage Statistics:")
        for file_type, file_info in stats.get("files", {}).items():
            if file_info.get("exists", False):
                size_kb = file_info["size_bytes"] / 1024
                count = file_info.get("record_count", "unknown")
                print(f"  {file_type.title()}: {count} records, {size_kb:.1f} KB")
            else:
                print(f"  {file_type.title()}: not found")
    
    except Exception as e:
        print(f"{Fore.RED}Verification failed: {e}")
        raise typer.Exit(1)


@app.command()
def all_receipts(
    log_dir: str = typer.Option("logs", "--log-dir", "-l", help="Log directory"),
    limit: int = typer.Option(100, "--limit", "-n", help="Maximum receipts to check")
):
    """Verify all receipts in storage."""
    
    try:
        storage = Storage(Path(log_dir))
        
        print(f"{Fore.CYAN}Verifying all receipts (limit: {limit})...")
        
        # Load receipts
        receipt_dicts = storage._read_lines(storage.receipt_log)
        receipt_dicts = receipt_dicts[-limit:]  # Take most recent
        
        if not receipt_dicts:
            print(f"{Fore.YELLOW}No receipts found")
            return
        
        print(f"Found {len(receipt_dicts)} receipts to verify")
        
        valid_count = 0
        error_count = 0
        warning_count = 0
        
        for i, receipt_dict in enumerate(receipt_dicts, 1):
            receipt_dict.pop("stored_at", None)
            receipt = Receipt(**receipt_dict)
            
            result = verify_receipt(receipt)
            
            if result.valid:
                valid_count += 1
                print(f"  {Fore.GREEN}✓ Receipt {i}: {receipt.receipt_id[:8]}...")
            else:
                error_count += 1
                print(f"  {Fore.RED}✗ Receipt {i}: {receipt.receipt_id[:8]}... - {result.errors[0]}")
            
            warning_count += len(result.warnings)
        
        print(f"\n{Fore.CYAN}Verification Summary:")
        print(f"  {Fore.GREEN}Valid: {valid_count}")
        print(f"  {Fore.RED}Invalid: {error_count}")
        print(f"  {Fore.YELLOW}Warnings: {warning_count}")
        
        if error_count == 0:
            print(f"\n{Fore.GREEN}✓ All receipts are valid!")
        else:
            print(f"\n{Fore.RED}✗ {error_count} receipts have integrity issues")
    
    except Exception as e:
        print(f"{Fore.RED}Verification failed: {e}")
        raise typer.Exit(1)


def main():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()