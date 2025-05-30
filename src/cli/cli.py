"""
Command-line interface for the dYdX trading bot.
"""
import logging
import click
import time
import os
from typing import Dict, Optional

from ..core import config
from ..core.auth import create_client, get_account_info
from ..core.market_data import MarketData
from ..strategies.strategy import BreakoutStrategy
from ..core.order_manager import OrderManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@click.group()
def cli():
    """dYdX Trading Bot - Breakout Strategy with Volume Confirmation"""
    pass

@cli.command()
@click.option('--market', default=config.DEFAULT_MARKET, help='Market symbol (e.g., "ETH-USD")')
@click.option('--timeframe', default=config.DEFAULT_TIMEFRAME, help='Candle timeframe (e.g., "5m")')
@click.option('--volume-factor', default=config.DEFAULT_VOLUME_FACTOR, type=float,
              help='Volume factor for breakout confirmation')
@click.option('--resistance-periods', default=config.DEFAULT_RESISTANCE_PERIODS, type=int,
              help='Number of periods to look back for resistance')
@click.option('--risk-reward', default=config.DEFAULT_RISK_REWARD_RATIO, type=float,
              help='Risk-to-reward ratio for take profit calculation')
@click.option('--position-size', default=config.DEFAULT_POSITION_SIZE_USD, type=float,
              help='Position size in USD')
@click.option('--simulation/--live', default=True, help='Simulation mode (no real orders)')
def start(market, timeframe, volume_factor, resistance_periods, risk_reward, position_size, simulation):
    """Start the trading bot with the specified parameters."""
    logger.info("Starting dYdX Trading Bot...")
    logger.info(f"Parameters: Market={market}, Timeframe={timeframe}, Volume Factor={volume_factor}, "
               f"Resistance Periods={resistance_periods}, Risk:Reward={risk_reward}, "
               f"Position Size=${position_size}, Simulation={simulation}")

    # Create dYdX client
    client = create_client()
    if not client:
        logger.error("Failed to create dYdX client. Exiting.")
        return

    # Get account info
    account_info = get_account_info(client)
    logger.info(f"Account info: {account_info}")

    # Initialize market data collector
    market_data = MarketData(client, market=market, timeframe=timeframe)

    # Initialize strategy
    strategy = BreakoutStrategy(
        market_data=market_data,
        volume_factor=volume_factor,
        resistance_periods=resistance_periods,
        risk_reward_ratio=risk_reward
    )

    # Initialize order manager
    order_manager = OrderManager(
        client=client,
        market=market,
        position_size_usd=position_size,
        simulation_mode=simulation
    )

    # Start WebSocket for real-time data
    market_data.start_websocket()

    try:
        # Initial market data update
        strategy.update_market_data()

        logger.info(f"Bot started successfully. Monitoring {market} for breakout opportunities...")
        logger.info(f"Initial resistance level: {strategy.resistance_level:.2f}, "
                   f"Average volume: {strategy.average_volume:.2f}")

        # Main loop
        while True:
            # Check for exit conditions if there's an active position
            if order_manager.active_position:
                exit_reason = order_manager.check_exit_conditions()
                if exit_reason:
                    closed_position = order_manager.close_position(exit_reason)
                    logger.info(f"Position closed: {closed_position}")

                    # Wait before looking for new opportunities
                    logger.info("Waiting 5 minutes before looking for new opportunities...")
                    time.sleep(300)  # 5 minutes

                    # Update market data after waiting
                    strategy.update_market_data()

            # If no active position, look for new opportunities
            else:
                # Update market data every minute
                strategy.update_market_data()

                # Check for breakout signal
                signal, signal_details = strategy.check_breakout_signal()

                if signal:
                    # Calculate entry, stop loss, and take profit levels
                    current_price = signal_details["current_price"]
                    levels = strategy.calculate_entry_exit_levels(current_price)

                    # Open long position
                    position = order_manager.open_long_position(
                        entry_price=levels["entry_price"],
                        stop_loss=levels["stop_loss"],
                        take_profit=levels["take_profit"]
                    )

                    logger.info(f"Opened position: {position}")

            # Sleep for a short time before next iteration
            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}", exc_info=True)
    finally:
        # Clean up
        market_data.stop_websocket()

        # Close any open positions
        if order_manager.active_position:
            logger.info("Closing active position before exit...")
            order_manager.close_position("bot_shutdown")

        logger.info("Bot shutdown complete.")

@cli.command()
def setup():
    """Setup the bot configuration."""
    click.echo("Setting up dYdX Trading Bot...")

    # Check if .env file exists
    if os.path.exists(".env"):
        overwrite = click.confirm("Configuration file already exists. Overwrite?", default=False)
        if not overwrite:
            click.echo("Setup cancelled.")
            return

    # Get mnemonic
    mnemonic = click.prompt("Enter your dYdX mnemonic (24 words)", hide_input=True)

    # Create .env file
    with open(".env", "w") as f:
        f.write(f"DYDX_MNEMONIC={mnemonic}\n")

    click.echo("Configuration saved to .env file.")
    click.echo("IMPORTANT: Keep your mnemonic secure and never share it with anyone!")

@cli.command()
def status():
    """Check the status of the bot and account."""
    click.echo("Checking dYdX Trading Bot status...")

    # Create dYdX client
    client = create_client()
    if not client:
        click.echo("Failed to create dYdX client. Check your configuration.")
        return

    # Get account info
    account_info = get_account_info(client)

    click.echo("\n=== Account Information ===")
    if "balance" in account_info:
        click.echo(f"Balance: {account_info['balance']} USDC")

    # Get positions
    order_manager = OrderManager(client, simulation_mode=False)
    positions = order_manager.get_positions()

    click.echo("\n=== Open Positions ===")
    if positions:
        for pos in positions:
            click.echo(f"Market: {pos.get('market')}")
            click.echo(f"Side: {pos.get('side')}")
            click.echo(f"Size: {pos.get('size')}")
            click.echo(f"Entry Price: {pos.get('entry_price')}")
            click.echo("---")
    else:
        click.echo("No open positions.")

    click.echo("\nStatus check complete.")

if __name__ == '__main__':
    cli()
