"""
Tests for the breakout strategy.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import numpy as np
from src.strategies.breakout_strategy import BreakoutStrategy

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
        }
    }

@pytest.fixture
def strategy(config):
    """Test strategy instance."""
    return BreakoutStrategy(config)

@pytest.fixture
def market_data():
    """Sample market data for testing."""
    # Generate sample data
    now = datetime.now()
    timestamps = [now - timedelta(minutes=i) for i in range(20, 0, -1)]
    
    # Create price series with a breakout pattern
    prices = [1000.0] * 10  # Flat prices
    prices += [1000.0, 1005.0, 1010.0, 1015.0, 1020.0]  # Rising prices
    prices += [1025.0, 1030.0, 1040.0, 1050.0, 1080.0]  # Breakout
    
    # Create volume series with a spike at the end
    volumes = [100.0] * 19  # Normal volumes
    volumes.append(300.0)  # Volume spike at breakout
    
    return {
        'prices': prices,
        'volumes': volumes,
        'timestamps': timestamps,
        'current_price': prices[-1],
    }

@pytest.mark.asyncio
async def test_analyze_breakout(strategy, market_data):
    """Test breakout detection."""
    # Run analysis
    analysis = await strategy.analyze(market_data)
    
    # Check results
    assert analysis['signal'] == 'breakout'
    assert analysis['current_price'] == 1080.0
    assert analysis['volume_anomaly'] > 2.0  # Should be above threshold

@pytest.mark.asyncio
async def test_analyze_no_breakout(strategy, market_data):
    """Test no breakout detection."""
    # Modify data to remove breakout conditions
    market_data['prices'][-1] = 1000.0  # No price breakout
    market_data['volumes'][-1] = 100.0  # No volume spike
    market_data['current_price'] = 1000.0
    
    # Run analysis
    analysis = await strategy.analyze(market_data)
    
    # Check results
    assert analysis['signal'] == 'neutral'
    assert analysis['current_price'] == 1000.0
    assert analysis['volume_anomaly'] <= 2.0  # Should be below threshold

def test_should_enter(strategy, market_data):
    """Test entry signal detection."""
    # Create analysis results
    breakout_analysis = {'signal': 'breakout', 'current_price': 1080.0}
    neutral_analysis = {'signal': 'neutral', 'current_price': 1000.0}
    
    # Check results
    assert strategy.should_enter(breakout_analysis) is True
    assert strategy.should_enter(neutral_analysis) is False

def test_calculate_position_size(strategy):
    """Test position size calculation."""
    # Create test data
    analysis = {
        'current_price': 1080.0,
        'resistance': 1000.0
    }
    account_info = {
        'equity': 10000.0
    }
    
    # Calculate position size
    position_size = strategy.calculate_position_size(analysis, account_info)
    
    # Check results
    assert position_size > 0
    assert position_size <= 0.1  # Should respect max position size

def test_calculate_exit_targets(strategy):
    """Test exit targets calculation."""
    # Create test data
    analysis = {
        'current_price': 1080.0,
        'resistance': 1000.0
    }
    entry_price = 1080.0
    
    # Calculate exit targets
    targets = strategy.calculate_exit_targets(analysis, entry_price)
    
    # Check results
    assert targets['stop_loss'] < entry_price
    assert targets['take_profit'] > entry_price
    assert targets['risk_reward_ratio'] == 3.0
