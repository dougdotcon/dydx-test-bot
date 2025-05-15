"""
Market data module for the trading bot.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from ..clients.rest_client import DydxRestClient
from ..clients.websocket_client import DydxWebSocketClient
from ..models.market import MarketData, Trade, OrderBook
from ..utils.helpers import calculate_resistance, calculate_volume_anomaly

class MarketDataService:
    """
    Service for collecting and analyzing market data.
    """
    def __init__(self, config: Dict):
        """
        Initialize the market data service.
        
        Args:
            config: Bot configuration
        """
        self.config = config
        self.market = config['trading']['market']
        self.timeframe = config['trading']['timeframe']
        self.volume_lookback = config['technical']['volume_lookback']
        self.polling_interval = 5  # seconds
        
        # Cache of data
        self.prices: List[float] = []
        self.volumes: List[float] = []
        self.timestamps: List[datetime] = []
        
        # Market data model
        self.market_data = MarketData(market=self.market)
        
        # Clients
        self.rest_client = DydxRestClient(config)
        self.ws_client = DydxWebSocketClient(config)
        
        # Control
        self.running = False
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        """Connect to API and initialize data."""
        try:
            # Connect to REST API
            await self.rest_client.connect()
            
            # Connect to WebSocket
            await self.ws_client.connect()
            
            # Register WebSocket callbacks
            self.ws_client.on_message('trades', self._handle_trades_message)
            self.ws_client.on_message('orderbook', self._handle_orderbook_message)
            self.ws_client.on_message('markets', self._handle_markets_message)
            
            # Subscribe to channels
            await self.ws_client.subscribe('trades', self.market)
            await self.ws_client.subscribe('orderbook', self.market)
            await self.ws_client.subscribe('markets', self.market)
            
            # Load initial data
            await self._load_initial_data()
            
            self.running = True
            self.logger.info(f"Connected to dYdX API for {self.market}")
            
        except Exception as e:
            self.logger.error(f"Error connecting to API: {e}")
            raise
    
    async def _load_initial_data(self):
        """Load initial historical data."""
        try:
            # Get market data
            market_data = await self.rest_client.get_market_data(self.market)
            if market_data:
                self.market_data = MarketData.from_api(self.market, market_data)
                self.logger.info(f"Loaded market data for {self.market}")
            
            # Get recent trades
            trades = await self.rest_client.get_trades(self.market, limit=100)
            if trades:
                self.market_data.update_trades(trades)
                
                # Extract price and volume data
                for trade in trades:
                    price = float(trade.get('price', 0))
                    size = float(trade.get('size', 0))
                    created_at = trade.get('createdAt', '')
                    if created_at:
                        timestamp = datetime.fromisoformat(
                            created_at.replace('Z', '+00:00')
                        )
                    else:
                        timestamp = datetime.now()
                    
                    self.prices.append(price)
                    self.volumes.append(size * price)  # Volume in USD
                    self.timestamps.append(timestamp)
                
                self.logger.info(f"Loaded {len(trades)} historical trades")
            
            # Get orderbook
            orderbook = await self.rest_client.get_orderbook(self.market)
            if orderbook:
                self.market_data.update_orderbook(orderbook)
                self.logger.info(f"Loaded orderbook for {self.market}")
            
        except Exception as e:
            self.logger.error(f"Error loading initial data: {e}")
    
    async def _handle_trades_message(self, message: Dict):
        """
        Handle trades WebSocket message.
        
        Args:
            message: WebSocket message
        """
        try:
            trades_data = message.get('contents', {}).get('trades', [])
            if trades_data:
                self.market_data.update_trades(trades_data)
                
                # Update price and volume data
                for trade in trades_data:
                    price = float(trade.get('price', 0))
                    size = float(trade.get('size', 0))
                    created_at = trade.get('createdAt', '')
                    if created_at:
                        timestamp = datetime.fromisoformat(
                            created_at.replace('Z', '+00:00')
                        )
                    else:
                        timestamp = datetime.now()
                    
                    self.prices.append(price)
                    self.volumes.append(size * price)  # Volume in USD
                    self.timestamps.append(timestamp)
                
                # Maintain data within lookback period
                cutoff = datetime.now() - timedelta(minutes=self.volume_lookback)
                while self.timestamps and self.timestamps[0] < cutoff:
                    self.prices.pop(0)
                    self.volumes.pop(0)
                    self.timestamps.pop(0)
                
                self.logger.debug(f"Processed {len(trades_data)} new trades")
        except Exception as e:
            self.logger.error(f"Error handling trades message: {e}")
    
    async def _handle_orderbook_message(self, message: Dict):
        """
        Handle orderbook WebSocket message.
        
        Args:
            message: WebSocket message
        """
        try:
            orderbook_data = message.get('contents', {}).get('orderbook')
            if orderbook_data:
                self.market_data.update_orderbook(orderbook_data)
                self.logger.debug("Processed orderbook update")
        except Exception as e:
            self.logger.error(f"Error handling orderbook message: {e}")
    
    async def _handle_markets_message(self, message: Dict):
        """
        Handle markets WebSocket message.
        
        Args:
            message: WebSocket message
        """
        try:
            market_data = message.get('contents', {}).get('markets', {}).get(self.market)
            if market_data:
                self.market_data = MarketData.from_api(self.market, market_data)
                self.logger.debug("Processed market update")
        except Exception as e:
            self.logger.error(f"Error handling markets message: {e}")
    
    async def _update_market_data(self):
        """Update market data via REST API (fallback)."""
        try:
            # Only update if WebSocket is not working
            if not self.ws_client.running:
                market_data = await self.rest_client.get_market_data(self.market)
                if market_data:
                    self.market_data = MarketData.from_api(self.market, market_data)
                
                trades = await self.rest_client.get_trades(self.market, limit=10)
                if trades:
                    self.market_data.update_trades(trades)
                    
                    # Update price and volume data
                    for trade in trades:
                        price = float(trade.get('price', 0))
                        size = float(trade.get('size', 0))
                        
                        self.prices.append(price)
                        self.volumes.append(size * price)  # Volume in USD
                        self.timestamps.append(datetime.now())
                    
                    # Maintain data within lookback period
                    cutoff = datetime.now() - timedelta(minutes=self.volume_lookback)
                    while self.timestamps and self.timestamps[0] < cutoff:
                        self.prices.pop(0)
                        self.volumes.pop(0)
                        self.timestamps.pop(0)
                
                orderbook = await self.rest_client.get_orderbook(self.market)
                if orderbook:
                    self.market_data.update_orderbook(orderbook)
                
                self.logger.debug("Updated market data via REST API")
        except Exception as e:
            self.logger.error(f"Error updating market data: {e}")
    
    async def listen(self):
        """Listen for market data updates."""
        try:
            # Start WebSocket listener
            ws_task = asyncio.create_task(self.ws_client.listen())
            
            # Start REST polling as fallback
            while self.running:
                await self._update_market_data()
                await asyncio.sleep(self.polling_interval)
                
        except asyncio.CancelledError:
            self.logger.info("Market data listener cancelled")
        except Exception as e:
            self.logger.error(f"Error in market data listener: {e}")
            raise
        finally:
            if 'ws_task' in locals() and not ws_task.done():
                ws_task.cancel()
    
    def get_current_price(self) -> Optional[float]:
        """
        Get current price.
        
        Returns:
            Current price or None if not available
        """
        return self.market_data.get_current_price()
    
    def calculate_volume_anomaly(self) -> Optional[float]:
        """
        Calculate volume anomaly.
        
        Returns:
            Volume anomaly ratio or None if not enough data
        """
        return calculate_volume_anomaly(self.volumes)
    
    def calculate_resistance(self) -> Optional[float]:
        """
        Calculate resistance level.
        
        Returns:
            Resistance level or None if not enough data
        """
        return calculate_resistance(
            self.prices,
            self.config['technical']['resistance_period']
        )
    
    def get_market_data_for_analysis(self) -> Dict:
        """
        Get market data for strategy analysis.
        
        Returns:
            Market data dictionary
        """
        return {
            'prices': self.prices,
            'volumes': self.volumes,
            'timestamps': self.timestamps,
            'current_price': self.get_current_price(),
            'orderbook': self.market_data.orderbook,
            'trades': self.market_data.trades
        }
    
    async def close(self):
        """Close connections."""
        self.running = False
        await self.rest_client.close()
        await self.ws_client.close()
        self.logger.info("Market data service stopped")
    
    async def __aenter__(self):
        """Support for async context manager."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support for async context manager."""
        await self.close()
