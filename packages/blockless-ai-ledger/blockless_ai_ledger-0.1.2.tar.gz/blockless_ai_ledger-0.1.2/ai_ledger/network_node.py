"""
Enhanced network-enabled AI Ledger node with peer-to-peer capabilities.

Extends the base node with distributed validation and peer networking.
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

import typer
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import params, crypto
from .node import (
    app as base_app, storage, account_manager, validator_pool, quorum_manager,
    initialize_node as base_initialize_node, startup_time, metrics
)
from .p2p import P2PNetwork
from .distributed_validator import DistributedValidatorPool, ValidatorCoordinator
from .validator import Validator
from .transaction import Transaction, SubmitRequest, SubmitResponse

logger = logging.getLogger(__name__)

# Network state
p2p_network: Optional[P2PNetwork] = None
distributed_validator_pool: Optional[DistributedValidatorPool] = None
validator_coordinator: Optional[ValidatorCoordinator] = None

# Create network-enabled app
network_app = FastAPI(
    title="AI Ledger Network Node",
    version="0.1.0",
    description="Distributed AI-validated ledger with peer-to-peer networking",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web UI
network_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Copy all routes from base app
for route in base_app.routes:
    network_app.routes.append(route)

# Add network-specific routes
@network_app.post("/validate", response_model=dict)
async def remote_validation_endpoint(request: dict):
    """
    Remote validation endpoint for distributed validators.
    
    This allows other nodes to request validation from local validators.
    """
    try:
        tx_data = request.get('transaction', {})
        validator_id = request.get('validator_id')
        
        if not validator_id or validator_id not in distributed_validator_pool.local_validators:
            raise HTTPException(status_code=404, detail="Validator not found")
        
        # Create transaction object
        tx = Transaction(**tx_data)
        
        # Get local validator
        validator = distributed_validator_pool.local_validators[validator_id]
        
        # Evaluate transaction
        opinion = await validator.evaluate_transaction(tx, account_manager)
        
        return opinion.dict()
        
    except Exception as e:
        logger.error(f"Remote validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@network_app.get("/network/stats")
async def get_network_stats():
    """Get network and validator statistics."""
    network_stats = {}
    validator_stats = {}
    
    if p2p_network:
        network_stats = p2p_network.get_peer_stats()
    
    if distributed_validator_pool:
        validator_stats = distributed_validator_pool.get_validator_stats()
    
    return {
        "node_info": {
            "node_id": network_stats.get('node_id', 'unknown'),
            "uptime_seconds": time.time() - startup_time,
            "llm_mode": params.LLM_MODE
        },
        "network": network_stats,
        "validators": validator_stats,
        "consensus": {
            "required_validators": params.QUORUM_K,
            "max_risk_threshold": params.MAX_RISK_AVG
        }
    }


@network_app.get("/network/peers")
async def get_network_peers():
    """Get information about network peers."""
    if not p2p_network:
        return {"error": "P2P network not initialized"}
    
    return {
        "peers": p2p_network.get_all_peers(),
        "stats": p2p_network.get_peer_stats()
    }


@network_app.post("/network/connect")
async def connect_to_peer(request: dict):
    """Manually connect to a peer node."""
    try:
        peer_endpoint = request.get('endpoint')
        if not peer_endpoint:
            raise HTTPException(status_code=400, detail="endpoint required")
        
        if p2p_network:
            await p2p_network._discover_peers_from_node(peer_endpoint)
            return {"status": "connection attempted", "endpoint": peer_endpoint}
        else:
            raise HTTPException(status_code=503, detail="P2P network not initialized")
            
    except Exception as e:
        logger.error(f"Manual peer connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class NetworkNodeConfig(BaseModel):
    """Configuration for network node."""
    port: int = 8001
    host: str = "0.0.0.0"
    log_dir: str = "logs"
    log_level: str = "INFO"
    
    # Network settings
    bootstrap_nodes: List[str] = []
    enable_p2p: bool = True
    node_id: Optional[str] = None
    
    # Validator settings
    create_validators: bool = True
    validator_count: int = 2  # Fewer per node for distribution


async def initialize_network_node(config: NetworkNodeConfig):
    """Initialize the network-enabled AI Ledger node."""
    global p2p_network, distributed_validator_pool, validator_coordinator
    
    logger.info("Initializing network-enabled AI Ledger node...")
    
    # Initialize base node components first
    await base_initialize_node(log_dir=config.log_dir)
    
    # Generate node ID if not provided
    if not config.node_id:
        privkey, pubkey = crypto.generate_keypair()
        config.node_id = crypto.create_validator_id(pubkey)[:16]  # Shorter node ID
    
    # Create local validators with individual API keys
    local_validators = []
    if config.create_validators:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key and params.LLM_MODE == "openai":
            logger.warning("OPENAI_API_KEY not set, validators will use stub mode")
        
        for i in range(config.validator_count):
            privkey, pubkey = crypto.generate_keypair()
            validator_id = crypto.create_validator_id(pubkey)
            
            validator = Validator(
                id=validator_id,
                pubkey_hex=pubkey.hex(),
                privkey_hex=privkey.hex(),
                is_active=True
            )
            
            local_validators.append(validator)
    
    # Initialize distributed validator pool
    distributed_validator_pool = DistributedValidatorPool(
        node_id=config.node_id,
        local_validators=local_validators
    )
    
    await distributed_validator_pool.start()
    
    # Initialize validator coordinator
    validator_coordinator = ValidatorCoordinator(distributed_validator_pool)
    
    # Initialize P2P network if enabled
    if config.enable_p2p:
        p2p_network = P2PNetwork(
            node_id=config.node_id,
            port=config.port,
            bootstrap_nodes=config.bootstrap_nodes
        )
        
        await p2p_network.start()
        
        # Announce validators to network
        await distributed_validator_pool.announce_validators_to_network(p2p_network)
        
        # Start periodic announcements
        asyncio.create_task(_periodic_announcements())
    
    logger.info(f"Network node initialized:")
    logger.info(f"  Node ID: {config.node_id}")
    logger.info(f"  Local validators: {len(local_validators)}")
    logger.info(f"  P2P enabled: {config.enable_p2p}")
    logger.info(f"  Bootstrap nodes: {len(config.bootstrap_nodes)}")


async def _periodic_announcements():
    """Periodically announce validators to the network."""
    while True:
        try:
            if distributed_validator_pool and p2p_network:
                await distributed_validator_pool.announce_validators_to_network(p2p_network)
            await asyncio.sleep(30)  # Announce every 30 seconds
        except Exception as e:
            logger.error(f"Periodic announcement error: {e}")
            await asyncio.sleep(5)


def create_bootstrap_script(
    node_name: str = "ailedger-node",
    port: int = 8001,
    bootstrap_nodes: List[str] = None
) -> str:
    """Create a bootstrap script for easy node deployment."""
    
    bootstrap_nodes = bootstrap_nodes or [
        "https://bootstrap1.ailedger.network:8001",
        "https://bootstrap2.ailedger.network:8001"
    ]
    
    script = f'''#!/bin/bash
# AI Ledger Node Bootstrap Script
# Generated on {datetime.now().isoformat()}

set -e

echo "🚀 Setting up AI Ledger Node: {node_name}"

# Check requirements
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ required. Please install Python first."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git required. Please install Git first."
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Using stub mode for AI validation."
    echo "   To use real AI, set: export OPENAI_API_KEY=your-key-here"
    export LLM_MODE="stub"
else
    echo "✅ OpenAI API key detected. Using real AI validation."
    export LLM_MODE="openai"
fi

# Create node directory
mkdir -p {node_name}
cd {node_name}

# Clone repository (in real deployment, this would be a proper release)
if [ ! -d "blockless" ]; then
    echo "📥 Cloning AI Ledger repository..."
    git clone https://github.com/netharalabs/blockless.git
fi

cd blockless

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e .

# Set configuration
export AI_LEDGER_PORT={port}
export AI_LEDGER_LOG_LEVEL="INFO"
export AI_LEDGER_NODE_NAME="{node_name}"

# Bootstrap nodes for peer discovery
BOOTSTRAP_NODES="{','.join(bootstrap_nodes)}"

echo "🔗 Starting AI Ledger Node..."
echo "   Port: {port}"
echo "   Node: {node_name}"
echo "   AI Mode: $LLM_MODE"
echo "   Bootstrap: $BOOTSTRAP_NODES"
echo ""

# Start node
python -m ai_ledger.network_node \\
    --port {port} \\
    --host 0.0.0.0 \\
    --bootstrap-nodes $BOOTSTRAP_NODES \\
    --node-name {node_name}

echo "🎉 AI Ledger Node started!"
echo "   API: http://localhost:{port}"
echo "   Docs: http://localhost:{port}/docs"
echo "   Network Stats: http://localhost:{port}/network/stats"
'''
    
    return script


def main():
    """CLI entry point for network node."""
    app_cli = typer.Typer()
    
    @app_cli.command()
    def run(
        port: int = typer.Option(8001, "--port", "-p", help="Port to run on"),
        host: str = typer.Option("0.0.0.0", "--host", help="Host to bind to"),
        log_dir: str = typer.Option("logs", "--log-dir", help="Log directory"),
        log_level: str = typer.Option("INFO", "--log-level", help="Log level"),
        bootstrap_nodes: List[str] = typer.Option([], "--bootstrap-nodes", help="Bootstrap node URLs"),
        node_name: str = typer.Option("", "--node-name", help="Human-readable node name"),
        disable_p2p: bool = typer.Option(False, "--disable-p2p", help="Disable P2P networking"),
        validator_count: int = typer.Option(2, "--validators", help="Number of local validators")
    ):
        """Run the AI Ledger network node."""
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create configuration
        config = NetworkNodeConfig(
            port=port,
            host=host,
            log_dir=log_dir,
            log_level=log_level,
            bootstrap_nodes=bootstrap_nodes,
            enable_p2p=not disable_p2p,
            validator_count=validator_count
        )
        
        async def startup():
            """Startup event handler."""
            await initialize_network_node(config)
        
        network_app.add_event_handler("startup", startup)
        
        # Start message
        print(f"🚀 Starting AI Ledger Network Node")
        print(f"   Port: {port}")
        print(f"   P2P: {'enabled' if not disable_p2p else 'disabled'}")
        print(f"   Validators: {validator_count}")
        print(f"   Bootstrap: {len(bootstrap_nodes)} nodes")
        
        if os.getenv("OPENAI_API_KEY"):
            print(f"   AI Mode: OpenAI (real validation)")
        else:
            print(f"   AI Mode: Stub (demo only)")
            print(f"   💡 Set OPENAI_API_KEY for real AI validation")
        
        print("")
        
        # Run server
        uvicorn.run(
            "ai_ledger.network_node:network_app",
            host=host,
            port=port,
            reload=False,
            log_level=log_level.lower()
        )
    
    @app_cli.command()
    def bootstrap(
        output_file: str = typer.Option("bootstrap.sh", "--output", "-o", help="Output script file"),
        node_name: str = typer.Option("my-ailedger-node", "--name", help="Node name"),
        port: int = typer.Option(8001, "--port", help="Node port"),
        bootstrap_nodes: List[str] = typer.Option([], "--bootstrap", help="Bootstrap nodes")
    ):
        """Generate a bootstrap script for easy node deployment."""
        
        script = create_bootstrap_script(
            node_name=node_name,
            port=port,
            bootstrap_nodes=bootstrap_nodes
        )
        
        with open(output_file, 'w') as f:
            f.write(script)
        
        os.chmod(output_file, 0o755)  # Make executable
        
        print(f"✅ Bootstrap script created: {output_file}")
        print(f"   Run with: ./{output_file}")
        print(f"   Or: bash {output_file}")
    
    app_cli()


if __name__ == "__main__":
    main()