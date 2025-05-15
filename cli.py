#!/usr/bin/env python3
"""
Command-line interface for the dYdX v4 trading bot.
"""

import click
import asyncio
import logging
import json
import os
from pathlib import Path

from src.core.bot import TradingBot
from src.utils.config import load_config, save_config, load_env
from src.utils.logging import setup_logging

@click.group()
def cli():
    """dYdX v4 Trading Bot - Breakout Strategy with Volume Confirmation"""
    pass

@cli.command()
@click.option(
    '--market',
    default=None,
    help='Trading pair (e.g., ETH-USD)'
)
@click.option(
    '--timeframe',
    default=None,
    help='Analysis timeframe (e.g., 5m)'
)
@click.option(
    '--volume-factor',
    default=None,
    type=float,
    help='Volume anomaly detection factor'
)
@click.option(
    '--simulation',
    is_flag=True,
    help='Run in simulation mode (no real orders)'
)
@click.option(
    '--config',
    default='config/config.json',
    help='Path to configuration file'
)
def start(market, timeframe, volume_factor, simulation, config):
    """Start the trading bot"""
    try:
        # Check if config file exists
        if not Path(config).exists():
            click.echo(f"Error: Configuration file not found: {config}")
            return

        # Set up logging
        setup_logging()

        # Update configuration with CLI parameters
        if any([market, timeframe, volume_factor, simulation]):
            config_data = load_config(config)

            if market:
                config_data['trading']['market'] = market

            if timeframe:
                config_data['trading']['timeframe'] = timeframe

            if volume_factor:
                config_data['trading']['volume_factor'] = volume_factor

            if simulation:
                if 'execution' not in config_data:
                    config_data['execution'] = {}
                config_data['execution']['simulation_mode'] = True

            # Save updated configuration
            save_config(config_data, config)

        click.echo("Starting trading bot...")

        # Start the bot
        bot = TradingBot(config)
        asyncio.run(bot.start())

    except KeyboardInterrupt:
        click.echo("\nBot interrupted by user")
    except Exception as e:
        click.echo(f"Error starting bot: {e}")
        raise

@cli.command()
@click.argument('market')
@click.option(
    '--config',
    default='config/config.json',
    help='Path to configuration file'
)
def status(market, config):
    """Check status of a specific market"""
    try:
        # Load configuration
        config_data = load_config(config)

        # Set up logging
        setup_logging()

        click.echo(f"\nMarket Status: {market}")
        click.echo("-" * 40)

        # Create a temporary bot instance to check market data
        async def check_market():
            # Initialize bot components
            from src.core.market_data import MarketDataService

            # Override market in config
            config_data['trading']['market'] = market

            # Initialize market data service
            market_data = MarketDataService(config_data)
            await market_data.connect()

            try:
                # Load initial data
                await market_data._load_initial_data()

                # Get current price
                current_price = market_data.get_current_price()

                if current_price:
                    click.echo(f"Current Price: {current_price}")

                    # Calculate technical indicators
                    volume_anomaly = market_data.calculate_volume_anomaly()
                    resistance = market_data.calculate_resistance()

                    if volume_anomaly:
                        click.echo(f"Volume Anomaly: {volume_anomaly:.2f}x average")

                    if resistance:
                        click.echo(f"Resistance Level: {resistance}")

                    # Show market data
                    click.echo(f"\nData Points: {len(market_data.prices)}")

                else:
                    click.echo("No price data available")
            finally:
                # Close connections
                await market_data.close()

        # Run the async function
        asyncio.run(check_market())

    except Exception as e:
        click.echo(f"Error checking market status: {e}")

@cli.command()
def version():
    """Show bot version"""
    click.echo("dYdX Trading Bot v1.0.0")

@cli.command()
@click.option('--check', is_flag=True, help='Only check configuration without setup')
def setup(check):
    """Configure or verify the bot environment"""
    try:
        # Load environment variables
        try:
            load_env()
        except FileNotFoundError:
            pass  # We'll check for this file below

        # Check required files
        files_to_check = [
            ('config/config.json', 'Configuration file'),
            ('config/.env', 'Environment variables file'),
            ('requirements.txt', 'Dependencies file')
        ]

        click.echo("\nChecking environment...")
        all_ok = True

        for file_path, description in files_to_check:
            exists = Path(file_path).exists()
            status = '✓' if exists else '✗'
            click.echo(f"{status} {description}: {file_path}")
            if not exists and file_path == 'config/.env':
                if Path('config/.env.example').exists():
                    click.echo("  → Copy .env.example to .env and configure your credentials")
                all_ok = False

        # Check required environment variables
        if Path('config/.env').exists():
            required_env = ['DYDX_TEST_MNEMONIC']
            missing_env = [env for env in required_env if not os.getenv(env)]
            if missing_env:
                all_ok = False
                click.echo("\nMissing environment variables:")
                for env in missing_env:
                    click.echo(f"✗ {env}")

        # Check directory structure
        directories_to_check = [
            ('src/clients', 'API clients directory'),
            ('src/core', 'Core modules directory'),
            ('src/strategies', 'Trading strategies directory'),
            ('src/models', 'Data models directory'),
            ('src/utils', 'Utilities directory'),
            ('tests', 'Tests directory'),
            ('logs', 'Logs directory')
        ]

        click.echo("\nChecking directory structure...")
        for dir_path, description in directories_to_check:
            exists = Path(dir_path).exists()
            status = '✓' if exists else '✗'
            click.echo(f"{status} {description}: {dir_path}")
            if not exists:
                all_ok = False

        if check:
            if all_ok:
                click.echo("\nAll checks passed successfully!")
            else:
                click.echo("\nSome checks failed. Fix the issues before starting the bot.")
            return

        # If not just checking, continue with setup
        if not all_ok:
            if not click.confirm("\nDo you want to continue with setup?", default=True):
                return

        click.echo("\nPerforming setup...")

        # Create missing directories
        for dir_path, description in directories_to_check:
            if not Path(dir_path).exists():
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                click.echo(f"Created directory: {dir_path}")

        # Create .env file from example if it doesn't exist
        if not Path('config/.env').exists() and Path('config/.env.example').exists():
            if click.confirm("Create .env file from .env.example?", default=True):
                with open('config/.env.example', 'r') as example_file:
                    example_content = example_file.read()

                with open('config/.env', 'w') as env_file:
                    env_file.write(example_content)

                click.echo("Created .env file. Please edit it with your credentials.")

        click.echo("\nSetup completed. You may need to install dependencies:")
        click.echo("pip install -r requirements.txt")

    except Exception as e:
        click.echo(f"Error during setup: {e}")

if __name__ == '__main__':
    cli()