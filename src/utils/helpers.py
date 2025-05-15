"""
Helper functions for the trading bot.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def format_price(price: float, decimals: int = 2) -> str:
    """
    Format price for display.
    
    Args:
        price: Price to format
        decimals: Number of decimal places
    
    Returns:
        Formatted price string
    """
    return f"{price:.{decimals}f}"

def calculate_position_size(
    account_balance: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calculate position size based on risk.
    
    Args:
        account_balance: Account balance
        risk_per_trade: Risk per trade as a percentage (0.02 = 2%)
        entry_price: Entry price
        stop_loss: Stop loss price
    
    Returns:
        Position size
    
    Raises:
        ValueError: If entry price equals stop loss
    """
    risk_amount = account_balance * risk_per_trade
    price_risk = abs(entry_price - stop_loss)
    
    if price_risk == 0:
        raise ValueError("Entry price equals stop loss")
    
    position_size = risk_amount / price_risk
    return position_size

def calculate_pnl(
    entry_price: float,
    exit_price: float,
    position_size: float,
    side: str
) -> float:
    """
    Calculate profit and loss.
    
    Args:
        entry_price: Entry price
        exit_price: Exit price
        position_size: Position size
        side: Position side ('buy' or 'sell')
    
    Returns:
        Profit and loss
    """
    if side == 'buy':
        return (exit_price - entry_price) * position_size
    else:  # sell
        return (entry_price - exit_price) * position_size

def calculate_roi(
    entry_price: float,
    exit_price: float,
    side: str
) -> float:
    """
    Calculate return on investment.
    
    Args:
        entry_price: Entry price
        exit_price: Exit price
        side: Position side ('buy' or 'sell')
    
    Returns:
        Return on investment as a percentage
    """
    if side == 'buy':
        return (exit_price - entry_price) / entry_price * 100
    else:  # sell
        return (entry_price - exit_price) / entry_price * 100

def calculate_moving_average(prices: List[float], window: int) -> List[float]:
    """
    Calculate moving average.
    
    Args:
        prices: List of prices
        window: Moving average window
    
    Returns:
        List of moving averages
    """
    if len(prices) < window:
        return []
    
    return list(pd.Series(prices).rolling(window=window).mean().dropna())

def calculate_resistance(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate resistance level.
    
    Args:
        prices: List of prices
        period: Lookback period
    
    Returns:
        Resistance level or None if not enough data
    """
    if len(prices) < period:
        return None
    
    return max(prices[-period:])

def calculate_support(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate support level.
    
    Args:
        prices: List of prices
        period: Lookback period
    
    Returns:
        Support level or None if not enough data
    """
    if len(prices) < period:
        return None
    
    return min(prices[-period:])

def calculate_volume_anomaly(volumes: List[float]) -> Optional[float]:
    """
    Calculate volume anomaly.
    
    Args:
        volumes: List of volumes
    
    Returns:
        Volume anomaly ratio or None if not enough data
    """
    if len(volumes) < 2:
        return None
    
    current_volume = volumes[-1]
    avg_volume = np.mean(volumes[:-1])
    
    return current_volume / avg_volume if avg_volume > 0 else None

def timestamp_to_datetime(timestamp: Union[int, str]) -> datetime:
    """
    Convert timestamp to datetime.
    
    Args:
        timestamp: Unix timestamp (seconds or milliseconds) or ISO string
    
    Returns:
        Datetime object
    """
    if isinstance(timestamp, str):
        # ISO format
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif isinstance(timestamp, int):
        # Unix timestamp
        if timestamp > 1e12:  # milliseconds
            return datetime.fromtimestamp(timestamp / 1000)
        else:  # seconds
            return datetime.fromtimestamp(timestamp)
    else:
        raise ValueError(f"Unsupported timestamp format: {timestamp}")

def datetime_to_timestamp(dt: datetime, milliseconds: bool = False) -> int:
    """
    Convert datetime to timestamp.
    
    Args:
        dt: Datetime object
        milliseconds: Whether to return milliseconds
    
    Returns:
        Unix timestamp
    """
    timestamp = dt.timestamp()
    if milliseconds:
        return int(timestamp * 1000)
    else:
        return int(timestamp)
