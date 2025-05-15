"""
WebSocket client for dYdX v4.
"""

import asyncio
import json
import logging
import ssl
import certifi
import websockets
from typing import Dict, Optional, List, Callable, Any
from datetime import datetime

class DydxWebSocketClient:
    """
    WebSocket client for dYdX v4.
    Handles real-time data streaming.
    """
    def __init__(self, config: Dict):
        """
        Initialize the WebSocket client.
        
        Args:
            config: Bot configuration dictionary
        """
        self.config = config
        self.ws_endpoint = config['network']['endpoints']['ws']
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # SSL Configuration
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        if config.get('debug', {}).get('ssl_verify') is False:
            self.logger.warning("SSL verification disabled. This is not recommended for production.")
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # WebSocket state
        self.ws = None
        self.running = False
        self.reconnect_interval = 5  # seconds
        self.ping_interval = 30  # seconds
        self.last_ping_time = None
        
        # Subscriptions and callbacks
        self.subscriptions = {}
        self.message_callbacks = {}
        self.connection_callbacks = {
            'connect': [],
            'disconnect': []
        }

    async def connect(self):
        """Connect to WebSocket server."""
        if self.ws is not None:
            return
        
        try:
            self.ws = await websockets.connect(
                self.ws_endpoint,
                ssl=self.ssl_context
            )
            self.running = True
            self.last_ping_time = datetime.now()
            self.logger.info(f"Connected to WebSocket: {self.ws_endpoint}")
            
            # Notify connection callbacks
            for callback in self.connection_callbacks['connect']:
                try:
                    await callback()
                except Exception as e:
                    self.logger.error(f"Error in connect callback: {e}")
            
            # Resubscribe to channels
            await self._resubscribe()
            
            # Start ping task
            asyncio.create_task(self._ping_loop())
            
        except Exception as e:
            self.logger.error(f"WebSocket connection error: {e}")
            self.ws = None
            raise

    async def close(self):
        """Close WebSocket connection."""
        self.running = False
        if self.ws:
            try:
                await self.ws.close()
                self.logger.info("WebSocket connection closed")
                
                # Notify disconnect callbacks
                for callback in self.connection_callbacks['disconnect']:
                    try:
                        await callback()
                    except Exception as e:
                        self.logger.error(f"Error in disconnect callback: {e}")
                        
            except Exception as e:
                self.logger.error(f"Error closing WebSocket: {e}")
            finally:
                self.ws = None

    async def _ping_loop(self):
        """Send periodic pings to keep connection alive."""
        while self.running and self.ws:
            try:
                now = datetime.now()
                if (now - self.last_ping_time).total_seconds() >= self.ping_interval:
                    await self.ws.ping()
                    self.last_ping_time = now
                    self.logger.debug("Ping sent")
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Ping error: {e}")
                await self._handle_disconnect()
                break

    async def _handle_disconnect(self):
        """Handle WebSocket disconnection."""
        if not self.running:
            return
            
        await self.close()
        self.logger.info(f"Reconnecting in {self.reconnect_interval} seconds...")
        await asyncio.sleep(self.reconnect_interval)
        try:
            await self.connect()
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")

    async def _resubscribe(self):
        """Resubscribe to all channels after reconnection."""
        for channel, markets in self.subscriptions.items():
            for market in markets:
                await self._send_subscribe(channel, market)

    async def _send_subscribe(self, channel: str, market: str):
        """
        Send subscription message.
        
        Args:
            channel: Channel name (e.g., 'trades', 'orderbook')
            market: Trading pair (e.g., 'ETH-USD')
        """
        if not self.ws:
            self.logger.error("Cannot subscribe: WebSocket not connected")
            return
            
        try:
            message = {
                "type": "subscribe",
                "channel": channel,
                "id": market
            }
            await self.ws.send(json.dumps(message))
            self.logger.info(f"Subscribed to {channel} for {market}")
        except Exception as e:
            self.logger.error(f"Subscription error: {e}")

    async def _send_unsubscribe(self, channel: str, market: str):
        """
        Send unsubscription message.
        
        Args:
            channel: Channel name (e.g., 'trades', 'orderbook')
            market: Trading pair (e.g., 'ETH-USD')
        """
        if not self.ws:
            return
            
        try:
            message = {
                "type": "unsubscribe",
                "channel": channel,
                "id": market
            }
            await self.ws.send(json.dumps(message))
            self.logger.info(f"Unsubscribed from {channel} for {market}")
        except Exception as e:
            self.logger.error(f"Unsubscription error: {e}")

    async def subscribe(self, channel: str, market: str):
        """
        Subscribe to a channel for a market.
        
        Args:
            channel: Channel name (e.g., 'trades', 'orderbook')
            market: Trading pair (e.g., 'ETH-USD')
        """
        if channel not in self.subscriptions:
            self.subscriptions[channel] = []
            
        if market not in self.subscriptions[channel]:
            self.subscriptions[channel].append(market)
            
        if self.ws:
            await self._send_subscribe(channel, market)

    async def unsubscribe(self, channel: str, market: str):
        """
        Unsubscribe from a channel for a market.
        
        Args:
            channel: Channel name (e.g., 'trades', 'orderbook')
            market: Trading pair (e.g., 'ETH-USD')
        """
        if channel in self.subscriptions and market in self.subscriptions[channel]:
            self.subscriptions[channel].remove(market)
            
        if self.ws:
            await self._send_unsubscribe(channel, market)

    def on_message(self, channel: str, callback: Callable[[Dict], Any]):
        """
        Register a callback for a channel.
        
        Args:
            channel: Channel name (e.g., 'trades', 'orderbook')
            callback: Callback function to handle messages
        """
        if channel not in self.message_callbacks:
            self.message_callbacks[channel] = []
            
        self.message_callbacks[channel].append(callback)

    def on_connect(self, callback: Callable[[], Any]):
        """
        Register a callback for connection events.
        
        Args:
            callback: Callback function to handle connection
        """
        self.connection_callbacks['connect'].append(callback)

    def on_disconnect(self, callback: Callable[[], Any]):
        """
        Register a callback for disconnection events.
        
        Args:
            callback: Callback function to handle disconnection
        """
        self.connection_callbacks['disconnect'].append(callback)

    async def listen(self):
        """Listen for WebSocket messages."""
        if not self.ws:
            await self.connect()
            
        while self.running:
            try:
                message = await self.ws.recv()
                await self._process_message(message)
            except websockets.ConnectionClosed:
                self.logger.warning("WebSocket connection closed")
                await self._handle_disconnect()
                break
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, message: str):
        """
        Process a WebSocket message.
        
        Args:
            message: JSON message string
        """
        try:
            data = json.loads(message)
            
            if self.config.get('debug', {}).get('log_market_data', False):
                self.logger.debug(f"WebSocket message: {json.dumps(data)}")
                
            # Handle different message types
            msg_type = data.get('type')
            
            if msg_type == 'subscribed':
                channel = data.get('channel')
                market = data.get('id')
                self.logger.info(f"Successfully subscribed to {channel} for {market}")
                
            elif msg_type == 'unsubscribed':
                channel = data.get('channel')
                market = data.get('id')
                self.logger.info(f"Successfully unsubscribed from {channel} for {market}")
                
            elif msg_type == 'error':
                self.logger.error(f"WebSocket error: {data.get('message')}")
                
            elif msg_type == 'channel_data':
                channel = data.get('channel')
                if channel in self.message_callbacks:
                    for callback in self.message_callbacks[channel]:
                        try:
                            await callback(data)
                        except Exception as e:
                            self.logger.error(f"Error in message callback: {e}")
                            
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def __aenter__(self):
        """Support for async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support for async context manager."""
        await self.close()
