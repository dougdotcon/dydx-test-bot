"""
Market data collection module for dYdX trading bot.
"""
import logging
import time
from typing import List, Dict, Optional
import pandas as pd
import websocket
import json
import threading

from dydx_v4_python.clients import CompositeClient
import config

logger = logging.getLogger(__name__)

class MarketData:
    def __init__(self, client: CompositeClient, market: str = config.DEFAULT_MARKET,
                 timeframe: str = config.DEFAULT_TIMEFRAME):
        """
        Initialize the market data collector.

        Args:
            client: Initialized dYdX client
            market: Market symbol (e.g., "ETH-USD")
            timeframe: Candle timeframe (e.g., "5m")
        """
        self.client = client
        self.market = market
        self.timeframe = timeframe
        self.candles = pd.DataFrame()
        self.latest_price = 0.0
        self.ws = None
        self.ws_thread = None
        self.running = False

    def fetch_candles(self, limit: int = 100) -> pd.DataFrame:
        """
        Fetch historical candles from dYdX.

        Args:
            limit: Number of candles to fetch

        Returns:
            DataFrame: Candle data with columns [timestamp, open, high, low, close, volume]
        """
        try:
            # Convert timeframe to seconds for API
            resolution = self._timeframe_to_seconds(self.timeframe)

            # Fetch candles from dYdX API
            candles_data = self.client.get_candles(
                market=self.market,
                resolution=resolution,
                limit=limit
            )

            # Convert to DataFrame
            df = pd.DataFrame(candles_data)

            # Rename and convert columns
            df = df.rename(columns={
                'startedAt': 'timestamp',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'baseTokenVolume': 'volume'
            })

            # Convert types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])

            # Sort by timestamp
            df = df.sort_values('timestamp')

            self.candles = df
            logger.info(f"Fetched {len(df)} candles for {self.market}")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch candles: {str(e)}")
            return pd.DataFrame()

    def get_latest_price(self) -> float:
        """
        Get the latest price for the market.

        Returns:
            float: Latest price
        """
        try:
            ticker = self.client.get_ticker(market=self.market)
            self.latest_price = float(ticker['price'])
            return self.latest_price
        except Exception as e:
            logger.error(f"Failed to get latest price: {str(e)}")
            return self.latest_price

    def start_websocket(self):
        """
        Start WebSocket connection to receive real-time market data.
        """
        if self.running:
            return

        self.running = True
        self.ws_thread = threading.Thread(target=self._run_websocket)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        logger.info(f"Started WebSocket connection for {self.market}")

    def stop_websocket(self):
        """
        Stop the WebSocket connection.
        """
        self.running = False
        if self.ws:
            self.ws.close()
        logger.info("Stopped WebSocket connection")

    def _run_websocket(self):
        """
        Run the WebSocket connection in a separate thread.
        """
        ws_url = config.TESTNET_ENDPOINTS["INDEXER_WS"]

        def on_message(ws, message):
            try:
                data = json.loads(message)
                if 'type' in data and data['type'] == 'channel_data':
                    if 'contents' in data and 'trades' in data['contents']:
                        trades = data['contents']['trades']
                        if trades:
                            # Update latest price from the most recent trade
                            self.latest_price = float(trades[0]['price'])
                            logger.debug(f"New price for {self.market}: {self.latest_price}")
            except Exception as e:
                logger.error(f"WebSocket message error: {str(e)}")

        def on_error(ws, error):
            logger.error(f"WebSocket error: {str(error)}")

        def on_close(ws, close_status_code, close_msg):
            logger.info(f"WebSocket connection closed: {close_msg}")
            if self.running:
                logger.info("Attempting to reconnect WebSocket in 5 seconds...")
                time.sleep(5)
                self._run_websocket()

        def on_open(ws):
            logger.info("WebSocket connection opened")
            # Subscribe to trades for the market
            subscribe_msg = {
                "type": "subscribe",
                "channel": "v4_trades",
                "id": self.market
            }
            ws.send(json.dumps(subscribe_msg))

        # Create WebSocket connection
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        # Run WebSocket connection
        self.ws.run_forever()

    def _timeframe_to_seconds(self, timeframe: str) -> int:
        """
        Convert timeframe string to seconds.

        Args:
            timeframe: Timeframe string (e.g., "5m", "1h")

        Returns:
            int: Timeframe in seconds
        """
        unit = timeframe[-1]
        value = int(timeframe[:-1])

        if unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 60 * 60
        elif unit == 'd':
            return value * 60 * 60 * 24
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")
