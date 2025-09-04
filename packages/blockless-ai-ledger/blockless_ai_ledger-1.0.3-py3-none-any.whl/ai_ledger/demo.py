"""
Interactive demonstration with beautiful colored output.

Shows the complete AI ledger workflow with multiple test scenarios,
validator opinions, and final state verification.
"""

import asyncio
import random
import time
import json
import httpx
from pathlib import Path
from typing import List, Dict, Optional

import typer
from colorama import init, Fore, Style

from . import params
from . import crypto
from .transaction import Transaction, SubmitRequest
from .account import AccountManager
from .validator import Validator
from .storage import Storage
from .node import initialize_node, app
import uvicorn
import threading

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Color assignments for validators  
VALIDATOR_COLORS = [
    Fore.RED, Fore.GREEN, Fore.YELLOW, 
    Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE
]

app_cli = typer.Typer()


class DemoClient:
    """HTTP client for interacting with AI Ledger nodes."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def submit_transaction(
        self,
        description: str,
        from_acct: str,
        to_acct: str,
        amount: str,
        asset: str = params.DEFAULT_ASSET
    ) -> Dict:
        """Submit transaction to node."""
        # Get current nonce
        account_resp = await self.client.get(f"{self.base_url}/account/{from_acct}")
        nonce = account_resp.json()["nonce"] + 1
        
        # Submit transaction
        req = SubmitRequest(
            nl_description=description,
            from_acct=from_acct,
            to_acct=to_acct,
            asset=asset,
            amount=amount,
            nonce=nonce
        )
        
        resp = await self.client.post(
            f"{self.base_url}/submit",
            json=req.dict()
        )
        resp.raise_for_status()
        return resp.json()
    
    async def get_receipt(self, tx_id: str) -> Optional[Dict]:
        """Get receipt for transaction."""
        try:
            resp = await self.client.get(f"{self.base_url}/receipt/{tx_id}")
            if resp.status_code == 200:
                return resp.json()
            return None
        except httpx.HTTPStatusError:
            return None
    
    async def get_account(self, account_id: str) -> Dict:
        """Get account information."""
        resp = await self.client.get(f"{self.base_url}/account/{account_id}")
        resp.raise_for_status()
        return resp.json()
    
    async def get_health(self) -> Dict:
        """Get node health status."""
        resp = await self.client.get(f"{self.base_url}/health")
        return resp.json()
    
    async def wait_for_finality(self, tx_id: str, timeout: float = 10.0) -> Optional[Dict]:
        """Wait for transaction to be finalized."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            receipt = await self.get_receipt(tx_id)
            if receipt and receipt.get("receipt_id"):
                return receipt
            await asyncio.sleep(0.5)
        
        return None


async def create_genesis_accounts() -> Dict[str, Dict[str, str]]:
    """Create genesis accounts with initial balances."""
    return {
        "alice": {params.DEFAULT_ASSET: "100.0"},
        "bob": {params.DEFAULT_ASSET: "0.0"},
        "treasury": {params.DEFAULT_ASSET: "900.0"}
    }


async def start_demo_node(port: int = 8001) -> str:
    """Start a demo node in background."""
    # Create temporary log directory
    log_dir = Path("demo_logs")
    log_dir.mkdir(exist_ok=True)
    
    # Initialize storage with genesis accounts
    storage = Storage(log_dir)
    account_manager = AccountManager()
    
    # Create genesis accounts
    genesis_balances = await create_genesis_accounts()
    genesis_data = account_manager.create_genesis_accounts(genesis_balances)
    
    print(f"  {Fore.GREEN}Genesis created: {genesis_data['genesis_hash'][:16]}...")
    
    # Start node in background thread
    def run_node():
        uvicorn.run(
            "ai_ledger.node:app",
            host="127.0.0.1",
            port=port,
            log_level="warning"  # Reduce noise
        )
    
    thread = threading.Thread(target=run_node, daemon=True)
    thread.start()
    
    # Wait for node to be ready
    client = DemoClient(f"http://127.0.0.1:{port}")
    
    for i in range(30):  # Wait up to 30 seconds
        try:
            await client.get_health()
            break
        except:
            await asyncio.sleep(1)
    else:
        raise RuntimeError("Node failed to start")
    
    return f"http://127.0.0.1:{port}"


