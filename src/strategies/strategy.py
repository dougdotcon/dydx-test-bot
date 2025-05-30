"""
Breakout trading strategy implementation.
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

from ..core import config
from ..core.market_data import MarketData

logger = logging.getLogger(__name__)

class BreakoutStrategy:
    def __init__(self, market_data: MarketData,
                 volume_factor: float = config.DEFAULT_VOLUME_FACTOR,
                 resistance_periods: int = config.DEFAULT_RESISTANCE_PERIODS,
                 risk_reward_ratio: float = config.DEFAULT_RISK_REWARD_RATIO):
        """
        Initialize the breakout strategy.

        Args:
            market_data: Market data collector
            volume_factor: Factor by which volume should exceed average to confirm breakout
            resistance_periods: Number of periods to look back for resistance
            risk_reward_ratio: Risk-to-reward ratio for take profit calculation
        """
        self.market_data = market_data
        self.volume_factor = volume_factor
        self.resistance_periods = resistance_periods
        self.risk_reward_ratio = risk_reward_ratio
        self.resistance_level = 0.0
        self.average_volume = 0.0

    def update_market_data(self):
        """
        Update market data and recalculate indicators.
        """
        # Fetch latest candles
        self.market_data.fetch_candles(limit=max(100, self.resistance_periods + 10))

        if len(self.market_data.candles) > 0:
            # Calculate resistance level (highest high in the lookback period)
            self.resistance_level = self.market_data.candles['high'].tail(self.resistance_periods).max()

            # Calculate average volume
            self.average_volume = self.market_data.candles['volume'].tail(self.resistance_periods).mean()

            logger.info(f"Updated indicators - Resistance: {self.resistance_level:.2f}, Avg Volume: {self.average_volume:.2f}")

    def check_breakout_signal(self) -> Tuple[bool, Dict]:
        """
        Check if there's a breakout signal based on price and volume.

        Returns:
            Tuple[bool, Dict]: Signal detected (True/False) and signal details
        """
        # Get latest price and update market data
        current_price = self.market_data.get_latest_price()

        # Get latest candle's volume
        if len(self.market_data.candles) > 0:
            latest_candle = self.market_data.candles.iloc[-1]
            current_volume = latest_candle['volume']
        else:
            current_volume = 0

        # Check for breakout conditions
        price_breakout = current_price > self.resistance_level
        volume_confirmation = current_volume > (self.average_volume * self.volume_factor)

        # Signal is valid if both price breaks resistance and volume is high
        signal = price_breakout and volume_confirmation

        signal_details = {
            "signal": signal,
            "current_price": current_price,
            "resistance_level": self.resistance_level,
            "current_volume": current_volume,
            "average_volume": self.average_volume,
            "volume_factor": self.volume_factor,
            "price_breakout": price_breakout,
            "volume_confirmation": volume_confirmation
        }

        if signal:
            logger.info(f"BREAKOUT SIGNAL DETECTED! Price: {current_price:.2f} > Resistance: {self.resistance_level:.2f}, "
                       f"Volume: {current_volume:.2f} > Avg*Factor: {self.average_volume * self.volume_factor:.2f}")

        return signal, signal_details

    def calculate_entry_exit_levels(self, entry_price: float) -> Dict:
        """
        Calculate entry, stop loss, and take profit levels.

        Args:
            entry_price: Entry price for the position

        Returns:
            Dict: Entry, stop loss, and take profit levels
        """
        # Stop loss is just below the resistance level (which becomes support after breakout)
        # Using 1% below resistance as a simple approach
        stop_loss = self.resistance_level * 0.99

        # Risk is the difference between entry and stop loss
        risk = entry_price - stop_loss

        # Take profit is entry plus risk times risk-reward ratio
        take_profit = entry_price + (risk * self.risk_reward_ratio)

        levels = {
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk": risk,
            "reward": risk * self.risk_reward_ratio,
            "risk_reward_ratio": self.risk_reward_ratio
        }

        logger.info(f"Position levels calculated - Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}, "
                   f"Risk: {risk:.2f}, Reward: {risk * self.risk_reward_ratio:.2f}, R:R = 1:{self.risk_reward_ratio}")

        return levels
