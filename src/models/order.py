"""
Order model for dYdX v4.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

@dataclass
class Order:
    """
    Order model for dYdX v4.
    """
    market: str
    side: str  # 'buy' or 'sell'
    size: float
    type: str  # 'MARKET' or 'LIMIT'
    price: Optional[float] = None
    client_id: Optional[str] = None
    time_in_force: str = "GTT"  # Good Till Time
    good_til_block: Optional[int] = None
    good_til_time_in_seconds: Optional[int] = None
    post_only: bool = False
    reduce_only: bool = False
    
    def __post_init__(self):
        """Validate and set defaults after initialization."""
        # Validate side
        if self.side not in ['buy', 'sell']:
            raise ValueError(f"Invalid side: {self.side}. Must be 'buy' or 'sell'.")
        
        # Validate type
        if self.type not in ['MARKET', 'LIMIT']:
            raise ValueError(f"Invalid type: {self.type}. Must be 'MARKET' or 'LIMIT'.")
        
        # Validate price for LIMIT orders
        if self.type == 'LIMIT' and self.price is None:
            raise ValueError("Price is required for LIMIT orders.")
        
        # Generate client_id if not provided
        if self.client_id is None:
            self.client_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert order to dictionary for API requests.
        
        Returns:
            Dictionary representation of the order
        """
        order_dict = {
            "market": self.market,
            "side": self.side,
            "size": str(self.size),
            "type": self.type,
            "clientId": self.client_id,
            "timeInForce": self.time_in_force,
        }
        
        # Add optional fields if present
        if self.price is not None:
            order_dict["price"] = str(self.price)
        
        if self.good_til_block is not None:
            order_dict["goodTilBlock"] = self.good_til_block
        
        if self.good_til_time_in_seconds is not None:
            order_dict["goodTilTimeInSeconds"] = self.good_til_time_in_seconds
        
        if self.post_only:
            order_dict["postOnly"] = True
        
        if self.reduce_only:
            order_dict["reduceOnly"] = True
        
        return order_dict
    
    @classmethod
    def market_buy(cls, market: str, size: float) -> 'Order':
        """
        Create a market buy order.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            size: Order size
            
        Returns:
            Market buy order
        """
        return cls(
            market=market,
            side='buy',
            size=size,
            type='MARKET'
        )
    
    @classmethod
    def market_sell(cls, market: str, size: float) -> 'Order':
        """
        Create a market sell order.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            size: Order size
            
        Returns:
            Market sell order
        """
        return cls(
            market=market,
            side='sell',
            size=size,
            type='MARKET'
        )
    
    @classmethod
    def limit_buy(cls, market: str, size: float, price: float) -> 'Order':
        """
        Create a limit buy order.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            size: Order size
            price: Limit price
            
        Returns:
            Limit buy order
        """
        return cls(
            market=market,
            side='buy',
            size=size,
            type='LIMIT',
            price=price
        )
    
    @classmethod
    def limit_sell(cls, market: str, size: float, price: float) -> 'Order':
        """
        Create a limit sell order.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            size: Order size
            price: Limit price
            
        Returns:
            Limit sell order
        """
        return cls(
            market=market,
            side='sell',
            size=size,
            type='LIMIT',
            price=price
        )
