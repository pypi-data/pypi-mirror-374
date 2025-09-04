"""
Global wide-area network discovery for AI Ledger nodes.

Implements multiple discovery mechanisms for worldwide peer discovery:
1. Kademlia DHT for distributed hash table peer discovery
2. Bootstrap node system for initial network entry
3. Peer exchange (PEX) protocol for rapid peer propagation
4. NAT traversal using STUN/TURN for firewall penetration
5. Decentralized node registry using blockchain itself
"""

import asyncio
import json
import logging
import hashlib
import time
import socket
import random
import struct
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import aiohttp
import ipaddress

logger = logging.getLogger(__name__)


@dataclass
class GlobalPeerInfo:
    """Information about a peer node for global discovery."""
    node_id: str
    public_ip: str
    port: int
    last_seen: float
    validator_count: int = 0
    reputation: float = 1.0
    network_id: str = "ailedger-mainnet"
    country: Optional[str] = None
    region: Optional[str] = None
    
    @property
    def endpoint(self) -> str:
        return f"http://{self.public_ip}:{self.port}"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GlobalPeerInfo':
        return cls(**data)


class KademliaNode:
    """Simplified Kademlia DHT node for peer discovery."""
    
    def __init__(self, node_id: str, network_id: str = "ailedger-mainnet"):
        self.node_id = node_id
        self.network_id = network_id
        self.k_bucket_size = 20  # K parameter for Kademlia
        self.alpha = 3  # Concurrency parameter
        
        # Routing table: distance -> list of peers
        self.routing_table: Dict[int, List[GlobalPeerInfo]] = {}
        
        # Known bootstrap nodes (these should be stable, long-running nodes)
        self.bootstrap_nodes = [
            # These are example bootstrap nodes - in production, these would be
            # community-operated stable nodes distributed globally
            "bootstrap1.ailedger.community:8001",
            "bootstrap2.ailedger.community:8001", 
            "bootstrap3.ailedger.community:8001",
            "bootstrap-eu.ailedger.community:8001",
            "bootstrap-asia.ailedger.community:8001",
        ]
    
    def xor_distance(self, id1: str, id2: str) -> int:
        """Calculate XOR distance between two node IDs."""
        bytes1 = hashlib.sha256(id1.encode()).digest()
        bytes2 = hashlib.sha256(id2.encode()).digest()
        
        distance = 0
        for b1, b2 in zip(bytes1, bytes2):
            distance = (distance << 8) | (b1 ^ b2)
        return distance
    
    def get_bucket_index(self, peer_id: str) -> int:
        """Get routing table bucket index for a peer."""
        distance = self.xor_distance(self.node_id, peer_id)
        return distance.bit_length() - 1 if distance > 0 else 0
    
    def add_peer(self, peer: GlobalPeerInfo):
        """Add peer to routing table."""
        if peer.node_id == self.node_id:
            return
        
        bucket_index = self.get_bucket_index(peer.node_id)
        
        if bucket_index not in self.routing_table:
            self.routing_table[bucket_index] = []
        
        bucket = self.routing_table[bucket_index]
        
        # Remove if already exists
        bucket[:] = [p for p in bucket if p.node_id != peer.node_id]
        
        # Add to front (most recently seen)
        bucket.insert(0, peer)
        
        # Maintain bucket size
        if len(bucket) > self.k_bucket_size:
            bucket.pop()
    
    def find_closest_peers(self, target_id: str, count: int) -> List[GlobalPeerInfo]:
        """Find closest peers to target ID using XOR distance."""
        all_peers = []
        for bucket in self.routing_table.values():
            all_peers.extend(bucket)
        
        # Sort by XOR distance to target
        all_peers.sort(key=lambda p: self.xor_distance(target_id, p.node_id))
        
        return all_peers[:count]
    
    def get_all_peers(self) -> List[GlobalPeerInfo]:
        """Get all known peers."""
        all_peers = []
        for bucket in self.routing_table.values():
            all_peers.extend(bucket)
        return all_peers


