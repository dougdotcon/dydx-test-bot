"""
Tests for the market data service.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import numpy as np

from src.core.market_data import MarketDataService
from src.clients.rest_client import DydxRestClient
from src.clients.websocket_client import DydxWebSocketClient

@pytest.fixture
def config():
    """Test configuration."""
    return {
        'trading': {
            'market': 'ETH-USD',
            'timeframe': '5m',
            'volume_factor': 2.0,
            'risk_reward_ratio': 3.0
        },
        'risk': {
            'max_position_size': 0.1,
            'max_risk_per_trade': 0.02
        },
        'technical': {
            'resistance_period': 10,
            'volume_lookback': 20
        },
        'network': {
            'endpoints': {
                'rest': 'https://example.com',
                'ws': 'wss://example.com'
            }
        },
        'debug': {
            'ssl_verify': False
        }
    }

@pytest.fixture
def mock_rest_client():
    """Mock REST client."""
    client = MagicMock(spec=DydxRestClient)
    
    # Mock market data response
    client.get_market_data.return_value = asyncio.Future()
    client.get_market_data.return_value.set_result({
        'oraclePrice': '1000.0',
        'indexPrice': '1001.0',
        'priceChange24H': '10.0',
        'volume24H': '1000000.0'
    })
    
    # Mock trades response
    client.get_trades.return_value = asyncio.Future()
    client.get_trades.return_value.set_result([
        {
            'id': '1',
            'price': '1000.0',
            'size': '1.0',
            'side': 'buy',
            'createdAt': datetime.now().isoformat() + 'Z'
        },
        {
            'id': '2',
            'price': '1001.0',
            'size': '2.0',
            'side': 'sell',
            'createdAt': (datetime.now() - timedelta(minutes=1)).isoformat() + 'Z'
        }
    ])
    
    # Mock orderbook response
    client.get_orderbook.return_value = asyncio.Future()
    client.get_orderbook.return_value.set_result({
        'bids': [['990.0', '10.0'], ['980.0', '20.0']],
        'asks': [['1010.0', '10.0'], ['1020.0', '20.0']]
    })
    
    return client

@pytest.fixture
def mock_ws_client():
    """Mock WebSocket client."""
    client = MagicMock(spec=DydxWebSocketClient)
    
    # Mock connect method
    client.connect.return_value = asyncio.Future()
    client.connect.return_value.set_result(None)
    
    # Mock subscribe method
    client.subscribe.return_value = asyncio.Future()
    client.subscribe.return_value.set_result(None)
    
    # Mock listen method
    client.listen.return_value = asyncio.Future()
    client.listen.return_value.set_result(None)
    
    return client

@pytest.mark.asyncio
async def test_market_data_initialization(config, mock_rest_client, mock_ws_client):
    """Test market data service initialization."""
    # Patch the clients
    with patch('src.core.market_data.DydxRestClient', return_value=mock_rest_client), \
         patch('src.core.market_data.DydxWebSocketClient', return_value=mock_ws_client):
        
        # Create market data service
        market_data = MarketDataService(config)
        
        # Check initialization
        assert market_data.market == 'ETH-USD'
        assert market_data.timeframe == '5m'
        assert market_data.volume_lookback == 20
        assert market_data.prices == []
        assert market_data.volumes == []
        assert market_data.timestamps == []
        
        # Connect and load data
        await market_data.connect()
        
        # Check that clients were connected
        mock_rest_client.connect.assert_called_once()
        mock_ws_client.connect.assert_called_once()
        
        # Check that WebSocket subscriptions were made
        assert mock_ws_client.subscribe.call_count == 3
        
        # Check that initial data was loaded
        mock_rest_client.get_market_data.assert_called_once_with('ETH-USD')
        mock_rest_client.get_trades.assert_called_once_with('ETH-USD', limit=100)
        mock_rest_client.get_orderbook.assert_called_once_with('ETH-USD')
        
        # Close connections
        await market_data.close()
        
        # Check that clients were closed
        mock_rest_client.close.assert_called_once()
        mock_ws_client.close.assert_called_once()

@pytest.mark.asyncio
async def test_market_data_analysis(config, mock_rest_client, mock_ws_client):
    """Test market data analysis functions."""
    # Patch the clients
    with patch('src.core.market_data.DydxRestClient', return_value=mock_rest_client), \
         patch('src.core.market_data.DydxWebSocketClient', return_value=mock_ws_client):
        
        # Create market data service
        market_data = MarketDataService(config)
        
        # Connect and load data
        await market_data.connect()
        
        # Add some test data
        market_data.prices = [1000.0, 1010.0, 1020.0, 1030.0, 1040.0]
        market_data.volumes = [100.0, 110.0, 120.0, 130.0, 300.0]
        market_data.timestamps = [
            datetime.now() - timedelta(minutes=4),
            datetime.now() - timedelta(minutes=3),
            datetime.now() - timedelta(minutes=2),
            datetime.now() - timedelta(minutes=1),
            datetime.now()
        ]
        
        # Test get_current_price
        current_price = market_data.get_current_price()
        assert current_price is not None
        
        # Test calculate_volume_anomaly
        volume_anomaly = market_data.calculate_volume_anomaly()
        assert volume_anomaly is not None
        assert volume_anomaly > 1.0  # Should detect volume spike
        
        # Test calculate_resistance
        resistance = market_data.calculate_resistance()
        assert resistance is not None
        assert resistance == 1040.0  # Should be the highest price
        
        # Test get_market_data_for_analysis
        analysis_data = market_data.get_market_data_for_analysis()
        assert 'prices' in analysis_data
        assert 'volumes' in analysis_data
        assert 'timestamps' in analysis_data
        assert 'current_price' in analysis_data
        
        # Close connections
        await market_data.close()