async def submit_and_display_transaction(
    client: DemoClient,
    description: str,
    from_acct: str,
    to_acct: str,
    amount: str,
    should_succeed: bool = True
) -> Optional[str]:
    """Submit transaction and display the validation process."""
    
    print(f"\n{Fore.WHITE}  📤 Submitting: {description}")
    print(f"    {from_acct} → {to_acct}: {amount} {params.DEFAULT_ASSET}")
    
    start_time = time.time()
    
    try:
        # Submit transaction
        result = await client.submit_transaction(description, from_acct, to_acct, amount)
        tx_id = result["transaction_id"]
        
        print(f"    {Fore.GREEN}✓ Accepted: {tx_id[:16]}...")
        
        # Wait for finality
        receipt = await client.wait_for_finality(tx_id, timeout=15.0)
        
        if receipt:
            finality_time = time.time() - start_time
            quorum = receipt.get("quorum_outcome", {})
            approved = quorum.get("approved", False)
            
            if approved:
                valid_count = quorum.get("valid_count", 0)
                total_count = quorum.get("total_count", 0)
                risk_avg = float(quorum.get("risk_avg", 0))
                
                print(f"    {Fore.GREEN}✅ APPROVED "
                      f"({valid_count}/{total_count} validators, "
                      f"risk={risk_avg:.3f}, "
                      f"time={finality_time:.2f}s)")
                
                # Show validator opinions with colors
                opinions = receipt.get("validator_opinions", [])
                print(f"    🤖 Validator Opinions:")
                for i, opinion in enumerate(opinions[:5]):  # Show first 5
                    color = VALIDATOR_COLORS[i % len(VALIDATOR_COLORS)]
                    symbol = "✓" if opinion["valid"] else "✗"
                    risk = opinion["risk_score"]
                    risk_bar = "█" * int(risk * 10)
                    validator_id = opinion["validator_id"][:6]
                    reason = opinion["reasons"][0] if opinion["reasons"] else "No reason"
                    
                    print(f"      {color}{symbol} {validator_id}: "
                          f"Risk={risk:.2f} {risk_bar} {reason}")
                
                return tx_id
            else:
                print(f"    {Fore.RED}❌ REJECTED by quorum")
                
                # Show why it was rejected
                opinions = receipt.get("validator_opinions", [])
                rejection_reasons = set()
                for opinion in opinions:
                    if not opinion["valid"]:
                        rejection_reasons.update(opinion.get("reasons", []))
                
                if rejection_reasons:
                    print(f"    Rejection reasons: {', '.join(list(rejection_reasons)[:3])}")
                
                return None
        else:
            print(f"    {Fore.RED}⏰ TIMEOUT - transaction did not finalize")
            return None
    
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", {}).get("detail", str(e))
        except:
            error_detail = str(e)
        
        expected_symbol = "✓" if should_succeed else "✗" 
        color = Fore.RED if should_succeed else Fore.YELLOW
        
        print(f"    {color}{expected_symbol} REJECTED: {error_detail}")
        return None
    
    except Exception as e:
        print(f"    {Fore.RED}💥 ERROR: {str(e)}")
        return None


async def display_account_balances(client: DemoClient, accounts: List[str]):
    """Display current account balances."""
    print(f"\n  {Fore.CYAN}💰 Account Balances:")
    
    for account in accounts:
        try:
            info = await client.get_account(account)
            balance = info["balance"]
            nonce = info["nonce"]
            tx_count = info["transaction_count"]
            pending = info["pending_count"]
            
            pending_str = f" (+{pending} pending)" if pending > 0 else ""
            
            print(f"    {account:10} {balance:>12} {params.DEFAULT_ASSET} "
                  f"(nonce={nonce}, txs={tx_count}{pending_str})")
        except Exception as e:
            print(f"    {account:10} {Fore.RED}ERROR: {e}")


async def verify_system_integrity(client: DemoClient):
    """Verify system integrity and consistency."""
    print(f"\n  {Fore.CYAN}🔍 System Verification:")
    
    try:
        health = await client.get_health()
        
        # Overall health
        status = health.get("status", "unknown")
        if status == "healthy":
            print(f"    {Fore.GREEN}✓ System Status: {status}")
        else:
            print(f"    {Fore.YELLOW}⚠ System Status: {status}")
        
        # Component health
        components = health.get("components", {})
        for component, info in components.items():
            comp_status = info.get("status", "unknown")
            if comp_status == "healthy":
                print(f"    {Fore.GREEN}✓ {component.title()}: {comp_status}")
            else:
                print(f"    {Fore.YELLOW}⚠ {component.title()}: {comp_status}")
                if "errors" in info:
                    for error in info["errors"][:3]:
                        print(f"      {Fore.RED}- {error}")
        
        # Storage stats
        storage_stats = components.get("storage", {}).get("stats", {})
        if storage_stats:
            files = storage_stats.get("files", {})
            tx_count = files.get("transactions", {}).get("record_count", 0)
            receipt_count = files.get("receipts", {}).get("record_count", 0)
            print(f"    📊 Storage: {tx_count} transactions, {receipt_count} receipts")
        
        # Validator stats
        validator_stats = components.get("validators", {}).get("stats", {})
        if validator_stats:
            active = validator_stats.get("active_validators", 0)
            eligible = validator_stats.get("eligible_validators", 0)
            print(f"    🤖 Validators: {eligible}/{active} eligible/active")
    
    except Exception as e:
        print(f"    {Fore.RED}✗ Verification failed: {e}")


