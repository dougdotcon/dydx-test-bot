"""
Test script for the dYdX trading bot.
"""
import logging
from dydx_api import DydxApiClient
from breakout_strategy import BreakoutStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_api_client():
    """Test the dYdX API client."""
    logger.info("Testing DydxApiClient...")

    api_client = DydxApiClient()

    # Test getting server time
    logger.info("Testing get_time()...")
    time_data = api_client.get_time()
    logger.info(f"Server time: {time_data}")

    # Test getting block height
    logger.info("Testing get_height()...")
    height_data = api_client.get_height()
    logger.info(f"Block height: {height_data}")

    # Test getting markets
    logger.info("Testing get_markets()...")
    markets_data = api_client.get_markets()
    if "markets" in markets_data:
        markets = markets_data["markets"]
        logger.info(f"Available markets: {list(markets.keys())}")
    else:
        logger.error(f"Failed to get markets: {markets_data}")

    # Test getting market data for ETH-USD
    if "markets" in markets_data and "ETH-USD" in markets_data["markets"]:
        logger.info("Testing get_market() for ETH-USD...")
        market_data = api_client.get_market("ETH-USD")
        logger.info(f"ETH-USD market data: {market_data}")

    # Test getting orderbook for ETH-USD
    logger.info("Testing get_orderbook() for ETH-USD...")
    orderbook_data = api_client.get_orderbook("ETH-USD")
    logger.info(f"ETH-USD orderbook: {orderbook_data}")

    # Test getting trades for ETH-USD
    logger.info("Testing get_trades() for ETH-USD...")
    trades_data = api_client.get_trades("ETH-USD", limit=5)
    logger.info(f"ETH-USD trades: {trades_data}")

    # Test getting candles for ETH-USD
    logger.info("Testing get_candles() for ETH-USD...")
    candles_data = api_client.get_candles("ETH-USD", resolution="1MIN", limit=5)
    logger.info(f"ETH-USD candles: {candles_data}")

    logger.info("API client test completed")

def test_strategy():
    """Test the breakout strategy."""
    logger.info("Testing BreakoutStrategy...")

    api_client = DydxApiClient()
    strategy = BreakoutStrategy(
        api_client=api_client,
        market_id="ETH-USD",
        timeframe="1MIN",  # Using 1MIN for testing
        volume_factor=2.0,
        resistance_periods=24,
        risk_reward_ratio=3.0
    )

    # Test updating market data
    logger.info("Testing update_market_data()...")
    success = strategy.update_market_data()
    if success:
        logger.info(f"Market data updated successfully")
        logger.info(f"Resistance level: {strategy.resistance_level}")
        logger.info(f"Average volume: {strategy.average_volume}")
        logger.info(f"Current price: {strategy.current_price}")
    else:
        logger.error("Failed to update market data")

    # Test checking for breakout signal
    logger.info("Testing check_breakout_signal()...")
    signal, signal_details = strategy.check_breakout_signal()
    logger.info(f"Breakout signal: {signal}")
    logger.info(f"Signal details: {signal_details}")

    # Test calculating entry/exit levels
    logger.info("Testing calculate_entry_exit_levels()...")
    levels = strategy.calculate_entry_exit_levels()
    logger.info(f"Entry/exit levels: {levels}")

    logger.info("Strategy test completed")

if __name__ == "__main__":
    logger.info("Starting dYdX trading bot tests...")

    # Test API client
    test_api_client()

    # Test strategy
    test_strategy()

    logger.info("All tests completed")
