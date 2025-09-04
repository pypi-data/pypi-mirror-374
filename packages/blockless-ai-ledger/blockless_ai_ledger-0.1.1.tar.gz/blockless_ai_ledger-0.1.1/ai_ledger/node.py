"""
Main node API with comprehensive error handling and validation.

Provides REST API for transaction submission, receipt queries,
and system monitoring with production-ready error handling.
"""

import asyncio
import logging
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

import typer
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from . import params
from .transaction import Transaction, SubmitRequest, SubmitResponse
from .account import AccountManager
from .validator import Validator, ValidatorPool
from .quorum import QuorumManager, QuorumError
from .storage import Storage, StorageError
from . import crypto

logger = logging.getLogger(__name__)

# Global state (in production, use dependency injection)
app = FastAPI(
    title="AI Ledger Node",
    version="0.1.0",
    description="AI-validated distributed ledger system",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Node state
storage: Optional[Storage] = None
account_manager: Optional[AccountManager] = None
validator_pool: Optional[ValidatorPool] = None
quorum_manager: Optional[QuorumManager] = None

# Runtime tracking
startup_time = time.time()
mempool: Dict[str, Transaction] = {}
pending_by_account: Dict[str, List[Transaction]] = defaultdict(list)
mempool_lock = asyncio.Lock()

# Rate limiting
request_counts = defaultdict(lambda: {"count": 0, "window_start": time.time()})

# Metrics
class NodeMetrics:
    def __init__(self):
        self.transactions_submitted = 0
        self.transactions_finalized = 0
        self.quorum_failures = 0
        self.avg_finality_time = 0.0
        self.finality_times = []
    
    def record_finality(self, time_seconds: float):
        self.finality_times.append(time_seconds)
        if len(self.finality_times) > 100:  # Keep last 100
            self.finality_times.pop(0)
        self.avg_finality_time = sum(self.finality_times) / len(self.finality_times)

metrics = NodeMetrics()


class ErrorResponse(BaseModel):
    """Consistent error response format."""
    code: str
    detail: str
    transaction_id: Optional[str] = None
    timestamp: str = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now(timezone.utc).isoformat()
        super().__init__(**data)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors to consistent format."""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            code="VALIDATION_ERROR",
            detail=str(exc)
        ).dict()
    )


@app.exception_handler(StorageError)
async def storage_exception_handler(request: Request, exc: StorageError):
    """Handle storage errors gracefully."""
    logger.error(f"Storage error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code="STORAGE_ERROR",
            detail="Internal storage error occurred"
        ).dict()
    )


async def rate_limit_check(request: Request):
    """Per-IP rate limiting."""
    client_ip = request.client.host
    now = time.time()
    
    window = request_counts[client_ip]
    if now - window["window_start"] > 1.0:
        window["count"] = 0
        window["window_start"] = now
    
    window["count"] += 1
    if window["count"] > params.RATE_LIMIT_TPS:
        raise HTTPException(
            status_code=429,
            detail=ErrorResponse(
                code="RATE_LIMIT",
                detail=f"Exceeded {params.RATE_LIMIT_TPS} requests per second"
            ).dict()
        )


@app.post("/submit", response_model=SubmitResponse, dependencies=[Depends(rate_limit_check)])
async def submit_transaction(req: SubmitRequest):
    """
    Submit a new transaction with comprehensive validation.
    
    - Rate limiting per IP
    - Per-account pending limits
    - Nonce conflict detection
    - Idempotent insertion
    """
    async with mempool_lock:
        # Check per-account pending limit
        account_pending = pending_by_account[req.from_acct]
        if len(account_pending) >= params.MAX_PENDING_PER_ACCOUNT:
            raise HTTPException(
                status_code=429,
                detail=ErrorResponse(
                    code="PENDING_LIMIT",
                    detail=f"Account has {len(account_pending)} pending transactions"
                ).dict()
            )
        
        # Check for nonce conflicts
        for pending_tx in account_pending:
            if pending_tx.nonce == req.nonce:
                # Idempotent - return existing if identical
                if (pending_tx.nl_description == req.nl_description and
                    pending_tx.amount == req.amount and
                    pending_tx.to_acct == req.to_acct):
                    return SubmitResponse(
                        transaction_id=pending_tx.id,
                        status="already_pending"
                    )
                else:
                    raise HTTPException(
                        status_code=409,
                        detail=ErrorResponse(
                            code="NONCE_CONFLICT",
                            detail=f"Transaction with nonce {req.nonce} already pending",
                            transaction_id=pending_tx.id
                        ).dict()
                    )
        
        # Create transaction
        tx = Transaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            **req.dict()
        )
        tx.id = tx.compute_id()
        
        # Validate against current account state
        is_valid, error_msg = account_manager.validate_transaction(tx)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    code="INVALID_TRANSACTION",
                    detail=error_msg,
                    transaction_id=tx.id
                ).dict()
            )
        
        # Add to mempool and storage
        mempool[tx.id] = tx
        account_pending.append(tx)
        storage.append_transaction(tx)
        
        metrics.transactions_submitted += 1
        
        # Trigger validation asynchronously
        asyncio.create_task(validate_transaction_async(tx))
        
        return SubmitResponse(
            transaction_id=tx.id,
            status="pending",
            estimated_finality_time=params.OPINION_TIMEOUT_SECS * 2
        )


async def validate_transaction_async(tx: Transaction):
    """Asynchronously validate transaction through quorum process."""
    try:
        start_time = time.time()
        
        logger.info(f"Starting validation for tx {tx.id}")
        
        # Collect validator opinions
        opinions = await quorum_manager.collect_opinions(tx, account_manager)
        
        # Check quorum
        outcome = quorum_manager.check_quorum(opinions)
        
        # Create receipt
        # In a real system, you'd get current account heads
        account_heads = {
            tx.from_acct: account_manager.get_last_receipt(tx.from_acct) or "genesis",
            tx.to_acct: account_manager.get_last_receipt(tx.to_acct) or "genesis"
        }
        
        receipt = quorum_manager.create_receipt(tx, outcome, opinions, account_heads)
        
        # Apply if approved
        if outcome.approved:
            success = account_manager.apply_transaction(tx, receipt.receipt_id)
            if success:
                metrics.transactions_finalized += 1
            else:
                logger.error(f"Failed to apply approved transaction {tx.id}")
        else:
            metrics.quorum_failures += 1
            logger.info(f"Transaction {tx.id} rejected by quorum")
        
        # Store receipt
        storage.append_receipt(receipt)
        
        # Remove from mempool
        async with mempool_lock:
            if tx.id in mempool:
                del mempool[tx.id]
            
            if tx in pending_by_account[tx.from_acct]:
                pending_by_account[tx.from_acct].remove(tx)
        
        # Record finality time
        finality_time = time.time() - start_time
        metrics.record_finality(finality_time)
        
        logger.info(f"Completed validation for tx {tx.id} in {finality_time:.3f}s: "
                   f"approved={outcome.approved}")
        
    except QuorumError as e:
        logger.warning(f"Quorum error for tx {tx.id}: {e}")
        metrics.quorum_failures += 1
    except Exception as e:
        logger.error(f"Validation failed for tx {tx.id}: {e}")
        metrics.quorum_failures += 1


@app.get("/receipt/{tx_id}")
async def get_receipt(tx_id: str):
    """Get finalized receipt or pending status."""
    try:
        # Check for finalized receipt
        receipt = storage.get_receipt(tx_id)
        if receipt:
            return receipt.dict()
        
        # Check if pending
        if tx_id in mempool:
            return {
                "status": "pending",
                "transaction_id": tx_id,
                "estimated_completion": time.time() + params.OPINION_TIMEOUT_SECS
            }
        
        # Not found
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                code="NOT_FOUND",
                detail="Transaction not found",
                transaction_id=tx_id
            ).dict()
        )
        
    except StorageError:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code="STORAGE_ERROR",
                detail="Error retrieving receipt"
            ).dict()
        )


@app.get("/account/{account_id}")
async def get_account(account_id: str):
    """Get account state with recent activity."""
    try:
        # Get current state
        balance = account_manager.get_balance(account_id, params.DEFAULT_ASSET)
        nonce = account_manager.get_nonce(account_id)
        last_receipt_id = account_manager.get_last_receipt(account_id)
        
        # Get recent receipts
        recent_receipts = storage.get_recent_receipts(account_id, limit=10)
        
        # Count pending transactions
        pending_count = len(pending_by_account[account_id])
        
        return {
            "account_id": account_id,
            "balance": str(balance),
            "asset": params.DEFAULT_ASSET,
            "nonce": nonce,
            "last_receipt_id": last_receipt_id,
            "transaction_count": account_manager.accounts.get(account_id, account_manager.get_account(account_id)).transaction_count,
            "pending_count": pending_count,
            "recent_receipts": [r.dict() for r in recent_receipts]
        }
        
    except Exception as e:
        logger.error(f"Error getting account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code="INTERNAL_ERROR",
                detail="Error retrieving account information"
            ).dict()
        )


@app.get("/params")
async def get_params():
    """Return active consensus parameters and their hash."""
    return {
        "schema_version": params.SCHEMA_VERSION,
        "n_validators": params.N_VALIDATORS,
        "quorum_k": params.QUORUM_K,
        "max_risk_avg": params.MAX_RISK_AVG,
        "asset_decimals": params.ASSET_DECIMALS,
        "default_asset": params.DEFAULT_ASSET,
        "params_hash": quorum_manager.params_hash if quorum_manager else None,
        "llm_mode": params.LLM_MODE
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """Prometheus-compatible metrics endpoint."""
    lines = [
        f"# HELP transactions_submitted Total transactions submitted",
        f"# TYPE transactions_submitted counter",
        f"transactions_submitted {metrics.transactions_submitted}",
        
        f"# HELP transactions_finalized Total transactions finalized",
        f"# TYPE transactions_finalized counter", 
        f"transactions_finalized {metrics.transactions_finalized}",
        
        f"# HELP quorum_failures Total quorum failures",
        f"# TYPE quorum_failures counter",
        f"quorum_failures {metrics.quorum_failures}",
        
        f"# HELP avg_finality_time Average time to finality in seconds",
        f"# TYPE avg_finality_time gauge",
        f"avg_finality_time {metrics.avg_finality_time:.3f}",
        
        f"# HELP mempool_size Current mempool size",
        f"# TYPE mempool_size gauge",
        f"mempool_size {len(mempool)}",
        
        f"# HELP active_validators Number of active validators",
        f"# TYPE active_validators gauge",
        f"active_validators {len(validator_pool.get_active_validators()) if validator_pool else 0}",
    ]
    
    # Add per-validator reputation metrics
    if validator_pool:
        for validator in validator_pool.get_active_validators():
            lines.append(f'validator_reputation{{id="{validator.id[:8]}"}} {validator.reputation:.3f}')
    
    return "\n".join(lines)


@app.get("/health")
async def health():
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "version": "0.1.0",
        "schema_version": params.SCHEMA_VERSION,
        "uptime_seconds": time.time() - startup_time,
        "llm_mode": params.LLM_MODE
    }
    
    # Check component health
    components = {}
    
    # Storage health
    try:
        storage_stats = storage.get_storage_stats() if storage else {}
        components["storage"] = {"status": "healthy", "stats": storage_stats}
    except Exception as e:
        components["storage"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Validator health
    if validator_pool:
        validator_stats = validator_pool.get_pool_stats()
        components["validators"] = {
            "status": "healthy" if validator_stats["eligible_validators"] >= params.MIN_DISTINCT_VALIDATORS else "degraded",
            "stats": validator_stats
        }
    
    # Account manager health
    if account_manager:
        try:
            is_valid, errors = account_manager.verify_integrity()
            components["accounts"] = {
                "status": "healthy" if is_valid else "unhealthy",
                "account_count": len(account_manager.accounts),
                "errors": errors if not is_valid else []
            }
            if not is_valid:
                health_status["status"] = "unhealthy"
        except Exception as e:
            components["accounts"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "unhealthy"
    
    health_status["components"] = components
    health_status["mempool_size"] = len(mempool)
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(health_status, status_code=status_code)


@app.get("/debug/mempool")
async def debug_mempool():
    """Debug endpoint for mempool inspection."""
    return {
        "mempool_size": len(mempool),
        "transactions": [tx.to_display_dict() for tx in mempool.values()],
        "pending_by_account": {
            account: len(txs) for account, txs in pending_by_account.items() if txs
        }
    }


async def initialize_node(
    log_dir: str = params.LOG_DIR_DEFAULT,
    validators: Optional[List[Dict]] = None
):
    """Initialize node components."""
    global storage, account_manager, validator_pool, quorum_manager
    
    logger.info("Initializing AI Ledger node...")
    
    # Initialize storage
    storage = Storage(Path(log_dir))
    
    # Rebuild account state from storage
    account_manager = storage.rebuild_state()
    
    # Initialize validator pool
    validator_pool = ValidatorPool()
    
    if validators:
        for validator_data in validators:
            validator = Validator(**validator_data)
            validator_pool.add_validator(validator)
    else:
        # Create default validators for demo
        await create_demo_validators()
    
    # Initialize quorum manager
    active_validators = validator_pool.get_active_validators()
    if len(active_validators) < params.MIN_DISTINCT_VALIDATORS:
        raise ValueError(f"Need at least {params.MIN_DISTINCT_VALIDATORS} validators")
    
    quorum_manager = QuorumManager(active_validators)
    
    logger.info(f"Node initialized with {len(active_validators)} validators")


async def create_demo_validators():
    """Create demo validators for testing."""
    for i in range(params.N_VALIDATORS):
        privkey, pubkey = crypto.generate_keypair()
        validator_id = crypto.create_validator_id(pubkey)
        
        validator = Validator(
            id=validator_id,
            pubkey_hex=pubkey.hex(),
            privkey_hex=privkey.hex(),  # Only for demo
            is_active=True
        )
        
        validator_pool.add_validator(validator)
    
    logger.info(f"Created {params.N_VALIDATORS} demo validators")


def main():
    """CLI entry point for node."""
    app_cli = typer.Typer()
    
    @app_cli.command()
    def run(
        port: int = typer.Option(8001, "--port", "-p", help="Port to run on"),
        host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
        log_dir: str = typer.Option("logs", "--log-dir", help="Log directory"),
        log_level: str = typer.Option("INFO", "--log-level", help="Log level"),
        reload: bool = typer.Option(False, "--reload", help="Enable auto-reload")
    ):
        """Run the AI Ledger node."""
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        async def startup():
            """Startup event handler."""
            await initialize_node(log_dir=log_dir)
        
        app.add_event_handler("startup", startup)
        
        # Run server
        uvicorn.run(
            "ai_ledger.node:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level.lower()
        )
    
    app_cli()


if __name__ == "__main__":
    main()