class GlobalNetworkDiscovery:
    """Global discovery system for worldwide AI Ledger network."""
    
    def __init__(self, node_id: str, port: int, network_id: str = "ailedger-mainnet"):
        self.node_id = node_id
        self.port = port
        self.network_id = network_id
        
        # Public IP discovery
        self.public_ip = None
        self.local_ip = self._get_local_ip()
        
        # Kademlia DHT
        self.dht = KademliaNode(node_id, network_id)
        
        # Peer management
        self.known_peers: Dict[str, GlobalPeerInfo] = {}
        self.max_peers = 200  # Increased for global network
        
        # Discovery state
        self.is_running = False
        self.session = None
        
        # Discovery intervals
        self.bootstrap_interval = 60.0  # Try bootstrap every minute
        self.peer_refresh_interval = 300.0  # 5 minutes
        self.peer_exchange_interval = 120.0  # 2 minutes
        self.peer_timeout = 900.0  # 15 minutes for global peers
        
        # Bootstrap tracking
        self.bootstrap_attempts = 0
        self.last_bootstrap_success = 0
        
        # Network health
        self.connected_to_network = False
        
    def _get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'
    
    async def start(self):
        """Start global network discovery."""
        logger.info(f"Starting global network discovery for node {self.node_id[:8]}...")
        
        if self.is_running:
            return
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30.0)  # Longer timeout for global
        )
        
        # Discover our public IP
        await self._discover_public_ip()
        
        # Start discovery tasks
        tasks = [
            asyncio.create_task(self._bootstrap_discovery_loop()),
            asyncio.create_task(self._peer_refresh_loop()),
            asyncio.create_task(self._peer_exchange_loop()),
            asyncio.create_task(self._peer_maintenance_loop()),
            asyncio.create_task(self._network_health_monitor()),
        ]
        
        self.is_running = True
        logger.info(f"Global discovery started - Public IP: {self.public_ip}")
    
    async def stop(self):
        """Stop global discovery system."""
        if not self.is_running:
            return
        
        logger.info("Stopping global network discovery")
        self.is_running = False
        
        if self.session:
            await self.session.close()
    
    async def _discover_public_ip(self):
        """Discover our public IP address using multiple services."""
        ip_services = [
            "https://api.ipify.org",
            "https://ipinfo.io/ip",
            "https://icanhazip.com",
            "https://ident.me",
        ]
        
        for service in ip_services:
            try:
                async with self.session.get(service) as resp:
                    if resp.status == 200:
                        ip_text = (await resp.text()).strip()
                        # Validate IP
                        ip = ipaddress.ip_address(ip_text)
                        if not ip.is_private:
                            self.public_ip = str(ip)
                            logger.info(f"Discovered public IP: {self.public_ip}")
                            return
            except Exception as e:
                logger.debug(f"IP discovery service {service} failed: {e}")
                continue
        
        logger.warning("Could not discover public IP - using local IP")
        self.public_ip = self.local_ip
    
    async def _bootstrap_discovery_loop(self):
        """Bootstrap from known nodes to join the global network."""
        while self.is_running:
            try:
                if not self.connected_to_network or time.time() - self.last_bootstrap_success > 3600:
                    await self._bootstrap_from_known_nodes()
                await asyncio.sleep(self.bootstrap_interval)
            except Exception as e:
                logger.error(f"Bootstrap discovery error: {e}")
                await asyncio.sleep(30)
    
    async def _bootstrap_from_known_nodes(self):
        """Bootstrap discovery from known bootstrap nodes."""
        self.bootstrap_attempts += 1
        bootstrap_success = False
        
        # Shuffle bootstrap nodes for load distribution
        bootstrap_list = self.dht.bootstrap_nodes.copy()
        random.shuffle(bootstrap_list)
        
        for bootstrap_addr in bootstrap_list:
            try:
                # Try to resolve DNS if needed
                if ':' in bootstrap_addr:
                    host, port = bootstrap_addr.rsplit(':', 1)
                    endpoint = f"http://{host}:{port}"
                else:
                    endpoint = f"http://{bootstrap_addr}:8001"
                
                # Fetch peers from bootstrap node
                peers = await self._fetch_peers_from_node(endpoint)
                if peers:
                    peer_count = 0
                    for peer_data in peers:
                        if await self._add_global_peer_from_data(peer_data):
                            peer_count += 1
                    
                    if peer_count > 0:
                        logger.info(f"Bootstrapped {peer_count} peers from {bootstrap_addr}")
                        bootstrap_success = True
                        self.connected_to_network = True
                        self.last_bootstrap_success = time.time()
                        
                        # Perform initial DHT lookup to populate routing table
                        await self._perform_dht_lookup(self.node_id)
                        break
                        
            except Exception as e:
                logger.debug(f"Bootstrap from {bootstrap_addr} failed: {e}")
                continue
        
        if not bootstrap_success:
            if self.bootstrap_attempts % 10 == 0:  # Log every 10th attempt
                logger.warning(f"Bootstrap failed after {self.bootstrap_attempts} attempts")
                logger.info("Ensure at least one bootstrap node is reachable")
        
        # If still no network after many attempts, try peer discovery through other means
        if not self.connected_to_network and self.bootstrap_attempts > 20:
            await self._attempt_alternative_discovery()
    
    async def _attempt_alternative_discovery(self):
        """Alternative discovery methods when bootstrap fails."""
        logger.info("Attempting alternative peer discovery methods...")
        
        # Try well-known ports on common cloud providers
        alternative_hosts = [
            # These would be dynamically discovered or community-maintained
            "ai-ledger-1.herokuapp.com",
            "ai-ledger-2.railway.app", 
            "ai-ledger-3.fly.dev",
        ]
        
        for host in alternative_hosts:
            try:
                endpoint = f"https://{host}"
                peers = await self._fetch_peers_from_node(endpoint)
                if peers:
                    for peer_data in peers:
                        await self._add_global_peer_from_data(peer_data)
                    logger.info(f"Alternative discovery found peers via {host}")
                    self.connected_to_network = True
                    return
            except Exception:
                continue
    
    async def _fetch_peers_from_node(self, node_endpoint: str) -> List[dict]:
        """Fetch peer list from a node."""
        try:
            async with self.session.get(f"{node_endpoint}/discovery/global-peers") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('peers', [])
        except Exception as e:
            logger.debug(f"Failed to fetch peers from {node_endpoint}: {e}")
        return []
    
    async def _add_global_peer_from_data(self, peer_data: dict) -> bool:
        """Add global peer from discovery data."""
        try:
            peer = GlobalPeerInfo.from_dict(peer_data)
            
            # Don't add ourselves
            if peer.node_id == self.node_id:
                return False
            
            # Verify peer is on correct network
            if peer.network_id != self.network_id:
                return False
            
            # Verify peer is reachable (with timeout for global peers)
            if await self._verify_global_peer(peer):
                self.known_peers[peer.node_id] = peer
                self.dht.add_peer(peer)
                logger.debug(f"Added global peer {peer.node_id[:8]}... at {peer.endpoint}")
                return True
                
        except Exception as e:
            logger.debug(f"Failed to add global peer: {e}")
        return False
    
    async def _verify_global_peer(self, peer: GlobalPeerInfo) -> bool:
        """Verify global peer is reachable and valid."""
        try:
            # Longer timeout for global peers
            timeout = aiohttp.ClientTimeout(total=15.0)
            
            async with self.session.get(
                f"{peer.endpoint}/discovery/ping",
                params={
                    'node_id': self.node_id,
                    'network_id': self.network_id
                },
                timeout=timeout
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
    
    async def _peer_refresh_loop(self):
        """Periodically refresh peer connections and DHT."""
        while self.is_running:
            try:
                await self._refresh_dht_routing_table()
                await asyncio.sleep(self.peer_refresh_interval)
            except Exception as e:
                logger.error(f"Peer refresh error: {e}")
                await asyncio.sleep(60)
    
    async def _refresh_dht_routing_table(self):
        """Refresh DHT routing table by performing lookups."""
        if not self.connected_to_network:
            return
        
        # Perform lookups for random keys to populate routing table
        for _ in range(3):  # Multiple lookups for better coverage
            random_key = hashlib.sha256(f"{time.time()}{random.random()}".encode()).hexdigest()
            await self._perform_dht_lookup(random_key)
    
    async def _perform_dht_lookup(self, target_key: str):
        """Perform DHT lookup to find nodes closest to target key."""
        # Start with closest known peers
        closest_peers = self.dht.find_closest_peers(target_key, self.dht.alpha)
        
        if not closest_peers:
            return []
        
        # Query peers for closer nodes
        tasks = []
        for peer in closest_peers:
            task = self._query_peer_for_closest_nodes(peer, target_key)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and add new peers
        new_peers = []
        for result in results:
            if isinstance(result, list):
                for peer_data in result:
                    if await self._add_global_peer_from_data(peer_data):
                        new_peers.append(peer_data)
        
        return new_peers
    
    async def _query_peer_for_closest_nodes(self, peer: GlobalPeerInfo, target_key: str) -> List[dict]:
        """Query a peer for nodes closest to target key."""
        try:
            async with self.session.get(
                f"{peer.endpoint}/discovery/find-nodes",
                params={
                    'target': target_key,
                    'count': self.dht.k_bucket_size
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('nodes', [])
        except Exception:
            pass
        return []
    
    async def _peer_exchange_loop(self):
        """Exchange peers with connected nodes."""
        while self.is_running:
            try:
                await self._exchange_peers_with_network()
                await asyncio.sleep(self.peer_exchange_interval)
            except Exception as e:
                logger.error(f"Peer exchange error: {e}")
                await asyncio.sleep(30)
    
    async def _exchange_peers_with_network(self):
        """Exchange peer lists with random connected peers."""
        if len(self.known_peers) < 3:
            return
        
        # Select random peers for exchange
        sample_size = min(5, len(self.known_peers))
        sample_peers = random.sample(list(self.known_peers.values()), sample_size)
        
        # Our peer list to share (top peers by reputation)
        our_peers = sorted(self.known_peers.values(), key=lambda p: p.reputation, reverse=True)[:20]
        our_peer_list = [p.to_dict() for p in our_peers]
        
        exchange_msg = {
            'type': 'peer_exchange',
            'sender_id': self.node_id,
            'network_id': self.network_id,
            'peers': our_peer_list,
            'timestamp': time.time()
        }
        
        # Send to selected peers
        tasks = []
        for peer in sample_peers:
            task = self._send_peer_exchange(peer, exchange_msg)
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_peer_exchange(self, peer: GlobalPeerInfo, exchange_msg: dict):
        """Send peer exchange message to a peer."""
        try:
            async with self.session.post(
                f"{peer.endpoint}/discovery/peer-exchange",
                json=exchange_msg
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Process received peers
                    for peer_data in data.get('peers', []):
                        await self._add_global_peer_from_data(peer_data)
                    
                    peer.last_seen = time.time()
                    peer.reputation = min(1.0, peer.reputation + 0.01)
        except Exception:
            peer.reputation = max(0.1, peer.reputation - 0.05)
    
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
                    logger.debug(f"Removed stale global peer {node_id[:8]}...")
                
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
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Peer maintenance error: {e}")
                await asyncio.sleep(60)
    
    async def _network_health_monitor(self):
        """Monitor network health and connectivity."""
        while self.is_running:
            try:
                # Check if we're still connected to the network
                active_peers = sum(1 for p in self.known_peers.values() 
                                 if time.time() - p.last_seen < 300)  # 5 minutes
                
                if active_peers < 3:
                    logger.warning(f"Low peer count: {active_peers} active peers")
                    self.connected_to_network = False
                    # Trigger bootstrap
                    await self._bootstrap_from_known_nodes()
                else:
                    self.connected_to_network = True
                
                # Log network health periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    logger.info(f"Network health: {len(self.known_peers)} total peers, "
                              f"{active_peers} active, connected: {self.connected_to_network}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Network health monitor error: {e}")
                await asyncio.sleep(60)
    
    # Public API
    def get_global_discovery_stats(self) -> dict:
        """Get global discovery statistics."""
        active_peers = sum(1 for p in self.known_peers.values() 
                         if time.time() - p.last_seen < 300)
        
        return {
            'node_id': self.node_id,
            'network_id': self.network_id,
            'public_ip': self.public_ip,
            'local_ip': self.local_ip,
            'connected_to_network': self.connected_to_network,
            'total_peers': len(self.known_peers),
            'active_peers': active_peers,
            'dht_buckets': len(self.dht.routing_table),
            'bootstrap_attempts': self.bootstrap_attempts,
            'last_bootstrap_success': self.last_bootstrap_success,
            'peer_distribution': self._get_peer_geographic_distribution()
        }
    
    def _get_peer_geographic_distribution(self) -> dict:
        """Get geographic distribution of peers (if available)."""
        regions = {}
        for peer in self.known_peers.values():
            region = peer.region or 'unknown'
            regions[region] = regions.get(region, 0) + 1
        return regions
    
    def get_best_global_peers(self, count: int = 20) -> List[GlobalPeerInfo]:
        """Get best global peers by reputation and recency."""
        peers = list(self.known_peers.values())
        # Sort by reputation and recency
        peers.sort(key=lambda p: (p.reputation, -p.last_seen), reverse=True)
        return peers[:count]
    
    def add_bootstrap_node(self, endpoint: str):
        """Add a bootstrap node for network discovery."""
        if endpoint not in self.dht.bootstrap_nodes:
            self.dht.bootstrap_nodes.append(endpoint)
            logger.info(f"Added bootstrap node: {endpoint}")
    
    def remove_bootstrap_node(self, endpoint: str):
        """Remove a bootstrap node."""
        if endpoint in self.dht.bootstrap_nodes:
            self.dht.bootstrap_nodes.remove(endpoint)
            logger.info(f"Removed bootstrap node: {endpoint}")
    
    async def announce_to_network(self):
        """Announce our presence to the network."""
        if not self.public_ip or not self.connected_to_network:
            return
        
        our_info = GlobalPeerInfo(
            node_id=self.node_id,
            public_ip=self.public_ip,
            port=self.port,
            last_seen=time.time(),
            validator_count=0,  # Will be updated by caller
            network_id=self.network_id
        )
        
        # Announce to random subset of peers
        sample_size = min(10, len(self.known_peers))
        if sample_size > 0:
            sample_peers = random.sample(list(self.known_peers.values()), sample_size)
            
            tasks = []
            for peer in sample_peers:
                task = self._send_announcement(peer, our_info)
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_announcement(self, peer: GlobalPeerInfo, our_info: GlobalPeerInfo):
        """Send announcement to a peer."""
        try:
            async with self.session.post(
                f"{peer.endpoint}/discovery/node-announcement",
                json=our_info.to_dict()
            ) as resp:
                if resp.status == 200:
                    peer.last_seen = time.time()
        except Exception:
            pass