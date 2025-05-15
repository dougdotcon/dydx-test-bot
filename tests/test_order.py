"""
Tests for the order model.
"""

import pytest
from src.models.order import Order

def test_order_initialization():
    """Test order initialization."""
    # Create a market buy order
    order = Order(
        market='ETH-USD',
        side='buy',
        size=0.1,
        type='MARKET'
    )
    
    # Check attributes
    assert order.market == 'ETH-USD'
    assert order.side == 'buy'
    assert order.size == 0.1
    assert order.type == 'MARKET'
    assert order.price is None
    assert order.client_id is not None  # Should be auto-generated
    assert order.time_in_force == 'GTT'
    assert order.post_only is False
    assert order.reduce_only is False
    
    # Create a limit sell order
    order = Order(
        market='BTC-USD',
        side='sell',
        size=0.05,
        type='LIMIT',
        price=50000.0,
        client_id='test-123',
        post_only=True
    )
    
    # Check attributes
    assert order.market == 'BTC-USD'
    assert order.side == 'sell'
    assert order.size == 0.05
    assert order.type == 'LIMIT'
    assert order.price == 50000.0
    assert order.client_id == 'test-123'
    assert order.post_only is True
    assert order.reduce_only is False

def test_order_validation():
    """Test order validation."""
    # Test invalid side
    with pytest.raises(ValueError, match="Invalid side"):
        Order(
            market='ETH-USD',
            side='invalid',
            size=0.1,
            type='MARKET'
        )
    
    # Test invalid type
    with pytest.raises(ValueError, match="Invalid type"):
        Order(
            market='ETH-USD',
            side='buy',
            size=0.1,
            type='INVALID'
        )
    
    # Test missing price for limit order
    with pytest.raises(ValueError, match="Price is required for LIMIT orders"):
        Order(
            market='ETH-USD',
            side='buy',
            size=0.1,
            type='LIMIT'
        )

def test_order_to_dict():
    """Test converting order to dictionary."""
    # Create a market buy order
    order = Order(
        market='ETH-USD',
        side='buy',
        size=0.1,
        type='MARKET',
        client_id='test-123'
    )
    
    # Convert to dictionary
    order_dict = order.to_dict()
    
    # Check dictionary
    assert order_dict['market'] == 'ETH-USD'
    assert order_dict['side'] == 'buy'
    assert order_dict['size'] == '0.1'  # Should be converted to string
    assert order_dict['type'] == 'MARKET'
    assert order_dict['clientId'] == 'test-123'
    assert order_dict['timeInForce'] == 'GTT'
    assert 'price' not in order_dict  # Price should not be included for market orders
    
    # Create a limit sell order with all options
    order = Order(
        market='BTC-USD',
        side='sell',
        size=0.05,
        type='LIMIT',
        price=50000.0,
        client_id='test-456',
        post_only=True,
        reduce_only=True,
        good_til_block=12345
    )
    
    # Convert to dictionary
    order_dict = order.to_dict()
    
    # Check dictionary
    assert order_dict['market'] == 'BTC-USD'
    assert order_dict['side'] == 'sell'
    assert order_dict['size'] == '0.05'
    assert order_dict['type'] == 'LIMIT'
    assert order_dict['price'] == '50000.0'
    assert order_dict['clientId'] == 'test-456'
    assert order_dict['timeInForce'] == 'GTT'
    assert order_dict['postOnly'] is True
    assert order_dict['reduceOnly'] is True
    assert order_dict['goodTilBlock'] == 12345

def test_order_factory_methods():
    """Test order factory methods."""
    # Test market_buy
    order = Order.market_buy('ETH-USD', 0.1)
    assert order.market == 'ETH-USD'
    assert order.side == 'buy'
    assert order.size == 0.1
    assert order.type == 'MARKET'
    assert order.price is None
    
    # Test market_sell
    order = Order.market_sell('ETH-USD', 0.1)
    assert order.market == 'ETH-USD'
    assert order.side == 'sell'
    assert order.size == 0.1
    assert order.type == 'MARKET'
    assert order.price is None
    
    # Test limit_buy
    order = Order.limit_buy('ETH-USD', 0.1, 1000.0)
    assert order.market == 'ETH-USD'
    assert order.side == 'buy'
    assert order.size == 0.1
    assert order.type == 'LIMIT'
    assert order.price == 1000.0
    
    # Test limit_sell
    order = Order.limit_sell('ETH-USD', 0.1, 1000.0)
    assert order.market == 'ETH-USD'
    assert order.side == 'sell'
    assert order.size == 0.1
    assert order.type == 'LIMIT'
    assert order.price == 1000.0