async def run_demo_scenario(mode: str = "stub"):
    """Run the complete demo scenario."""
    
    # Set random seed for reproducible demo
    random.seed(params.DEMO_SEED)
    
    print(f"{Fore.CYAN}{Style.BRIGHT}🚀 AI Ledger Demo")
    print(f"{Fore.CYAN}Mode: {mode.upper()}")
    print(f"{Fore.CYAN}{'='*60}")
    
    # Update LLM mode
    import ai_ledger.params as demo_params
    demo_params.LLM_MODE = mode
    
    try:
        # Start demo node
        print(f"\n{Fore.YELLOW}🖥️  Starting demo node...")
        node_url = await start_demo_node(port=8001)
        print(f"  {Fore.GREEN}✓ Node running at {node_url}")
        
        client = DemoClient(node_url)
        
        # Wait a moment for initialization
        await asyncio.sleep(2)
        
        # Show initial state
        print(f"\n{Fore.YELLOW}🌍 Initial State:")
        await display_account_balances(client, ["alice", "bob", "treasury"])
        
        # Demo transactions
        print(f"\n{Fore.CYAN}{Style.BRIGHT}💫 Demo Transactions")
        print(f"{Fore.CYAN}{'='*60}")
        
        successful_txs = []
        
        # Transaction 1: Normal payment
        print(f"\n{Fore.WHITE}{Style.BRIGHT}Transaction 1: Normal Payment")
        tx1 = await submit_and_display_transaction(
            client,
            "Alice pays Bob 25 LABS for web design work",
            "alice", "bob", "25.0",
            should_succeed=True
        )
        if tx1:
            successful_txs.append(tx1)
        
        # Transaction 2: Small refund
        print(f"\n{Fore.WHITE}{Style.BRIGHT}Transaction 2: Refund Transaction")
        tx2 = await submit_and_display_transaction(
            client,
            "Bob returns 5 LABS to Alice as refund for overcharge",
            "bob", "alice", "5.0",
            should_succeed=True
        )
        if tx2:
            successful_txs.append(tx2)
        
        # Transaction 3: Insufficient balance (should fail)
        print(f"\n{Fore.WHITE}{Style.BRIGHT}Transaction 3: Insufficient Balance [Should Fail]")
        await submit_and_display_transaction(
            client,
            "Alice tries to pay Bob 100 LABS for premium service",
            "alice", "bob", "100.0",
            should_succeed=False
        )
        
        # Transaction 4: Suspicious transaction (should fail in AI modes)
        print(f"\n{Fore.WHITE}{Style.BRIGHT}Transaction 4: Suspicious Pattern [May Fail]")
        await submit_and_display_transaction(
            client,
            "Alice sends suspicious transfer to Bob for urgent hack",
            "alice", "bob", "10.0", 
            should_succeed=(mode == "rule_only")
        )
        
        # Transaction 5: Normal meal payment
        print(f"\n{Fore.WHITE}{Style.BRIGHT}Transaction 5: Meal Payment")
        tx5 = await submit_and_display_transaction(
            client,
            "Alice pays Bob 15 LABS for lunch at the cafe",
            "alice", "bob", "15.0",
            should_succeed=True
        )
        if tx5:
            successful_txs.append(tx5)
        
        # Show final state
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 Final Results")
        print(f"{Fore.CYAN}{'='*60}")
        
        await display_account_balances(client, ["alice", "bob", "treasury"])
        await verify_system_integrity(client)
        
        # Show successful transaction summary
        if successful_txs:
            print(f"\n  {Fore.GREEN}✅ Successful Transactions: {len(successful_txs)}")
            for tx_id in successful_txs:
                print(f"    - {tx_id[:16]}...")
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 Demo completed successfully!")
        
        if mode == "stub":
            print(f"\n{Fore.YELLOW}💡 Tip: Try with OpenAI for real AI validation:")
            print(f"   export OPENAI_API_KEY=your-key")
            print(f"   python -m ai_ledger.demo --mode openai")
        
    except Exception as e:
        print(f"\n{Fore.RED}💥 Demo failed: {e}")
        raise


@app_cli.command()
def main(
    mode: str = typer.Option("stub", "--mode", "-m", 
                            help="LLM mode: openai, stub, or rule_only"),
    verbose: bool = typer.Option(False, "--verbose", "-v",
                                help="Show detailed logs"),
    port: int = typer.Option(8001, "--port", "-p",
                           help="Port for demo node")
):
    """Run the AI Ledger interactive demo."""
    
    # Configure logging
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    else:
        import logging
        logging.basicConfig(level=logging.WARNING)
    
    # Validate mode
    if mode not in ["openai", "stub", "rule_only"]:
        print(f"{Fore.RED}Invalid mode: {mode}")
        print("Valid modes: openai, stub, rule_only")
        raise typer.Exit(1)
    
    # Check OpenAI key if needed
    if mode == "openai":
        import os
        if not os.getenv("OPENAI_API_KEY"):
            print(f"{Fore.RED}OpenAI mode requires OPENAI_API_KEY environment variable")
            print("Set it with: export OPENAI_API_KEY=your-key-here")
            raise typer.Exit(1)
    
    try:
        # Run demo
        asyncio.run(run_demo_scenario(mode))
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Demo interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}Demo failed: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app_cli()