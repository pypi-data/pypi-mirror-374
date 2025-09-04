"""
Distributed validator system for coordinating AI validators across network peers.

Each node contributes validators to a global pool, using their own API keys.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone
import aiohttp
from dataclasses import dataclass

from .validator import Validator, ValidatorOpinion
from .transaction import Transaction
from . import params

logger = logging.getLogger(__name__)


@dataclass
class RemoteValidator:
    """Information about a validator on a remote node."""
    validator_id: str
    node_id: str
    endpoint: str
    reputation: float = 1.0
    last_seen: float = 0
    is_active: bool = True


class DistributedValidatorPool:
    """Manages validators across the distributed network."""
    
    def __init__(self, node_id: str, local_validators: List[Validator] = None):
        self.node_id = node_id
        self.local_validators: Dict[str, Validator] = {}
        self.remote_validators: Dict[str, RemoteValidator] = {}
        
        # Add local validators
        if local_validators:
            for validator in local_validators:
                self.local_validators[validator.id] = validator
        
        # Networking
        self.session = None
        self.validator_timeout = 3.0
    
    async def start(self):
        """Start the distributed validator pool."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.validator_timeout)
        )
        logger.info(f"Started distributed validator pool with {len(self.local_validators)} local validators")
    
    async def stop(self):
        """Stop the distributed validator pool."""
        if self.session:
            await self.session.close()
    
    def add_local_validator(self, validator: Validator):
        """Add a local validator to the pool."""
        self.local_validators[validator.id] = validator
        logger.info(f"Added local validator {validator.id[:8]}...")
    
    def add_remote_validator(self, validator_id: str, node_id: str, endpoint: str):
        """Add a remote validator from network discovery."""
        if validator_id not in self.remote_validators:
            self.remote_validators[validator_id] = RemoteValidator(
                validator_id=validator_id,
                node_id=node_id,
                endpoint=endpoint,
                last_seen=time.time()
            )
            logger.info(f"Added remote validator {validator_id[:8]}... from node {node_id[:8]}...")
    
    def remove_remote_validator(self, validator_id: str):
        """Remove a remote validator."""
        if validator_id in self.remote_validators:
            del self.remote_validators[validator_id]
            logger.info(f"Removed remote validator {validator_id[:8]}...")
    
    async def collect_distributed_opinions(
        self, 
        tx: Transaction, 
        account_manager,
        required_count: int = None
    ) -> List[ValidatorOpinion]:
        """
        Collect validator opinions from across the distributed network.
        
        Args:
            tx: Transaction to validate
            account_manager: Local account manager for context
            required_count: Minimum number of opinions needed
            
        Returns:
            List of validator opinions
        """
        if required_count is None:
            required_count = params.QUORUM_K
        
        opinions = []
        
        # Collect from local validators
        local_tasks = []
        for validator in list(self.local_validators.values()):
            task = self._get_local_opinion(validator, tx, account_manager)
            local_tasks.append(task)
        
        # Collect from remote validators
        remote_tasks = []
        active_remote = [v for v in self.remote_validators.values() if v.is_active]
        
        # Limit remote validators to avoid overwhelming the network
        max_remote = min(len(active_remote), params.N_VALIDATORS - len(self.local_validators))
        
        for remote_validator in active_remote[:max_remote]:
            task = self._get_remote_opinion(remote_validator, tx)
            remote_tasks.append(task)
        
        # Execute all tasks concurrently
        all_tasks = local_tasks + remote_tasks
        if not all_tasks:
            logger.warning("No validators available for opinion collection")
            return opinions
        
        try:
            # Wait for opinions with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*all_tasks, return_exceptions=True),
                timeout=params.OPINION_TIMEOUT_SECS
            )
            
            # Process results
            for result in results:
                if isinstance(result, ValidatorOpinion):
                    opinions.append(result)
                elif isinstance(result, Exception):
                    logger.debug(f"Validator opinion failed: {result}")
        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout collecting validator opinions for tx {tx.id}")
        
        logger.info(f"Collected {len(opinions)} opinions from {len(all_tasks)} validators for tx {tx.id}")
        return opinions
    
    async def _get_local_opinion(
        self, 
        validator: Validator, 
        tx: Transaction, 
        account_manager
    ) -> Optional[ValidatorOpinion]:
        """Get opinion from a local validator."""
        try:
            return await validator.evaluate_transaction(tx, account_manager)
        except Exception as e:
            logger.error(f"Local validator {validator.id[:8]} failed: {e}")
            return None
    
    async def _get_remote_opinion(
        self, 
        remote_validator: RemoteValidator, 
        tx: Transaction
    ) -> Optional[ValidatorOpinion]:
        """Get opinion from a remote validator."""
        try:
            # Prepare validation request
            request_data = {
                'transaction': tx.dict(),
                'validator_id': remote_validator.validator_id,
                'timeout': self.validator_timeout
            }
            
            # Send request to remote node
            async with self.session.post(
                f"{remote_validator.endpoint}/validate",
                json=request_data
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    opinion = ValidatorOpinion(**data)
                    
                    # Update remote validator status
                    remote_validator.last_seen = time.time()
                    remote_validator.is_active = True
                    
                    return opinion
                else:
                    logger.warning(f"Remote validator {remote_validator.validator_id[:8]} returned {resp.status}")
                    remote_validator.is_active = False
                    return None
                    
        except asyncio.TimeoutError:
            logger.debug(f"Timeout getting opinion from remote validator {remote_validator.validator_id[:8]}")
            remote_validator.is_active = False
            return None
        except Exception as e:
            logger.debug(f"Error getting remote opinion: {e}")
            remote_validator.is_active = False
            return None
    
    def get_validator_stats(self) -> dict:
        """Get statistics about the validator pool."""
        active_remote = sum(1 for v in self.remote_validators.values() if v.is_active)
        
        return {
            'node_id': self.node_id,
            'local_validators': len(self.local_validators),
            'remote_validators': len(self.remote_validators),
            'active_remote_validators': active_remote,
            'total_validators': len(self.local_validators) + active_remote,
            'local_validator_ids': [v.id[:8] + '...' for v in self.local_validators.values()],
            'remote_nodes': list(set(v.node_id[:8] + '...' for v in self.remote_validators.values()))
        }
    
    def get_validator_announcement(self) -> dict:
        """Get validator announcement for network broadcast."""
        return {
            'node_id': self.node_id,
            'validator_count': len(self.local_validators),
            'validator_ids': list(self.local_validators.keys()),
            'timestamp': time.time()
        }
    
    async def announce_validators_to_network(self, p2p_network):
        """Announce local validators to the network."""
        announcement = self.get_validator_announcement()
        await p2p_network.broadcast_message('validator_announcement', announcement)
    
    def process_validator_announcement(self, announcement: dict, sender_endpoint: str):
        """Process a validator announcement from another node."""
        node_id = announcement.get('node_id')
        validator_ids = announcement.get('validator_ids', [])
        
        if node_id and node_id != self.node_id:
            # Add/update remote validators using actual sender endpoint
            for validator_id in validator_ids:
                self.add_remote_validator(validator_id, node_id, sender_endpoint)
    
    async def cleanup_inactive_validators(self):
        """Remove inactive remote validators."""
        current_time = time.time()
        inactive_validators = []
        
        for validator_id, validator in self.remote_validators.items():
            if current_time - validator.last_seen > 60.0:  # 60 second timeout
                inactive_validators.append(validator_id)
        
        for validator_id in inactive_validators:
            self.remove_remote_validator(validator_id)


class ValidatorCoordinator:
    """Coordinates validation requests across the distributed network."""
    
    def __init__(self, distributed_pool: DistributedValidatorPool):
        self.distributed_pool = distributed_pool
        self.pending_validations: Dict[str, asyncio.Future] = {}
    
    async def coordinate_validation(
        self, 
        tx: Transaction, 
        account_manager,
        p2p_network = None
    ) -> List[ValidatorOpinion]:
        """
        Coordinate distributed validation for a transaction.
        
        This is the main entry point for distributed consensus.
        """
        tx_id = tx.id
        
        # Check if validation is already in progress
        if tx_id in self.pending_validations:
            try:
                return await self.pending_validations[tx_id]
            except Exception as e:
                logger.error(f"Pending validation failed for {tx_id}: {e}")
                del self.pending_validations[tx_id]
        
        # Create future for this validation
        future = asyncio.get_event_loop().create_future()
        self.pending_validations[tx_id] = future
        
        try:
            # Broadcast transaction to network for validation
            if p2p_network:
                await p2p_network.broadcast_message('transaction_broadcast', {
                    'transaction': tx.dict(),
                    'requesting_node': self.distributed_pool.node_id,
                    'timestamp': time.time()
                })
            
            # Collect opinions from distributed validators
            opinions = await self.distributed_pool.collect_distributed_opinions(
                tx, account_manager
            )
            
            # Set result
            future.set_result(opinions)
            return opinions
            
        except Exception as e:
            logger.error(f"Validation coordination failed for {tx_id}: {e}")
            future.set_exception(e)
            raise
        finally:
            # Clean up pending validation
            if tx_id in self.pending_validations:
                del self.pending_validations[tx_id]