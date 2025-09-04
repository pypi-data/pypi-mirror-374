"""
Peer-to-peer networking for distributed AI Ledger nodes.

Handles node discovery, validator coordination, and transaction broadcasting.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import aiohttp
from aiohttp import web
import socket
from urllib.parse import urlparse

from . import params

logger = logging.getLogger(__name__)


@dataclass
class PeerInfo:
    """Information about a peer node."""
    node_id: str
    host: str
    port: int
    last_seen: float
    validator_count: int = 0
    is_active: bool = True
    
    @property
    def endpoint(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class NetworkMessage:
    """P2P network message."""
    message_type: str
    sender_id: str
    data: dict
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NetworkMessage':
        return cls(**data)


class P2PNetwork:
    """Peer-to-peer network manager for AI Ledger nodes."""
    
    def __init__(self, node_id: str, port: int, bootstrap_nodes: List[str] = None):
        self.node_id = node_id
        self.port = port
        self.host = self._get_local_ip()
        
        # Peer management
        self.peers: Dict[str, PeerInfo] = {}
        self.bootstrap_nodes = bootstrap_nodes or []
        self.max_peers = 50
        
        # Network state
        self.is_running = False
        self.server = None
        self.session = None
        
        # Message handlers
        self.message_handlers = {
            'ping': self._handle_ping,
            'pong': self._handle_pong,
            'peer_discovery': self._handle_peer_discovery,
            'validator_announcement': self._handle_validator_announcement,
            'transaction_broadcast': self._handle_transaction_broadcast,
        }
        
        # Discovery
        self.discovery_interval = 30.0
        self.heartbeat_interval = 15.0
        self.peer_timeout = 60.0
    
    def _get_local_ip(self) -> str:
        """Get local IP address for peer communication."""
        try:
            # Connect to a remote address to get local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'
    
    async def start(self):
        """Start the P2P network."""
        if self.is_running:
            return
        
        logger.info(f"Starting P2P network on {self.host}:{self.port}")
        
        # Start HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5.0)
        )
        
        # Start background tasks
        asyncio.create_task(self._discovery_loop())
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._cleanup_loop())
        
        # Connect to bootstrap nodes
        if self.bootstrap_nodes:
            await self._connect_bootstrap_nodes()
        
        self.is_running = True
        logger.info(f"P2P network started with node ID {self.node_id[:8]}...")
    
    async def stop(self):
        """Stop the P2P network."""
        if not self.is_running:
            return
        
        logger.info("Stopping P2P network")
        self.is_running = False
        
        if self.session:
            await self.session.close()
        
        if self.server:
            await self.server.cleanup()
    
    async def _connect_bootstrap_nodes(self):
        """Connect to bootstrap nodes for initial peer discovery."""
        for bootstrap_node in self.bootstrap_nodes:
            try:
                await self._discover_peers_from_node(bootstrap_node)
            except Exception as e:
                logger.warning(f"Failed to connect to bootstrap node {bootstrap_node}: {e}")
    
    async def _discover_peers_from_node(self, node_endpoint: str):
        """Discover peers from a known node."""
        try:
            async with self.session.get(f"{node_endpoint}/p2p/peers") as resp:
                if resp.status == 200:
                    peers_data = await resp.json()
                    for peer_data in peers_data.get('peers', []):
                        await self._add_peer_from_data(peer_data)
        except Exception as e:
            logger.debug(f"Peer discovery from {node_endpoint} failed: {e}")
    
    async def _add_peer_from_data(self, peer_data: dict):
        """Add a peer from discovery data."""
        try:
            peer = PeerInfo(**peer_data)
            if peer.node_id != self.node_id and peer.node_id not in self.peers:
                # Verify peer is reachable
                if await self._ping_peer(peer):
                    self.peers[peer.node_id] = peer
                    logger.info(f"Added peer {peer.node_id[:8]}... at {peer.endpoint}")
        except Exception as e:
            logger.debug(f"Failed to add peer from data: {e}")
    
    async def _ping_peer(self, peer: PeerInfo) -> bool:
        """Ping a peer to verify connectivity."""
        try:
            message = NetworkMessage(
                message_type='ping',
                sender_id=self.node_id,
                data={'timestamp': time.time()}
            )
            
            async with self.session.post(
                f"{peer.endpoint}/p2p/message",
                json=message.to_dict()
            ) as resp:
                return resp.status == 200
        except Exception:
            return False
    
    async def broadcast_message(self, message_type: str, data: dict):
        """Broadcast a message to all connected peers."""
        message = NetworkMessage(
            message_type=message_type,
            sender_id=self.node_id,
            data=data
        )
        
        tasks = []
        for peer in list(self.peers.values()):
            if peer.is_active:
                task = self._send_message_to_peer(peer, message)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            logger.debug(f"Broadcast {message_type} to {success_count}/{len(tasks)} peers")
    
    async def _send_message_to_peer(self, peer: PeerInfo, message: NetworkMessage) -> bool:
        """Send a message to a specific peer."""
        try:
            async with self.session.post(
                f"{peer.endpoint}/p2p/message",
                json=message.to_dict()
            ) as resp:
                if resp.status == 200:
                    peer.last_seen = time.time()
                    return True
                else:
                    logger.warning(f"Failed to send message to {peer.node_id[:8]}: {resp.status}")
                    return False
        except Exception as e:
            logger.debug(f"Error sending message to {peer.node_id[:8]}: {e}")
            peer.is_active = False
            return False
    
    async def _discovery_loop(self):
        """Periodic peer discovery."""
        while self.is_running:
            try:
                # Discover peers from existing peers
                for peer in list(self.peers.values()):
                    if peer.is_active:
                        await self._discover_peers_from_node(peer.endpoint)
                
                await asyncio.sleep(self.discovery_interval)
            except Exception as e:
                logger.error(f"Discovery loop error: {e}")
                await asyncio.sleep(5)
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to maintain connections."""
        while self.is_running:
            try:
                tasks = []
                for peer in list(self.peers.values()):
                    if peer.is_active:
                        task = self._ping_peer(peer)
                        tasks.append((peer, task))
                
                if tasks:
                    results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
                    for (peer, _), result in zip(tasks, results):
                        if result is not True:
                            peer.is_active = False
                
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self):
        """Clean up inactive peers."""
        while self.is_running:
            try:
                current_time = time.time()
                inactive_peers = []
                
                for peer_id, peer in self.peers.items():
                    if current_time - peer.last_seen > self.peer_timeout:
                        inactive_peers.append(peer_id)
                
                for peer_id in inactive_peers:
                    del self.peers[peer_id]
                    logger.info(f"Removed inactive peer {peer_id[:8]}...")
                
                await asyncio.sleep(30)  # Cleanup every 30 seconds
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(5)
    
    # Message handlers
    async def _handle_ping(self, sender_peer: PeerInfo, data: dict):
        """Handle ping message."""
        # Update peer info
        sender_peer.last_seen = time.time()
        sender_peer.is_active = True
        
        # Send pong response
        pong_message = NetworkMessage(
            message_type='pong',
            sender_id=self.node_id,
            data={'timestamp': time.time(), 'original_timestamp': data.get('timestamp')}
        )
        
        await self._send_message_to_peer(sender_peer, pong_message)
    
    async def _handle_pong(self, sender_peer: PeerInfo, data: dict):
        """Handle pong message."""
        sender_peer.last_seen = time.time()
        sender_peer.is_active = True
    
    async def _handle_peer_discovery(self, sender_peer: PeerInfo, data: dict):
        """Handle peer discovery message."""
        # Add new peers from discovery data
        for peer_data in data.get('peers', []):
            await self._add_peer_from_data(peer_data)
    
    async def _handle_validator_announcement(self, sender_peer: PeerInfo, data: dict):
        """Handle validator announcement."""
        sender_peer.validator_count = data.get('validator_count', 0)
    
    async def _handle_transaction_broadcast(self, sender_peer: PeerInfo, data: dict):
        """Handle transaction broadcast from another node."""
        # This would integrate with the main transaction processing
        logger.info(f"Received transaction broadcast from {sender_peer.node_id[:8]}")
    
    def get_peer_stats(self) -> dict:
        """Get statistics about peer connections."""
        active_peers = [p for p in self.peers.values() if p.is_active]
        
        return {
            'node_id': self.node_id,
            'endpoint': f"{self.host}:{self.port}",
            'total_peers': len(self.peers),
            'active_peers': len(active_peers),
            'is_running': self.is_running,
            'peers': [p.to_dict() for p in active_peers[:10]]  # Show first 10
        }
    
    def get_all_peers(self) -> List[dict]:
        """Get all peer information for discovery."""
        return [p.to_dict() for p in self.peers.values() if p.is_active]


