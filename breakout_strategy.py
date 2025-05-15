"""
Breakout trading strategy implementation using direct REST API.
"""
import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

from dydx_api import DydxApiClient

logger = logging.getLogger(__name__)

class BreakoutStrategy:
    """
    Breakout trading strategy with volume confirmation.
    """

    def __init__(self, api_client: DydxApiClient, market_id: str,
                 timeframe: str = "5MIN", volume_factor: float = 2.0,
                 resistance_periods: int = 24, risk_reward_ratio: float = 3.0):
        """
        Initialize the breakout strategy.

        Args:
            api_client: dYdX API client
            market_id: Market ID (e.g., "ETH-USD")
            timeframe: Candle timeframe (e.g., "5MIN")
            volume_factor: Factor by which volume should exceed average to confirm breakout
            resistance_periods: Number of periods to look back for resistance
            risk_reward_ratio: Risk-to-reward ratio for take profit calculation
        """
        self.api_client = api_client
        self.market_id = market_id
        self.timeframe = timeframe
        self.volume_factor = volume_factor
        self.resistance_periods = resistance_periods
        self.risk_reward_ratio = risk_reward_ratio

        # Strategy state
        self.candles = pd.DataFrame()
        self.resistance_level = 0.0
        self.average_volume = 0.0
        self.current_price = 0.0

    def update_market_data(self) -> bool:
        """
        Update market data and recalculate indicators.

        Returns:
            bool: True if data was updated successfully, False otherwise
        """
        try:
            # Get candles from API
            candles_data = self.api_client.get_candles(
                market_id=self.market_id,
                resolution=self.timeframe,
                limit=max(100, self.resistance_periods + 10)
            )

            # Check if we got valid data
            if "candles" not in candles_data or not candles_data["candles"]:
                logger.error(f"Failed to get candles for {self.market_id}")
                return False

            # Convert to DataFrame
            candles = pd.DataFrame(candles_data["candles"])

            # Convert types
            for col in ["open", "high", "low", "close", "baseTokenVolume"]:
                if col in candles.columns:
                    candles[col] = pd.to_numeric(candles[col])

            # Sort by startedAt
            if "startedAt" in candles.columns:
                candles = candles.sort_values("startedAt", ascending=False)

            self.candles = candles

            # Calculate resistance level (highest high in the lookback period)
            if "high" in candles.columns and len(candles) > 0:
                self.resistance_level = candles["high"].head(self.resistance_periods).max()

            # Calculate average volume
            if "baseTokenVolume" in candles.columns and len(candles) > 0:
                self.average_volume = candles["baseTokenVolume"].head(self.resistance_periods).mean()

            # Get current price from market data
            market_data = self.api_client.get_market(self.market_id)
            if "oraclePrice" in market_data:
                self.current_price = float(market_data["oraclePrice"])
            elif "close" in candles.columns and len(candles) > 0:
                self.current_price = candles["close"].iloc[0]  # Most recent candle

            logger.info(f"Updated market data - Resistance: {self.resistance_level:.2f}, "
                       f"Avg Volume: {self.average_volume:.2f}, Current Price: {self.current_price:.2f}")

            return True

        except Exception as e:
            logger.error(f"Failed to update market data: {str(e)}")
            return False

    def check_breakout_signal(self) -> Tuple[bool, Dict]:
        """
        Check if there's a breakout signal based on price and volume.

        Returns:
            Tuple[bool, Dict]: Signal detected (True/False) and signal details
        """
        # Make sure we have data
        if len(self.candles) == 0 or self.resistance_level == 0 or self.average_volume == 0:
            return False, {"error": "Insufficient data"}

        # Get latest candle
        latest_candle = self.candles.iloc[-1]

        # Check for breakout conditions
        price_breakout = self.current_price > self.resistance_level

        # Get current volume
        current_volume = latest_candle["baseTokenVolume"] if "baseTokenVolume" in latest_candle else 0

        # Check volume confirmation
        volume_confirmation = current_volume > (self.average_volume * self.volume_factor)

        # Signal is valid if both price breaks resistance and volume is high
        signal = price_breakout and volume_confirmation

        signal_details = {
            "signal": signal,
            "current_price": self.current_price,
            "resistance_level": self.resistance_level,
            "current_volume": current_volume,
            "average_volume": self.average_volume,
            "volume_factor": self.volume_factor,
            "price_breakout": price_breakout,
            "volume_confirmation": volume_confirmation
        }

        if signal:
            logger.info(f"BREAKOUT SIGNAL DETECTED! Price: {self.current_price:.2f} > Resistance: {self.resistance_level:.2f}, "
                       f"Volume: {current_volume:.2f} > Avg*Factor: {self.average_volume * self.volume_factor:.2f}")

        return signal, signal_details

    def calculate_entry_exit_levels(self) -> Dict:
        """
        Calculate entry, stop loss, and take profit levels.

        Returns:
            Dict: Entry, stop loss, and take profit levels
        """
        # Stop loss is just below the resistance level (which becomes support after breakout)
        # Using 1% below resistance as a simple approach
        stop_loss = self.resistance_level * 0.99

        # Risk is the difference between entry and stop loss
        risk = self.current_price - stop_loss

        # Take profit is entry plus risk times risk-reward ratio
        take_profit = self.current_price + (risk * self.risk_reward_ratio)

        levels = {
            "entry_price": self.current_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk": risk,
            "reward": risk * self.risk_reward_ratio,
            "risk_reward_ratio": self.risk_reward_ratio
        }

        logger.info(f"Position levels calculated - Entry: {self.current_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}, "
                   f"Risk: {risk:.2f}, Reward: {risk * self.risk_reward_ratio:.2f}, R:R = 1:{self.risk_reward_ratio}")

        return levels
