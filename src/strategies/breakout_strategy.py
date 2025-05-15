"""
Breakout strategy implementation.
"""

from typing import Dict, Optional, List, Any
import pandas as pd
import numpy as np
from datetime import datetime
from .base_strategy import BaseStrategy

class BreakoutStrategy(BaseStrategy):
    """
    Breakout strategy with volume confirmation.
    Detects price breakouts above resistance levels with abnormal volume.
    """
    def __init__(self, config: Dict):
        """
        Initialize the breakout strategy.
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        self.market = config['trading']['market']
        self.volume_factor = config['trading']['volume_factor']
        self.risk_reward_ratio = config['trading']['risk_reward_ratio']
        self.resistance_period = config['technical']['resistance_period']
        self.volume_lookback = config['technical']['volume_lookback']
        
        # Risk parameters
        self.max_position_size = config['risk']['max_position_size']
        self.max_risk_per_trade = config['risk']['max_risk_per_trade']
        
        self.logger.info(f"Breakout strategy initialized for {self.market}")
        
    async def analyze(self, market_data: Dict) -> Dict:
        """
        Analyze market data for breakout signals.
        
        Args:
            market_data: Market data dictionary with prices, volumes, and timestamps
            
        Returns:
            Dictionary with analysis results
        """
        prices = market_data.get('prices', [])
        volumes = market_data.get('volumes', [])
        timestamps = market_data.get('timestamps', [])
        
        if not prices or len(prices) < self.resistance_period:
            return {
                'signal': 'insufficient_data',
                'current_price': prices[-1] if prices else None,
                'timestamp': datetime.now().isoformat()
            }
        
        # Calculate current price
        current_price = prices[-1]
        
        # Calculate resistance level (simple implementation using period high)
        resistance = max(prices[-self.resistance_period:])
        
        # Calculate volume anomaly
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[:-1]) if len(volumes) > 1 else current_volume
        volume_anomaly = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Determine signal
        signal = 'neutral'
        if current_price > resistance and volume_anomaly > self.volume_factor:
            signal = 'breakout'
            self.logger.info(
                f"Breakout detected! Price: {current_price} > {resistance}, "
                f"Volume: {volume_anomaly:.2f}x above average"
            )
        
        return {
            'signal': signal,
            'current_price': current_price,
            'resistance': resistance,
            'volume_anomaly': volume_anomaly,
            'timestamp': datetime.now().isoformat()
        }
    
    def should_enter(self, analysis: Dict) -> bool:
        """
        Determine if a position should be entered based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            
        Returns:
            True if a position should be entered, False otherwise
        """
        return analysis.get('signal') == 'breakout'
    
    def should_exit(self, analysis: Dict, position: Dict) -> bool:
        """
        Determine if a position should be exited based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            position: Current position information
            
        Returns:
            True if the position should be exited, False otherwise
        """
        # This is a simple implementation
        # In a real system, you would check stop loss and take profit levels
        current_price = analysis.get('current_price')
        entry_price = position.get('entry_price')
        side = position.get('side')
        
        if not all([current_price, entry_price, side]):
            return False
        
        # For long positions
        if side == 'buy':
            # Exit if price falls below entry (simple implementation)
            return current_price < entry_price
        
        return False
    
    def calculate_position_size(self, analysis: Dict, account_info: Dict) -> float:
        """
        Calculate position size based on analysis and account information.
        
        Args:
            analysis: Analysis results from analyze()
            account_info: Account information
            
        Returns:
            Position size
        """
        # Get account balance
        equity = account_info.get('equity', 0)
        if equity <= 0:
            return 0
        
        # Calculate risk amount
        risk_amount = equity * self.max_risk_per_trade
        
        # Calculate price risk (distance to stop loss)
        current_price = analysis.get('current_price')
        resistance = analysis.get('resistance')
        
        if not current_price or not resistance:
            return 0
        
        # Simple stop loss calculation: just below resistance
        stop_loss = resistance * 0.99
        price_risk = current_price - stop_loss
        
        if price_risk <= 0:
            return 0
        
        # Calculate position size based on risk
        position_size = risk_amount / price_risk
        
        # Apply maximum position size limit
        position_size = min(position_size, self.max_position_size)
        
        return position_size
    
    def calculate_entry_price(self, analysis: Dict) -> float:
        """
        Calculate entry price based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            
        Returns:
            Entry price
        """
        # For a breakout strategy, we enter at current price
        return analysis.get('current_price', 0)
    
    def calculate_exit_targets(self, analysis: Dict, entry_price: float) -> Dict:
        """
        Calculate exit targets (stop loss, take profit) based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            entry_price: Entry price
            
        Returns:
            Dictionary with exit targets
        """
        resistance = analysis.get('resistance', 0)
        
        # Stop loss just below resistance
        stop_loss = resistance * 0.99
        
        # Risk is the distance from entry to stop loss
        risk = entry_price - stop_loss
        
        # Take profit based on risk-reward ratio
        take_profit = entry_price + (risk * self.risk_reward_ratio)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': self.risk_reward_ratio
        }
