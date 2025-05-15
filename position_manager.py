"""
Position management for the dYdX trading bot.
"""
import logging
import time
from typing import Dict, Optional

from dydx_api import DydxApiClient

logger = logging.getLogger(__name__)

class PositionManager:
    """
    Manages trading positions (simulated for now).
    """
    
    def __init__(self, api_client: DydxApiClient, market_id: str, position_size_usd: float = 100.0):
        """
        Initialize the position manager.
        
        Args:
            api_client: dYdX API client
            market_id: Market ID (e.g., "ETH-USD")
            position_size_usd: Position size in USD
        """
        self.api_client = api_client
        self.market_id = market_id
        self.position_size_usd = position_size_usd
        
        # Position state
        self.active_position = None
    
    def open_long_position(self, entry_price: float, stop_loss: float, take_profit: float) -> Dict:
        """
        Open a long position (simulated).
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Dict: Position information
        """
        # Calculate position size in tokens
        size = self.position_size_usd / entry_price
        
        # Create position object
        position = {
            "market": self.market_id,
            "side": "LONG",
            "entry_price": entry_price,
            "size": size,
            "size_usd": self.position_size_usd,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "OPEN",
            "opened_at": time.time()
        }
        
        self.active_position = position
        logger.info(f"Opened LONG position: {position}")
        
        return position
    
    def close_position(self, exit_price: float, reason: str) -> Dict:
        """
        Close the active position (simulated).
        
        Args:
            exit_price: Exit price
            reason: Reason for closing the position (e.g., "stop_loss", "take_profit")
            
        Returns:
            Dict: Closed position information
        """
        if not self.active_position:
            logger.warning("No active position to close")
            return {"status": "FAILED", "error": "No active position"}
        
        # Calculate profit/loss
        if self.active_position["side"] == "LONG":
            pnl = (exit_price - self.active_position["entry_price"]) * self.active_position["size"]
            pnl_percent = ((exit_price / self.active_position["entry_price"]) - 1) * 100
        else:
            pnl = (self.active_position["entry_price"] - exit_price) * self.active_position["size"]
            pnl_percent = ((self.active_position["entry_price"] / exit_price) - 1) * 100
        
        # Update position status
        closed_position = {
            **self.active_position,
            "status": "CLOSED",
            "exit_price": exit_price,
            "exit_reason": reason,
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "closed_at": time.time(),
            "duration": time.time() - self.active_position["opened_at"]
        }
        
        logger.info(f"Closed position due to {reason}: {closed_position}")
        
        # Clear active position
        self.active_position = None
        
        return closed_position
    
    def check_exit_conditions(self, current_price: float) -> Optional[str]:
        """
        Check if exit conditions (stop loss or take profit) are met.
        
        Args:
            current_price: Current market price
            
        Returns:
            Optional[str]: Exit reason or None if no exit condition is met
        """
        if not self.active_position:
            return None
        
        if self.active_position["side"] == "LONG":
            # Check stop loss
            if current_price <= self.active_position["stop_loss"]:
                return "stop_loss"
            
            # Check take profit
            if current_price >= self.active_position["take_profit"]:
                return "take_profit"
        
        return None
    
    def get_position_status(self) -> Dict:
        """
        Get the status of the active position.
        
        Returns:
            Dict: Position status
        """
        if not self.active_position:
            return {"status": "NO_POSITION"}
        
        return self.active_position