# Integration with FastAPI
def add_p2p_routes(app: web.Application, p2p_network: P2PNetwork):
    """Add P2P routes to FastAPI application."""
    
    @app.route('/p2p/peers', methods=['GET'])
    async def get_peers(request):
        """Get list of connected peers."""
        return web.json_response({
            'peers': p2p_network.get_all_peers(),
            'stats': p2p_network.get_peer_stats()
        })
    
    @app.route('/p2p/message', methods=['POST'])
    async def handle_message(request):
        """Handle incoming P2P message."""
        try:
            data = await request.json()
            message = NetworkMessage.from_dict(data)
            
            # Find or create sender peer
            sender_peer = p2p_network.peers.get(message.sender_id)
            if not sender_peer:
                # Create peer info from message
                sender_peer = PeerInfo(
                    node_id=message.sender_id,
                    host=request.remote,
                    port=8001,  # Default port
                    last_seen=time.time()
                )
                p2p_network.peers[message.sender_id] = sender_peer
            
            # Handle message
            handler = p2p_network.message_handlers.get(message.message_type)
            if handler:
                await handler(sender_peer, message.data)
            else:
                logger.warning(f"Unknown message type: {message.message_type}")
            
            return web.json_response({'status': 'ok'})
            
        except Exception as e:
            logger.error(f"Error handling P2P message: {e}")
            return web.json_response(
                {'error': str(e)}, 
                status=500
            )