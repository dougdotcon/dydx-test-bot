"""
Main bot implementation for dYdX trading.
"""
import logging
import time
import argparse
from typing import Dict, Optional

from dydx_api import DydxApiClient
from breakout_strategy import BreakoutStrategy
from position_manager import PositionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dydx_bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DydxTradingBot:
    """
    Trading bot for dYdX v4 using breakout strategy.
    """

    def __init__(self, market_id: str, timeframe: str = "1MIN",
                 volume_factor: float = 2.0, resistance_periods: int = 24,
                 risk_reward_ratio: float = 3.0, position_size_usd: float = 100.0,
                 update_interval: int = 60, api_url: str = "https://dydx-testnet.imperator.co/v4"):
        """
        Initialize the trading bot.

        Args:
            market_id: Market ID (e.g., "ETH-USD")
            timeframe: Candle timeframe (e.g., "1MIN", "5MINS", "15MINS", "30MINS", "1HOUR", "4HOURS", "1DAY")
            volume_factor: Factor by which volume should exceed average to confirm breakout
            resistance_periods: Number of periods to look back for resistance
            risk_reward_ratio: Risk-to-reward ratio for take profit calculation
            position_size_usd: Position size in USD
            update_interval: Interval in seconds between market data updates
            api_url: URL of the dYdX API
        """
        self.market_id = market_id
        self.timeframe = timeframe
        self.volume_factor = volume_factor
        self.resistance_periods = resistance_periods
        self.risk_reward_ratio = risk_reward_ratio
        self.position_size_usd = position_size_usd
        self.update_interval = update_interval

        # Initialize API client
        self.api_client = DydxApiClient(base_url=api_url)

        # Initialize strategy
        self.strategy = BreakoutStrategy(
            api_client=self.api_client,
            market_id=market_id,
            timeframe=timeframe,
            volume_factor=volume_factor,
            resistance_periods=resistance_periods,
            risk_reward_ratio=risk_reward_ratio
        )

        # Initialize position manager
        self.position_manager = PositionManager(
            api_client=self.api_client,
            market_id=market_id,
            position_size_usd=position_size_usd
        )

        # Bot state
        self.running = False
        self.last_update_time = 0

    def start(self):
        """
        Start the trading bot.
        """
        self.running = True
        logger.info(f"Starting dYdX Trading Bot for {self.market_id}")
        logger.info(f"Parameters: Timeframe={self.timeframe}, Volume Factor={self.volume_factor}, "
                   f"Resistance Periods={self.resistance_periods}, Risk:Reward={self.risk_reward_ratio}, "
                   f"Position Size=${self.position_size_usd}, Update Interval={self.update_interval}s")

        try:
            # Initial market data update
            success = self.strategy.update_market_data()
            if not success:
                logger.error("Failed to update initial market data. Exiting.")
                return

            # Get server time
            time_data = self.api_client.get_time()
            if "iso" in time_data:
                logger.info(f"Server time: {time_data['iso']}")

            # Get market info
            market_data = self.api_client.get_market(self.market_id)
            if "oraclePrice" in market_data:
                logger.info(f"Current {self.market_id} price: {market_data['oraclePrice']}")

            logger.info(f"Bot started successfully. Monitoring {self.market_id} for breakout opportunities...")
            logger.info(f"Initial resistance level: {self.strategy.resistance_level:.2f}, "
                       f"Average volume: {self.strategy.average_volume:.4f}")

            self.last_update_time = time.time()

            # Main loop
            while self.running:
                current_time = time.time()

                # Update market data at regular intervals
                if current_time - self.last_update_time >= self.update_interval:
                    logger.info("Updating market data...")
                    self.strategy.update_market_data()
                    self.last_update_time = current_time

                    # Log current state
                    logger.info(f"Current price: {self.strategy.current_price:.2f}, "
                               f"Resistance: {self.strategy.resistance_level:.2f}, "
                               f"Avg Volume: {self.strategy.average_volume:.4f}")

                # Check for exit conditions if there's an active position
                if self.position_manager.active_position:
                    # Check exit conditions
                    exit_reason = self.position_manager.check_exit_conditions(self.strategy.current_price)
                    if exit_reason:
                        closed_position = self.position_manager.close_position(
                            exit_price=self.strategy.current_price,
                            reason=exit_reason
                        )
                        logger.info(f"Position closed: {closed_position}")

                        # Calculate profit/loss
                        pnl = closed_position.get("pnl", 0)
                        pnl_percent = closed_position.get("pnl_percent", 0)
                        logger.info(f"Profit/Loss: ${pnl:.2f} ({pnl_percent:.2f}%)")

                        # Wait before looking for new opportunities
                        cooldown_time = 300  # 5 minutes
                        logger.info(f"Waiting {cooldown_time} seconds before looking for new opportunities...")
                        time.sleep(cooldown_time)

                        # Update market data after waiting
                        self.strategy.update_market_data()
                        self.last_update_time = time.time()

                # If no active position, look for new opportunities
                else:
                    # Check for breakout signal
                    signal, signal_details = self.strategy.check_breakout_signal()

                    if signal:
                        logger.info("Breakout signal detected!")
                        logger.info(f"Signal details: {signal_details}")

                        # Calculate entry, stop loss, and take profit levels
                        levels = self.strategy.calculate_entry_exit_levels()

                        # Open long position
                        position = self.position_manager.open_long_position(
                            entry_price=levels["entry_price"],
                            stop_loss=levels["stop_loss"],
                            take_profit=levels["take_profit"]
                        )

                        logger.info(f"Opened position: {position}")
                        logger.info(f"Entry: {levels['entry_price']:.2f}, "
                                   f"Stop Loss: {levels['stop_loss']:.2f}, "
                                   f"Take Profit: {levels['take_profit']:.2f}, "
                                   f"Risk: {levels['risk']:.2f}, "
                                   f"Reward: {levels['reward']:.2f}")

                # Sleep for a short time before next iteration
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        finally:
            # Clean up
            self.stop()

    def stop(self):
        """
        Stop the trading bot.
        """
        self.running = False

        # Close any open positions
        if self.position_manager.active_position:
            logger.info("Closing active position before exit...")
            self.position_manager.close_position(
                exit_price=self.strategy.current_price,
                reason="bot_shutdown"
            )

        logger.info("Bot shutdown complete.")

def parse_args():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="dYdX Trading Bot - Breakout Strategy")

    parser.add_argument("--market", default="ETH-USD", help="Market symbol (e.g., 'ETH-USD')")
    parser.add_argument("--timeframe", default="1MIN", help="Candle timeframe (e.g., '1MIN', '5MINS')")
    parser.add_argument("--volume-factor", type=float, default=2.0, help="Volume factor for breakout confirmation")
    parser.add_argument("--resistance-periods", type=int, default=24, help="Number of periods to look back for resistance")
    parser.add_argument("--risk-reward", type=float, default=3.0, help="Risk-to-reward ratio for take profit calculation")
    parser.add_argument("--position-size", type=float, default=100.0, help="Position size in USD")
    parser.add_argument("--update-interval", type=int, default=60, help="Interval in seconds between market data updates")
    parser.add_argument("--api-url", default="https://dydx-testnet.imperator.co/v4", help="URL of the dYdX API")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    bot = DydxTradingBot(
        market_id=args.market,
        timeframe=args.timeframe,
        volume_factor=args.volume_factor,
        resistance_periods=args.resistance_periods,
        risk_reward_ratio=args.risk_reward,
        position_size_usd=args.position_size,
        update_interval=args.update_interval,
        api_url=args.api_url
    )

    bot.start()
