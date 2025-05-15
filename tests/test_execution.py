"""
Tests for the execution service.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.core.execution import ExecutionService
from src.clients.rest_client import DydxRestClient
from src.models.order import Order

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
        'execution': {
            'simulation_mode': True
        },
        'debug': {
            'ssl_verify': False
        }
    }

@pytest.fixture
def mock_rest_client():
    """Mock REST client."""
    client = MagicMock(spec=DydxRestClient)
    
    # Mock place_order response
    client.place_order.return_value = asyncio.Future()
    client.place_order.return_value.set_result({
        'order': {
            'id': '123',
            'market': 'ETH-USD',
            'side': 'buy',
            'size': '0.1',
            'price': '1000.0',
            'status': 'open'
        }
    })
    
    # Mock get_position response
    client.get_position.return_value = asyncio.Future()
    client.get_position.return_value.set_result({
        'market': 'ETH-USD',
        'side': 'long',
        'size': '0.1',
        'entryPrice': '1000.0',
        'unrealizedPnl': '10.0'
    })
    
    # Mock get_positions response
    client.get_positions.return_value = asyncio.Future()
    client.get_positions.return_value.set_result([
        {
            'market': 'ETH-USD',
            'side': 'long',
            'size': '0.1',
            'entryPrice': '1000.0',
            'unrealizedPnl': '10.0'
        }
    ])
    
    return client

@pytest.mark.asyncio
async def test_execution_initialization(config, mock_rest_client):
    """Test execution service initialization."""
    # Create execution service with mock client
    execution = ExecutionService(config, mock_rest_client)
    
    # Check initialization
    assert execution.config == config
    assert execution.rest_client == mock_rest_client
    assert execution.simulation_mode is True
    
    # Connect
    await execution.connect()
    
    # Check that client was connected
    mock_rest_client.connect.assert_called_once()
    
    # Close connections
    await execution.close()
    
    # Check that client was closed
    mock_rest_client.close.assert_called_once()

@pytest.mark.asyncio
async def test_send_order_simulation(config, mock_rest_client):
    """Test sending an order in simulation mode."""
    # Create execution service with mock client
    execution = ExecutionService(config, mock_rest_client)
    
    # Send a market buy order
    result = await execution.send_order(
        side='buy',
        size=0.1,
        price=None
    )
    
    # Check result
    assert result['status'] == 'success'
    assert result['simulation'] is True
    assert result['order']['market'] == 'ETH-USD'
    assert result['order']['side'] == 'buy'
    assert result['order']['size'] == 0.1
    assert result['order']['type'] == 'MARKET'
    
    # Check that no real order was placed
    mock_rest_client.place_order.assert_not_called()

@pytest.mark.asyncio
async def test_send_order_real(config, mock_rest_client):
    """Test sending a real order."""
    # Modify config to disable simulation mode
    config['execution']['simulation_mode'] = False
    
    # Create execution service with mock client
    execution = ExecutionService(config, mock_rest_client)
    
    # Send a limit buy order
    result = await execution.send_order(
        side='buy',
        size=0.1,
        price=1000.0
    )
    
    # Check that a real order was placed
    mock_rest_client.place_order.assert_called_once()
    
    # Check the order parameters
    order_dict = mock_rest_client.place_order.call_args[0][0]
    assert order_dict['market'] == 'ETH-USD'
    assert order_dict['side'] == 'buy'
    assert order_dict['size'] == 0.1
    assert order_dict['type'] == 'LIMIT'
    assert order_dict['price'] == 1000.0

@pytest.mark.asyncio
async def test_get_position(config, mock_rest_client):
    """Test getting a position."""
    # Create execution service with mock client
    execution = ExecutionService(config, mock_rest_client)
    
    # Get position
    position = await execution.get_position()
    
    # Check that client method was called
    mock_rest_client.get_position.assert_called_once_with('ETH-USD')
    
    # Check position data
    assert position['market'] == 'ETH-USD'
    assert position['side'] == 'long'
    assert position['size'] == '0.1'
    assert position['entryPrice'] == '1000.0'

@pytest.mark.asyncio
async def test_get_all_positions(config, mock_rest_client):
    """Test getting all positions."""
    # Create execution service with mock client
    execution = ExecutionService(config, mock_rest_client)
    
    # Get all positions
    positions = await execution.get_all_positions()
    
    # Check that client method was called
    mock_rest_client.get_positions.assert_called_once()
    
    # Check positions data
    assert len(positions) == 1
    assert positions[0]['market'] == 'ETH-USD'
    assert positions[0]['side'] == 'long'
    assert positions[0]['size'] == '0.1'

@pytest.mark.asyncio
async def test_close_position(config, mock_rest_client):
    """Test closing a position."""
    # Create execution service with mock client
    execution = ExecutionService(config, mock_rest_client)
    
    # Close position
    result = await execution.close_position()
    
    # Check that position was queried
    mock_rest_client.get_position.assert_called_once_with('ETH-USD')
    
    # In simulation mode, no real order should be placed
    mock_rest_client.place_order.assert_not_called()
    
    # Check result
    assert result['status'] == 'success'
    assert result['simulation'] is True
    assert result['order']['side'] == 'sell'  # Should be opposite of position side
    assert result['order']['size'] == 0.1
    assert result['order']['type'] == 'MARKET'
    assert result['order']['reduce_only'] is True

def test_calculate_exit_levels(config, mock_rest_client):
    """Test calculating exit levels."""
    # Create execution service with mock client
    execution = ExecutionService(config, mock_rest_client)
    
    # Calculate exit levels for a long position
    exit_levels = execution.calculate_exit_levels(1000.0, 'buy')
    
    # Check exit levels
    assert exit_levels['stop_loss'] < 1000.0
    assert exit_levels['take_profit'] > 1000.0
    assert exit_levels['risk_reward_ratio'] == 3.0
    
    # Calculate exit levels for a short position
    exit_levels = execution.calculate_exit_levels(1000.0, 'sell')
    
    # Check exit levels
    assert exit_levels['stop_loss'] > 1000.0
    assert exit_levels['take_profit'] < 1000.0
    assert exit_levels['risk_reward_ratio'] == 3.0
