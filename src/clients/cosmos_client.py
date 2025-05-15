"""
Cosmos client for dYdX v4.
"""

import base64
import json
from typing import Dict, Optional, List
from .base_client import BaseClient

class DydxCosmosClient(BaseClient):
    """
    Cosmos client for dYdX v4.
    Handles Tendermint RPC and Cosmos SDK queries.
    """
    def __init__(self, config: Dict):
        """
        Initialize the Cosmos client.
        
        Args:
            config: Bot configuration dictionary
        """
        super().__init__(config)
        self.rest_endpoint = config['network']['endpoints']['rest'].rstrip('/')
        self.logger.info(f"Cosmos client initialized with endpoint: {self.rest_endpoint}")

    async def get_network_status(self) -> Optional[Dict]:
        """
        Get network status.
        
        Returns:
            Network status or None if error
        """
        url = f"{self.rest_endpoint}/status"
        return await self._make_request('GET', url)

    async def get_latest_block(self) -> Optional[Dict]:
        """
        Get latest block information.
        
        Returns:
            Block information or None if error
        """
        url = f"{self.rest_endpoint}/block"
        return await self._make_request('GET', url)

    async def get_block(self, height: Optional[int] = None) -> Optional[Dict]:
        """
        Get block information.
        
        Args:
            height: Block height (None for latest block)
            
        Returns:
            Block information or None if error
        """
        url = f"{self.rest_endpoint}/block"
        params = {}
        if height is not None:
            params['height'] = str(height)
        
        return await self._make_request('GET', url, params=params)

    async def get_market_data(self, market: str) -> Optional[Dict]:
        """
        Get market data using Cosmos SDK queries.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            
        Returns:
            Market data or None if error
        """
        try:
            # First get the current block height
            status = await self.get_network_status()
            if not status:
                return None
            
            height = status.get('sync_info', {}).get('latest_block_height')
            
            # Try different query paths
            modules = [
                ("clob", "orderbook"),           # Central Limit Order Book
                ("prices", "oracle"),            # Oracle prices
                ("perpetuals", "markets"),       # Perpetual markets
                ("stats", "markets"),            # Market statistics
            ]
            
            # Helper function to create store key
            def create_store_key(module: str, submodule: str, market_id: str) -> str:
                return f"{module}/{submodule}/{market_id}".encode()
            
            # Try each module
            for module, submodule in modules:
                store_key = create_store_key(module, submodule, market)
                encoded_key = base64.b64encode(store_key).decode()
                
                # Query using module store
                params = {
                    "path": f"/store/{module}/key",
                    "data": encoded_key,
                    "height": height,
                    "prove": "false"
                }
                
                self.logger.debug(f"Trying query in module {module}/{submodule}")
                url = f"{self.rest_endpoint}/abci_query"
                data = await self._make_request('GET', url, params=params)
                
                if data and data.get('response', {}).get('value'):
                    try:
                        decoded = base64.b64decode(data['response']['value'])
                        market_data = json.loads(decoded)
                        self.logger.debug(f"Data found in module {module}")
                        return market_data
                    except:
                        continue
            
            # If no module returned data, try chain state
            state_path = f"/dydxprotocol/{market.lower()}/state"
            params = {
                "path": state_path,
                "height": height,
                "prove": "false"
            }
            
            self.logger.debug(f"Trying state query: {state_path}")
            url = f"{self.rest_endpoint}/abci_query"
            state_data = await self._make_request('GET', url, params=params)
            
            if state_data and state_data.get('response', {}).get('value'):
                try:
                    decoded = base64.b64decode(state_data['response']['value'])
                    return json.loads(decoded)
                except:
                    pass
            
            # If still no data, try extracting from block
            block = await self.get_latest_block()
            if block:
                return self._extract_market_data_from_block(block, market)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return None

    def _extract_market_data_from_block(self, block_data: Dict, market: str) -> Optional[Dict]:
        """
        Extract market data from a block.
        
        Args:
            block_data: Block data
            market: Trading pair (e.g., 'ETH-USD')
            
        Returns:
            Market data or None if not found
        """
        try:
            # Look for transactions related to the market
            txs = block_data.get('block', {}).get('data', {}).get('txs', [])
            market_txs = []
            market_bytes = market.encode()
            
            for tx in txs:
                try:
                    tx_data = base64.b64decode(tx)
                    if market_bytes in tx_data:
                        market_txs.append(tx_data)
                except:
                    continue
            
            if market_txs:
                # Extract basic information
                block_time = block_data.get('block', {}).get('header', {}).get('time')
                height = block_data.get('block', {}).get('header', {}).get('height')
                
                # Try to find price data in transactions
                for tx_data in market_txs:
                    try:
                        # Look for known patterns in data
                        if b'"price"' in tx_data and b'"market"' in tx_data:
                            decoded = json.loads(tx_data.decode())
                            if 'price' in decoded:
                                return {
                                    'market': market,
                                    'price': decoded['price'],
                                    'last_update': block_time,
                                    'height': height
                                }
                    except:
                        continue
                
                # If no price found, return basic data
                return {
                    'market': market,
                    'transactions': len(market_txs),
                    'last_update': block_time,
                    'height': height
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting data from block: {e}")
            return None
