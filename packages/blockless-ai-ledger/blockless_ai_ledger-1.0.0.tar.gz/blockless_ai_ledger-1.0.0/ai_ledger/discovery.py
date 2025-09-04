"""
Fully decentralized peer discovery system for AI Ledger nodes.

Implements multiple discovery mechanisms:
1. mDNS/Bonjour for local network discovery
2. DHT (Distributed Hash Table) for wide-area discovery  
3. Seed exchange protocol for bootstrapping
4. Gossip protocol for efficient propagation
"""

import asyncio
import json
import logging
import hashlib
import time
import socket
import struct
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class PeerAddress:
    """Network address of a peer."""
    host: str
    port: int
    node_id: str
    last_seen: float
    validator_count: int = 0
    reputation: float = 1.0
    
    @property
    def endpoint(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PeerAddress':
        return cls(**data)


class DecentralizedDiscovery:
    """Fully decentralized peer discovery system."""
    
    def __init__(self, node_id: str, port: int, network_id: str = "ailedger-mainnet"):
        self.node_id = node_id
        self.port = port
        self.network_id = network_id
        self.local_ip = self._get_local_ip()
        
        # Peer management
        self.known_peers: Dict[str, PeerAddress] = {}
        self.seed_peers: Set[str] = set()
        self.max_peers = 50
        
        # Discovery mechanisms
        self.mdns_enabled = True
        self.dht_enabled = True
        self.gossip_enabled = True
        
        # Network state
        self.is_running = False
        self.session = None
        
        # Discovery intervals
        self.mdns_interval = 30.0
        self.dht_refresh_interval = 300.0  # 5 minutes
        self.gossip_interval = 60.0
        self.peer_timeout = 300.0  # 5 minutes
    
    def _get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'
    
    async def start(self, initial_peers: List[str] = None):
        """Start decentralized discovery."""
        logger.info(f"Starting decentralized discovery for node {self.node_id[:8]}...")
        
        if self.is_running:
            return
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10.0)
        )
        
        # Add initial peers as seeds
        if initial_peers:
            for peer_addr in initial_peers:
                self.seed_peers.add(peer_addr)
        
        # Start discovery mechanisms
        tasks = []
        
        if self.mdns_enabled:
            tasks.append(asyncio.create_task(self._mdns_discovery_loop()))
            tasks.append(asyncio.create_task(self._mdns_announce_loop()))
        
        if self.dht_enabled:
            tasks.append(asyncio.create_task(self._dht_discovery_loop()))
        
        if self.gossip_enabled:
            tasks.append(asyncio.create_task(self._gossip_loop()))
        
        # Peer maintenance
        tasks.append(asyncio.create_task(self._peer_maintenance_loop()))
        
        # Bootstrap from seeds
        await self._bootstrap_from_seeds()
        
        self.is_running = True
        logger.info(f"Decentralized discovery started with {len(self.known_peers)} peers")
    
    async def stop(self):
        """Stop discovery system."""
        if not self.is_running:
            return
        
        logger.info("Stopping decentralized discovery")
        self.is_running = False
        
        if self.session:
            await self.session.close()
    
    async def _bootstrap_from_seeds(self):
        """Bootstrap discovery from seed peers."""
        if not self.seed_peers:
            logger.warning("No seed peers provided - starting in isolation mode")
            return
        
        bootstrap_success = 0
        for seed_addr in self.seed_peers:
            try:
                # Try to connect and get peer list
                peers = await self._fetch_peers_from_node(seed_addr)
                if peers:
                    for peer_data in peers:
                        await self._add_peer_from_data(peer_data)
                    bootstrap_success += 1
                    
            except Exception as e:
                logger.debug(f"Failed to bootstrap from {seed_addr}: {e}")
        
        if bootstrap_success == 0:
            logger.warning("Bootstrap failed - no seed peers responded")
        else:
            logger.info(f"Bootstrapped from {bootstrap_success}/{len(self.seed_peers)} seeds")
    
    async def _fetch_peers_from_node(self, node_endpoint: str) -> List[dict]:
        """Fetch peer list from a node."""
        try:
            async with self.session.get(f"{node_endpoint}/discovery/peers") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('peers', [])
        except Exception as e:
            logger.debug(f"Failed to fetch peers from {node_endpoint}: {e}")
        return []
    
    async def _add_peer_from_data(self, peer_data: dict):
        """Add peer from discovery data."""
        try:
            peer = PeerAddress.from_dict(peer_data)
            
            # Don't add ourselves
            if peer.node_id == self.node_id:
                return
            
            # Verify peer is reachable before adding
            if await self._verify_peer(peer):
                self.known_peers[peer.node_id] = peer
                logger.debug(f"Added peer {peer.node_id[:8]}... at {peer.endpoint}")
                
        except Exception as e:
            logger.debug(f"Failed to add peer from data: {e}")
    
    async def _verify_peer(self, peer: PeerAddress) -> bool:
        """Verify peer is reachable and valid."""
        try:
            async with self.session.get(
                f"{peer.endpoint}/discovery/ping",
                params={'node_id': self.node_id}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Verify it's the correct node and network
                    if (data.get('node_id') == peer.node_id and 
                        data.get('network_id') == self.network_id):
                        peer.last_seen = time.time()
                        return True
        except Exception:
            pass
        return False
    
    # mDNS Discovery for Local Networks
    async def _mdns_discovery_loop(self):
        """Discover peers on local network using mDNS."""
        while self.is_running:
            try:
                # Simple UDP multicast for local discovery
                await self._mdns_discover_local_peers()
                await asyncio.sleep(self.mdns_interval)
            except Exception as e:
                logger.error(f"mDNS discovery error: {e}")
                await asyncio.sleep(5)
    
    async def _mdns_announce_loop(self):
        """Announce presence on local network."""
        while self.is_running:
            try:
                await self._mdns_announce_presence()
                await asyncio.sleep(self.mdns_interval)
            except Exception as e:
                logger.error(f"mDNS announce error: {e}")
                await asyncio.sleep(5)
    
    async def _mdns_discover_local_peers(self):
        """Discover peers on local network using UDP multicast."""
        try:
            # Create multicast socket for discovery
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(1.0)
            
            # Join multicast group
            multicast_group = '224.0.0.251'
            multicast_port = 5353
            
            # Send discovery request
            discovery_msg = json.dumps({
                'type': 'discovery_request',
                'node_id': self.node_id,
                'network_id': self.network_id,
                'timestamp': time.time()
            })
            
            sock.sendto(discovery_msg.encode(), (multicast_group, multicast_port))
            
            # Listen for responses
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    await self._process_mdns_response(data.decode(), addr)
            except socket.timeout:
                pass
            
            sock.close()
            
        except Exception as e:
            logger.debug(f"mDNS discovery failed: {e}")
    
    async def _mdns_announce_presence(self):
        """Announce our presence on local network."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            multicast_group = '224.0.0.251'
            multicast_port = 5353
            
            announcement = json.dumps({
                'type': 'node_announcement',
                'node_id': self.node_id,
                'network_id': self.network_id,
                'host': self.local_ip,
                'port': self.port,
                'timestamp': time.time()
            })
            
            sock.sendto(announcement.encode(), (multicast_group, multicast_port))
            sock.close()
            
        except Exception as e:
            logger.debug(f"mDNS announce failed: {e}")
    
    async def _process_mdns_response(self, data: str, addr: Tuple[str, int]):
        """Process mDNS response from another node."""
        try:
            msg = json.loads(data)
            
            if msg.get('network_id') != self.network_id:
                return
            
            if msg.get('type') == 'node_announcement':
                peer_data = {
                    'node_id': msg['node_id'],
                    'host': msg['host'],
                    'port': msg['port'],
                    'last_seen': time.time(),
                    'validator_count': 0
                }
                await self._add_peer_from_data(peer_data)
                
        except Exception as e:
            logger.debug(f"Failed to process mDNS response: {e}")
    
    # DHT-like Discovery for Wide Area Networks
    async def _dht_discovery_loop(self):
        """DHT-like discovery for wide area networks."""
        while self.is_running:
            try:
                await self._dht_refresh_routing_table()
                await asyncio.sleep(self.dht_refresh_interval)
            except Exception as e:
                logger.error(f"DHT discovery error: {e}")
                await asyncio.sleep(30)
    
    async def _dht_refresh_routing_table(self):
        """Refresh DHT routing table by querying peers."""
        if not self.known_peers:
            return
        
        # Query random peers for their peer lists
        sample_size = min(5, len(self.known_peers))
        sample_peers = list(self.known_peers.values())[:sample_size]
        
        for peer in sample_peers:
            try:
                peers = await self._fetch_peers_from_node(peer.endpoint)
                for peer_data in peers:
                    await self._add_peer_from_data(peer_data)
            except Exception:
                continue
    
    # Gossip Protocol for Efficient Propagation
    async def _gossip_loop(self):
        """Gossip protocol for efficient peer information propagation."""
        while self.is_running:
            try:
                await self._gossip_peer_information()
                await asyncio.sleep(self.gossip_interval)
            except Exception as e:
                logger.error(f"Gossip loop error: {e}")
                await asyncio.sleep(10)
    
    async def _gossip_peer_information(self):
        """Gossip our peer information to random subset of peers."""
        if len(self.known_peers) < 3:
            return
        
        # Select random subset for gossip (sqrt(n) for optimal epidemic spread)
        import math
        gossip_count = max(2, int(math.sqrt(len(self.known_peers))))
        gossip_peers = list(self.known_peers.values())[:gossip_count]
        
        # Prepare gossip message with our peer list
        our_peers = [peer.to_dict() for peer in list(self.known_peers.values())[:20]]
        
        gossip_msg = {
            'type': 'peer_gossip',
            'sender_id': self.node_id,
            'network_id': self.network_id,
            'peers': our_peers,
            'timestamp': time.time()
        }
        
        # Send gossip to selected peers
        tasks = []
        for peer in gossip_peers:
            task = self._send_gossip_message(peer, gossip_msg)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_gossip_message(self, peer: PeerAddress, message: dict):
        """Send gossip message to a peer."""
        try:
            async with self.session.post(
                f"{peer.endpoint}/discovery/gossip",
                json=message
            ) as resp:
                if resp.status == 200:
                    peer.last_seen = time.time()
                    peer.reputation = min(1.0, peer.reputation + 0.01)
                else:
                    peer.reputation = max(0.0, peer.reputation - 0.05)
        except Exception:
            peer.reputation = max(0.0, peer.reputation - 0.1)
    
    # Peer Maintenance
    async def _peer_maintenance_loop(self):
        """Maintain peer list by removing stale peers."""
        while self.is_running:
            try:
                current_time = time.time()
                stale_peers = []
                
                for node_id, peer in self.known_peers.items():
                    if current_time - peer.last_seen > self.peer_timeout:
                        stale_peers.append(node_id)
                    elif peer.reputation < 0.1:
                        stale_peers.append(node_id)
                
                # Remove stale peers
                for node_id in stale_peers:
                    del self.known_peers[node_id]
                    logger.debug(f"Removed stale peer {node_id[:8]}...")
                
                # Maintain peer count
                if len(self.known_peers) > self.max_peers:
                    # Remove lowest reputation peers
                    sorted_peers = sorted(
                        self.known_peers.items(), 
                        key=lambda x: x[1].reputation
                    )
                    excess = len(self.known_peers) - self.max_peers
                    for node_id, _ in sorted_peers[:excess]:
                        del self.known_peers[node_id]
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Peer maintenance error: {e}")
                await asyncio.sleep(30)
    
    # Public Interface
    def get_discovery_stats(self) -> dict:
        """Get discovery statistics."""
        return {
            'node_id': self.node_id,
            'network_id': self.network_id,
            'local_endpoint': f"{self.local_ip}:{self.port}",
            'known_peers': len(self.known_peers),
            'seed_peers': len(self.seed_peers),
            'discovery_mechanisms': {
                'mdns': self.mdns_enabled,
                'dht': self.dht_enabled,
                'gossip': self.gossip_enabled
            },
            'peer_distribution': self._get_peer_distribution()
        }
    
    def _get_peer_distribution(self) -> dict:
        """Get distribution of peers by reputation."""
        if not self.known_peers:
            return {}
        
        excellent = sum(1 for p in self.known_peers.values() if p.reputation > 0.8)
        good = sum(1 for p in self.known_peers.values() if 0.6 < p.reputation <= 0.8)
        fair = sum(1 for p in self.known_peers.values() if 0.4 < p.reputation <= 0.6)
        poor = sum(1 for p in self.known_peers.values() if p.reputation <= 0.4)
        
        return {
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'poor': poor
        }
    
    def get_best_peers(self, count: int = 10) -> List[PeerAddress]:
        """Get best peers by reputation."""
        peers = list(self.known_peers.values())
        peers.sort(key=lambda p: (p.reputation, -p.last_seen), reverse=True)
        return peers[:count]
    
    def add_seed_peer(self, peer_endpoint: str):
        """Add a seed peer for bootstrapping."""
        self.seed_peers.add(peer_endpoint)
    
    def remove_seed_peer(self, peer_endpoint: str):
        """Remove a seed peer."""
        self.seed_peers.discard(peer_endpoint)
    
    async def force_discovery_refresh(self):
        """Force immediate discovery refresh."""
        tasks = []
        
        if self.mdns_enabled:
            tasks.append(self._mdns_discover_local_peers())
        
        if self.dht_enabled:
            tasks.append(self._dht_refresh_routing_table())
        
        if self.gossip_enabled:
            tasks.append(self._gossip_peer_information())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)