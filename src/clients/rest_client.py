"""
REST API client for dYdX v4.
"""

from typing import Dict, Optional, List
from .base_client import BaseClient

class DydxRestClient(BaseClient):
    """
    REST API client for dYdX v4.
    Handles all REST API interactions.
    """
    def __init__(self, config: Dict):
        """
        Initialize the REST client.
        
        Args:
            config: Bot configuration dictionary
        """
        super().__init__(config)
        self.rest_endpoint = config['network']['endpoints']['rest'].rstrip('/')
        self.logger.info(f"REST client initialized with endpoint: {self.rest_endpoint}")

    async def get_market_data(self, market: str) -> Optional[Dict]:
        """
        Get market data for the specified market.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            
        Returns:
            Market data or None if error
        """
        url = f"{self.rest_endpoint}/perpetual/markets"
        data = await self._make_request('GET', url)
        
        if data and 'markets' in data:
            return data['markets'].get(market)
        return None

    async def get_orderbook(self, market: str) -> Optional[Dict]:
        """
        Get orderbook for the specified market.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            
        Returns:
            Orderbook data or None if error
        """
        url = f"{self.rest_endpoint}/perpetual/markets/{market}/orderbook"
        data = await self._make_request('GET', url)
        
        if data:
            return data.get('orderbook')
        return None

    async def get_trades(self, market: str, limit: int = 100) -> Optional[List]:
        """
        Get recent trades for the specified market.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            limit: Maximum number of trades to return
            
        Returns:
            List of trades or None if error
        """
        url = f"{self.rest_endpoint}/perpetual/markets/{market}/trades"
        params = {'limit': limit}
        data = await self._make_request('GET', url, params=params)
        
        if data:
            return data.get('trades', [])
        return None

    async def place_order(self, order_params: Dict) -> Optional[Dict]:
        """
        Place an order.
        
        Args:
            order_params: Order parameters
            
        Returns:
            Order response or None if error
        """
        url = f"{self.rest_endpoint}/perpetual/orders"
        return await self._make_request('POST', url, data=order_params)

    async def get_account_info(self) -> Optional[Dict]:
        """
        Get account information.
        
        Returns:
            Account information or None if error
        """
        url = f"{self.rest_endpoint}/perpetual/account"
        return await self._make_request('GET', url)

    async def get_positions(self) -> Optional[List]:
        """
        Get open positions.
        
        Returns:
            List of positions or None if error
        """
        url = f"{self.rest_endpoint}/perpetual/positions"
        data = await self._make_request('GET', url)
        
        if data:
            return data.get('positions', [])
        return None

    async def get_position(self, market: str) -> Optional[Dict]:
        """
        Get position for the specified market.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            
        Returns:
            Position data or None if error
        """
        positions = await self.get_positions()
        if positions:
            for position in positions:
                if position.get('market') == market:
                    return position
        return None
