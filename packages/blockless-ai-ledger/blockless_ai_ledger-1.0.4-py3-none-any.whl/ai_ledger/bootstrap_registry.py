"""
Decentralized bootstrap registry using the blockchain itself.

Creates a self-maintaining registry of stable nodes that can serve as
bootstrap points for new nodes joining the network.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class BootstrapCandidate:
    """Information about a potential bootstrap node."""
    node_id: str
    public_ip: str
    port: int
    uptime_hours: float
    validator_count: int
    reputation: float
    last_seen: float
    consensus_participation: float  # Percentage of consensus rounds participated
    geographic_region: Optional[str] = None
    
    @property
    def endpoint(self) -> str:
        return f"http://{self.public_ip}:{self.port}"
    
    @property
    def stability_score(self) -> float:
        """Calculate stability score for bootstrap eligibility."""
        # Weight factors for bootstrap node selection
        uptime_score = min(1.0, self.uptime_hours / (24 * 30))  # 30 days max
        participation_score = self.consensus_participation
        reputation_score = self.reputation
        recency_score = max(0.0, 1.0 - ((time.time() - self.last_seen) / 3600))  # 1 hour decay
        
        return (uptime_score * 0.4 + 
                participation_score * 0.3 + 
                reputation_score * 0.2 + 
                recency_score * 0.1)
    
    def is_bootstrap_eligible(self) -> bool:
        """Check if this node is eligible to be a bootstrap node."""
        return (
            self.uptime_hours > 24 and  # At least 24 hours uptime
            self.reputation > 0.7 and  # Good reputation
            self.consensus_participation > 0.8 and  # Active in consensus
            self.validator_count >= 2 and  # Contributing validators
            self.stability_score > 0.7  # High stability score
        )
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BootstrapCandidate':
        return cls(**data)


class DecentralizedBootstrapRegistry:
    """
    Self-maintaining bootstrap registry using the blockchain itself.
    
    Stores bootstrap node information in special transactions on the ledger,
    allowing the network to maintain its own discovery infrastructure.
    """
    
    def __init__(self, node_id: str, storage_manager, account_manager):
        self.node_id = node_id
        self.storage = storage_manager
        self.account_manager = account_manager
        
        # Bootstrap candidates
        self.candidates: Dict[str, BootstrapCandidate] = {}
        self.bootstrap_nodes: List[str] = []
        
        # Registry maintenance
        self.min_bootstrap_nodes = 5
        self.max_bootstrap_nodes = 15
        self.registry_refresh_interval = 3600.0  # 1 hour
        
        # Our node stats for registration
        self.start_time = time.time()
        self.consensus_rounds = 0
        self.consensus_participations = 0
    
    async def start(self):
        """Start the bootstrap registry system."""
        logger.info("Starting decentralized bootstrap registry...")
        
        # Load existing registry from blockchain
        await self._load_registry_from_blockchain()
        
        # Start maintenance tasks
        asyncio.create_task(self._registry_maintenance_loop())
        asyncio.create_task(self._self_registration_loop())
        
        logger.info(f"Bootstrap registry started with {len(self.candidates)} candidates")
    
    async def _load_registry_from_blockchain(self):
        """Load bootstrap registry from special transactions on blockchain."""
        try:
            # Look for special "registry" transactions in storage
            # These would be special transactions with type="bootstrap_registry"
            
            # For now, use a simple file-based approach that could be moved on-chain
            registry_data = await self._load_registry_cache()
            
            for candidate_data in registry_data:
                candidate = BootstrapCandidate.from_dict(candidate_data)
                if candidate.is_bootstrap_eligible():
                    self.candidates[candidate.node_id] = candidate
            
            # Update bootstrap node list
            self._update_bootstrap_node_list()
            
        except Exception as e:
            logger.error(f"Failed to load registry from blockchain: {e}")
    
    async def _load_registry_cache(self) -> List[dict]:
        """Load registry from cache file (transitional approach)."""
        try:
            from .storage_utils import read_json_lines_safely
            registry_file = self.storage.log_dir / "bootstrap_registry.jsonl"
            
            if registry_file.exists():
                return read_json_lines_safely(registry_file)
        except Exception as e:
            logger.debug(f"No registry cache found: {e}")
        return []
    
    async def _save_registry_cache(self):
        """Save registry to cache file."""
        try:
            from .storage_utils import safe_write_json_line
            registry_file = self.storage.log_dir / "bootstrap_registry.jsonl"
            
            # Write all candidates
            registry_data = {
                "registry_update": True,
                "timestamp": time.time(),
                "candidates": [candidate.to_dict() for candidate in self.candidates.values()]
            }
            
            safe_write_json_line(registry_file, registry_data, fsync=True)
            
        except Exception as e:
            logger.error(f"Failed to save registry cache: {e}")
    
    def _update_bootstrap_node_list(self):
        """Update the list of active bootstrap nodes."""
        # Get top bootstrap candidates
        eligible_candidates = [c for c in self.candidates.values() if c.is_bootstrap_eligible()]
        eligible_candidates.sort(key=lambda c: c.stability_score, reverse=True)
        
        # Maintain geographic diversity if possible
        selected_nodes = []
        used_regions = set()
        
        # First pass: select one node per region
        for candidate in eligible_candidates:
            if len(selected_nodes) >= self.max_bootstrap_nodes:
                break
            
            region = candidate.geographic_region or 'unknown'
            if region not in used_regions or len(used_regions) >= 3:
                selected_nodes.append(candidate.endpoint)
                used_regions.add(region)
        
        # Second pass: fill remaining slots with best candidates
        for candidate in eligible_candidates:
            if len(selected_nodes) >= self.max_bootstrap_nodes:
                break
            if candidate.endpoint not in selected_nodes:
                selected_nodes.append(candidate.endpoint)
        
        self.bootstrap_nodes = selected_nodes
        logger.info(f"Updated bootstrap registry: {len(self.bootstrap_nodes)} active nodes")
    
    async def _registry_maintenance_loop(self):
        """Periodically maintain the bootstrap registry."""
        while True:
            try:
                # Update registry from network
                await self._collect_bootstrap_candidates()
                
                # Clean up stale candidates
                await self._cleanup_stale_candidates()
                
                # Update bootstrap node list
                self._update_bootstrap_node_list()
                
                # Save registry
                await self._save_registry_cache()
                
                await asyncio.sleep(self.registry_refresh_interval)
                
            except Exception as e:
                logger.error(f"Registry maintenance error: {e}")
                await asyncio.sleep(300)  # 5 minute backoff
    
    async def _collect_bootstrap_candidates(self):
        """Collect bootstrap candidates from network peers."""
        # This would query peers for their node statistics
        # For now, we'll implement a simple approach
        
        # In production, this would:
        # 1. Query all known peers for their stats
        # 2. Verify their stability and uptime
        # 3. Check their consensus participation
        # 4. Add eligible nodes as bootstrap candidates
        
        pass  # Implementation depends on peer discovery integration
    
    async def _cleanup_stale_candidates(self):
        """Remove candidates that are no longer eligible."""
        current_time = time.time()
        stale_candidates = []
        
        for node_id, candidate in self.candidates.items():
            # Remove if too old or poor performance
            if (current_time - candidate.last_seen > 86400 or  # 24 hours
                candidate.stability_score < 0.5):
                stale_candidates.append(node_id)
        
        for node_id in stale_candidates:
            del self.candidates[node_id]
            logger.debug(f"Removed stale bootstrap candidate {node_id[:8]}...")
    
    async def _self_registration_loop(self):
        """Register ourselves as a bootstrap candidate if eligible."""
        while True:
            try:
                await asyncio.sleep(1800)  # Check every 30 minutes
                
                # Calculate our stats
                uptime_hours = (time.time() - self.start_time) / 3600
                participation_rate = (self.consensus_participations / self.consensus_rounds 
                                    if self.consensus_rounds > 0 else 0.0)
                
                # Create our candidate entry
                our_candidate = BootstrapCandidate(
                    node_id=self.node_id,
                    public_ip="127.0.0.1",  # Will be updated by global discovery
                    port=8001,  # Will be updated
                    uptime_hours=uptime_hours,
                    validator_count=len(distributed_validator_pool.local_validators) if distributed_validator_pool else 0,
                    reputation=1.0,  # Would be calculated from validator performance
                    last_seen=time.time(),
                    consensus_participation=participation_rate
                )
                
                # Register if eligible
                if our_candidate.is_bootstrap_eligible():
                    self.candidates[self.node_id] = our_candidate
                    logger.info(f"Registered as bootstrap candidate (stability: {our_candidate.stability_score:.2f})")
                
            except Exception as e:
                logger.error(f"Self-registration error: {e}")
    
    def record_consensus_participation(self, participated: bool):
        """Record our participation in a consensus round."""
        self.consensus_rounds += 1
        if participated:
            self.consensus_participations += 1
    
    def get_bootstrap_nodes(self) -> List[str]:
        """Get current list of bootstrap nodes."""
        return self.bootstrap_nodes.copy()
    
    def get_registry_stats(self) -> dict:
        """Get statistics about the bootstrap registry."""
        eligible_count = sum(1 for c in self.candidates.values() if c.is_bootstrap_eligible())
        
        return {
            "total_candidates": len(self.candidates),
            "eligible_candidates": eligible_count,
            "active_bootstrap_nodes": len(self.bootstrap_nodes),
            "registry_age_hours": (time.time() - self.start_time) / 3600,
            "geographic_distribution": self._get_geographic_distribution()
        }
    
    def _get_geographic_distribution(self) -> dict:
        """Get geographic distribution of bootstrap candidates."""
        regions = {}
        for candidate in self.candidates.values():
            region = candidate.geographic_region or 'unknown'
            regions[region] = regions.get(region, 0) + 1
        return regions


# Hardcoded community bootstrap nodes for initial network seeding
COMMUNITY_BOOTSTRAP_NODES = [
    # These would be stable, community-operated nodes
    # In practice, these would be operated by different organizations/individuals
    # to ensure true decentralization
    
    # Community members can add their stable nodes here via pull requests
    "ailedger-bootstrap1.example.org:8001",
    "ailedger-bootstrap2.example.org:8001", 
    "ailedger-bootstrap3.example.org:8001",
    
    # Geographic distribution
    "bootstrap-us.ailedger.community:8001",
    "bootstrap-eu.ailedger.community:8001", 
    "bootstrap-asia.ailedger.community:8001",
    
    # Fallback to any existing stable deployments
    # (These would be replaced with community nodes over time)
]


def get_initial_bootstrap_nodes() -> List[str]:
    """
    Get initial bootstrap nodes for network discovery.
    
    In a mature network, this would query the bootstrap registry.
    For initial deployment, uses hardcoded community nodes.
    """
    # Try to load from local registry first
    try:
        from pathlib import Path
        registry_file = Path("bootstrap_registry.json")
        
        if registry_file.exists():
            with open(registry_file) as f:
                data = json.load(f)
                nodes = data.get('active_nodes', [])
                if nodes:
                    return nodes
    except Exception:
        pass
    
    # Fallback to community bootstrap nodes
    return COMMUNITY_BOOTSTRAP_NODES.copy()


async def update_community_bootstrap_registry(
    public_ip: str, 
    port: int, 
    node_id: str,
    uptime_hours: float,
    stability_score: float
):
    """
    Update the community bootstrap registry.
    
    This would eventually be stored on the blockchain itself,
    making the registry fully decentralized.
    """
    if stability_score < 0.8 or uptime_hours < 72:  # 3 days minimum
        return False
    
    # For now, save to local file that could be shared via IPFS or Git
    registry_entry = {
        "node_id": node_id,
        "endpoint": f"{public_ip}:{port}",
        "uptime_hours": uptime_hours,
        "stability_score": stability_score,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }
    
    try:
        from pathlib import Path
        registry_file = Path("bootstrap_registry.json")
        
        # Load existing registry
        registry_data = {"active_nodes": [], "candidates": []}
        if registry_file.exists():
            with open(registry_file) as f:
                registry_data = json.load(f)
        
        # Add our entry
        registry_data["candidates"].append(registry_entry)
        
        # Clean up expired entries
        now = datetime.now(timezone.utc)
        registry_data["candidates"] = [
            entry for entry in registry_data["candidates"]
            if datetime.fromisoformat(entry["expires_at"]) > now
        ]
        
        # Update active nodes list
        eligible_candidates = [
            entry for entry in registry_data["candidates"]
            if entry["stability_score"] > 0.8
        ]
        
        # Sort by stability and take top candidates
        eligible_candidates.sort(key=lambda x: x["stability_score"], reverse=True)
        registry_data["active_nodes"] = [
            entry["endpoint"] for entry in eligible_candidates[:15]
        ]
        
        # Save registry
        with open(registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
        
        logger.info(f"Updated community bootstrap registry with {len(registry_data['active_nodes'])} active nodes")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update bootstrap registry: {e}")
        return False