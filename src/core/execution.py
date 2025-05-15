"""
Execution module for the trading bot.
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

from ..clients.rest_client import DydxRestClient
from ..models.order import Order

class ExecutionService:
    """
    Service for executing orders and managing positions.
    """
    def __init__(self, config: Dict, rest_client: Optional[DydxRestClient] = None):
        """
        Initialize the execution service.
        
        Args:
            config: Bot configuration
            rest_client: REST client (optional, will create one if not provided)
        """
        self.config = config
        self.rest_client = rest_client or DydxRestClient(config)
        self.logger = logging.getLogger(__name__)
        
        # Simulation mode
        self.simulation_mode = config.get('execution', {}).get('simulation_mode', True)
        if self.simulation_mode:
            self.logger.warning("Running in simulation mode. No real orders will be placed.")
    
    async def connect(self):
        """Connect to API if needed."""
        if not self.rest_client.session:
            await self.rest_client.connect()
    
    async def send_order(
        self,
        side: str,
        size: float,
        price: Optional[float] = None,
        order_type: str = None,
        reduce_only: bool = False
    ) -> Dict:
        """
        Send an order to the exchange.
        
        Args:
            side: Order side ('buy' or 'sell')
            size: Order size
            price: Limit price (None for market orders)
            order_type: Order type ('LIMIT' or 'MARKET', defaults to 'MARKET' if price is None)
            reduce_only: Whether the order should only reduce position
            
        Returns:
            Order response
        """
        # Determine order type
        if order_type is None:
            order_type = "MARKET" if price is None else "LIMIT"
        
        # Create order
        order = Order(
            market=self.config['trading']['market'],
            side=side,
            size=size,
            type=order_type,
            price=price,
            reduce_only=reduce_only
        )
        
        self.logger.info(
            f"Sending order: {side} {size} {self.config['trading']['market']} "
            f"@ {price if price else 'market'}"
        )
        
        # Handle simulation mode
        if self.simulation_mode:
            self.logger.info("Simulation mode: Order not actually sent")
            return {
                "status": "success",
                "order": order.to_dict(),
                "simulation": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # Send order to exchange
        try:
            await self.connect()
            response = await self.rest_client.place_order(order.to_dict())
            
            if response:
                self.logger.info(f"Order sent successfully: {response}")
                return response
            else:
                error_msg = "Failed to send order: Empty response"
                self.logger.error(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Error sending order: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    async def get_position(self, market: Optional[str] = None) -> Optional[Dict]:
        """
        Get current position.
        
        Args:
            market: Market symbol (defaults to configured market)
            
        Returns:
            Position data or None if no position
        """
        if market is None:
            market = self.config['trading']['market']
        
        try:
            await self.connect()
            position = await self.rest_client.get_position(market)
            
            if position:
                self.logger.debug(f"Current position: {position}")
            else:
                self.logger.debug(f"No position found for {market}")
                
            return position
            
        except Exception as e:
            self.logger.error(f"Error getting position: {e}")
            return None
    
    async def get_all_positions(self) -> List[Dict]:
        """
        Get all positions.
        
        Returns:
            List of positions
        """
        try:
            await self.connect()
            positions = await self.rest_client.get_positions()
            
            if positions:
                self.logger.debug(f"Found {len(positions)} positions")
            else:
                self.logger.debug("No positions found")
                positions = []
                
            return positions
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []
    
    async def close_position(self, market: Optional[str] = None) -> Dict:
        """
        Close position for a market.
        
        Args:
            market: Market symbol (defaults to configured market)
            
        Returns:
            Order response
        """
        if market is None:
            market = self.config['trading']['market']
        
        try:
            # Get current position
            position = await self.get_position(market)
            
            if not position or float(position.get('size', 0)) == 0:
                self.logger.info(f"No position to close for {market}")
                return {"status": "info", "message": "No position to close"}
            
            # Determine side for closing
            side = 'sell' if position.get('side') == 'long' else 'buy'
            size = abs(float(position.get('size', 0)))
            
            # Send order to close position
            return await self.send_order(
                side=side,
                size=size,
                price=None,  # Market order
                order_type="MARKET",
                reduce_only=True
            )
            
        except Exception as e:
            error_msg = f"Error closing position: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def calculate_exit_levels(self, entry_price: float, side: str) -> Dict:
        """
        Calculate exit levels (stop loss and take profit).
        
        Args:
            entry_price: Entry price
            side: Position side ('buy' or 'sell')
            
        Returns:
            Dictionary with exit levels
        """
        # Get risk parameters
        risk_reward_ratio = self.config['trading']['risk_reward_ratio']
        
        # For long positions
        if side == 'buy':
            # Simple implementation: stop loss 2% below entry
            stop_loss = entry_price * 0.98
            # Take profit based on risk-reward ratio
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * risk_reward_ratio)
        # For short positions
        else:
            # Stop loss 2% above entry
            stop_loss = entry_price * 1.02
            # Take profit based on risk-reward ratio
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * risk_reward_ratio)
        
        return {
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward_ratio": risk_reward_ratio
        }
    
    async def close(self):
        """Close connections."""
        await self.rest_client.close()
        self.logger.info("Execution service stopped")
    
    async def __aenter__(self):
        """Support for async context manager."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support for async context manager."""
        await self.close()
