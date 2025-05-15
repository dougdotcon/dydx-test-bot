"""
dYdX v4 API client using direct REST API calls.
"""
import logging
import requests
import time
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DydxApiClient:
    """
    Client for interacting with the dYdX v4 API.
    """

    def __init__(self, base_url: str = "https://dydx-testnet.imperator.co/v4"):
        """
        Initialize the dYdX API client.

        Args:
            base_url: Base URL for the dYdX API
                For testnet: "https://dydx-testnet.imperator.co/v4"
                For mainnet: "https://indexer.dydx.trade/v4"
        """
        self.base_url = base_url
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """
        Make a request to the dYdX API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            headers: Request headers

        Returns:
            Dict: Response data
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {"error": str(e)}

    def get_height(self) -> Dict:
        """
        Get the current block height and time.

        Returns:
            Dict: Height data with height and time
        """
        return self._make_request("GET", "height")

    def get_time(self) -> Dict:
        """
        Get the current server time.

        Returns:
            Dict: Time data with ISO and epoch time
        """
        return self._make_request("GET", "time")

    def get_markets(self) -> Dict:
        """
        Get all available perpetual markets.

        Returns:
            Dict: Markets data
        """
        return self._make_request("GET", "perpetualMarkets")

    def get_market(self, market_id: str) -> Dict:
        """
        Get information for a specific market.

        Args:
            market_id: Market ID (e.g., "ETH-USD")

        Returns:
            Dict: Market data
        """
        markets = self.get_markets()
        if "markets" in markets and market_id in markets["markets"]:
            return markets["markets"][market_id]
        return {"error": f"Market {market_id} not found"}

    def get_orderbook(self, market_id: str) -> Dict:
        """
        Get the orderbook for a specific market.

        Args:
            market_id: Market ID (e.g., "ETH-USD")

        Returns:
            Dict: Orderbook data
        """
        return self._make_request("GET", f"orderbook/{market_id}")

    def get_trades(self, market_id: str, limit: int = 100) -> Dict:
        """
        Get trades for a specific market.

        Args:
            market_id: Market ID (e.g., "ETH-USD")
            limit: Number of trades to return

        Returns:
            Dict: Trades data
        """
        params = {"limit": limit}
        return self._make_request("GET", f"trades/perpetualMarkets/{market_id}", params=params)

    def get_historical_funding(self, market_id: str, limit: int = 100) -> Dict:
        """
        Get historical funding rates for a specific market.

        Args:
            market_id: Market ID (e.g., "ETH-USD")
            limit: Number of funding rates to return

        Returns:
            Dict: Historical funding rates data
        """
        params = {"limit": limit}
        return self._make_request("GET", f"historicalFunding/{market_id}", params=params)

    def get_candles(self, market_id: str, resolution: str = "1MIN", limit: int = 100) -> Dict:
        """
        Get candles for a specific market.

        Args:
            market_id: Market ID (e.g., "ETH-USD")
            resolution: Candle resolution (e.g., "1MIN", "5MINS", "15MINS", "30MINS", "1HOUR", "4HOURS", "1DAY")
            limit: Number of candles to return

        Returns:
            Dict: Candles data
        """
        params = {
            "resolution": resolution,
            "limit": limit
        }
        return self._make_request("GET", f"candles/perpetualMarkets/{market_id}", params=params)
