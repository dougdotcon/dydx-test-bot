"""
Market model for dYdX v4.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class Trade:
    """
    Trade model for dYdX v4.
    """
    id: str
    price: float
    size: float
    side: str  # 'buy' or 'sell'
    created_at: datetime
    
    @classmethod
    def from_api(cls, trade_data: Dict[str, Any]) -> 'Trade':
        """
        Create a Trade from API data.
        
        Args:
            trade_data: Trade data from API
            
        Returns:
            Trade instance
        """
        return cls(
            id=trade_data.get('id', ''),
            price=float(trade_data.get('price', 0)),
            size=float(trade_data.get('size', 0)),
            side=trade_data.get('side', ''),
            created_at=datetime.fromisoformat(
                trade_data.get('createdAt', '').replace('Z', '+00:00')
            ) if trade_data.get('createdAt') else datetime.now()
        )

@dataclass
class OrderBookLevel:
    """
    Order book level model for dYdX v4.
    """
    price: float
    size: float
    
    @classmethod
    def from_api(cls, level_data: List) -> 'OrderBookLevel':
        """
        Create an OrderBookLevel from API data.
        
        Args:
            level_data: Level data from API [price, size]
            
        Returns:
            OrderBookLevel instance
        """
        return cls(
            price=float(level_data[0]),
            size=float(level_data[1])
        )

@dataclass
class OrderBook:
    """
    Order book model for dYdX v4.
    """
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    
    @classmethod
    def from_api(cls, orderbook_data: Dict[str, Any]) -> 'OrderBook':
        """
        Create an OrderBook from API data.
        
        Args:
            orderbook_data: Order book data from API
            
        Returns:
            OrderBook instance
        """
        bids = [OrderBookLevel.from_api(bid) for bid in orderbook_data.get('bids', [])]
        asks = [OrderBookLevel.from_api(ask) for ask in orderbook_data.get('asks', [])]
        
        return cls(bids=bids, asks=asks)

@dataclass
class MarketData:
    """
    Market data model for dYdX v4.
    """
    market: str
    index_price: Optional[float] = None
    oracle_price: Optional[float] = None
    price_change_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    trades: List[Trade] = None
    orderbook: Optional[OrderBook] = None
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.trades is None:
            self.trades = []
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @classmethod
    def from_api(cls, market: str, market_data: Dict[str, Any]) -> 'MarketData':
        """
        Create a MarketData from API data.
        
        Args:
            market: Market symbol (e.g., 'ETH-USD')
            market_data: Market data from API
            
        Returns:
            MarketData instance
        """
        return cls(
            market=market,
            index_price=float(market_data.get('indexPrice', 0)) or None,
            oracle_price=float(market_data.get('oraclePrice', 0)) or None,
            price_change_24h=float(market_data.get('priceChange24H', 0)) or None,
            volume_24h=float(market_data.get('volume24H', 0)) or None,
            last_updated=datetime.now()
        )
    
    def update_trades(self, trades_data: List[Dict[str, Any]]) -> None:
        """
        Update trades with new data.
        
        Args:
            trades_data: Trades data from API
        """
        self.trades = [Trade.from_api(trade) for trade in trades_data]
        self.last_updated = datetime.now()
    
    def update_orderbook(self, orderbook_data: Dict[str, Any]) -> None:
        """
        Update order book with new data.
        
        Args:
            orderbook_data: Order book data from API
        """
        self.orderbook = OrderBook.from_api(orderbook_data)
        self.last_updated = datetime.now()
    
    def get_mid_price(self) -> Optional[float]:
        """
        Get mid price from order book.
        
        Returns:
            Mid price or None if order book is empty
        """
        if not self.orderbook or not self.orderbook.bids or not self.orderbook.asks:
            return None
        
        best_bid = self.orderbook.bids[0].price
        best_ask = self.orderbook.asks[0].price
        
        return (best_bid + best_ask) / 2
    
    def get_current_price(self) -> Optional[float]:
        """
        Get current price from various sources.
        
        Returns:
            Current price or None if no price is available
        """
        # Try oracle price first
        if self.oracle_price:
            return self.oracle_price
        
        # Then index price
        if self.index_price:
            return self.index_price
        
        # Then mid price from order book
        mid_price = self.get_mid_price()
        if mid_price:
            return mid_price
        
        # Then last trade price
        if self.trades:
            return self.trades[0].price
        
        return None
