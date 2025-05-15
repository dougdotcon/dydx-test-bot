# Getting Started with dYdX v4 Trading Bot

This guide will help you set up and run the dYdX v4 Trading Bot on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A dYdX v4 testnet account
- Basic knowledge of trading concepts

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/dydx_automate.git
   cd dydx_automate
   ```

2. **Create a virtual environment (recommended)**

   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   
   - Linux/macOS:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Copy the example environment file and edit it with your credentials:

   ```bash
   cp config/.env.example config/.env
   ```

   Edit `config/.env` and add your dYdX testnet mnemonic:

   ```
   DYDX_TEST_MNEMONIC="your 24-word mnemonic here"
   LOG_LEVEL=INFO
   LOG_FILE=logs/bot.log
   ```

5. **Run the setup command**

   ```bash
   python cli.py setup
   ```

   This will check your environment and create any missing directories.

## Configuration

The bot is configured using the `config/config.json` file. The default configuration is set up for the ETH-USD market on the dYdX testnet.

Key configuration options:

- `trading.market`: The trading pair (e.g., "ETH-USD")
- `trading.volume_factor`: Volume anomaly detection threshold
- `risk.max_position_size`: Maximum position size
- `risk.max_risk_per_trade`: Maximum risk per trade as a percentage
- `execution.simulation_mode`: Whether to run in simulation mode (no real orders)

For more details, see the [Configuration Guide](configuration.md).

## Running the Bot

To start the bot with the default configuration:

```bash
python cli.py start
```

To start the bot with specific options:

```bash
python cli.py start --market ETH-USD --volume-factor 2.5 --simulation
```

## Checking Market Status

To check the status of a specific market:

```bash
python cli.py status ETH-USD
```

## Monitoring

The bot logs all activities to the console and to the log file specified in the `.env` file. Trading signals, orders, and positions are also logged to `logs/trades.log` for later analysis.

## Next Steps

- Learn about the [available trading strategies](strategies.md)
- Understand how to [configure the bot](configuration.md) for your needs
- Explore the [development guide](../development/README.md) if you want to extend the bot
