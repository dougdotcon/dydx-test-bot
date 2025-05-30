# dYdX v4 Trading Bot - Breakout Strategy

A simple CLI trading bot for dYdX v4 that implements a breakout strategy with volume confirmation.

## Features

- Monitors price and volume data from dYdX v4 testnet
- Detects breakout signals when price breaks resistance with high volume
- Automatically calculates stop-loss and take-profit levels using 1:3 risk-reward ratio
- Executes trades and manages positions
- Supports simulation mode for testing without placing real orders
- Command-line interface for easy configuration and control

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/dydx-trading-bot.git
   cd dydx-trading-bot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your configuration:
   ```
   python main.py setup
   ```
   This will prompt you for your dYdX mnemonic and create a `.env` file.

   Alternatively, you can copy the `.env.example` file to `.env` and edit it manually:
   ```
   cp .env.example .env
   ```

## Usage

### Starting the Bot

```
python main.py start [OPTIONS]
```

Options:
- `--market TEXT`: Market symbol (e.g., "ETH-USD") [default: ETH-USD]
- `--timeframe TEXT`: Candle timeframe (e.g., "5m") [default: 5m]
- `--volume-factor FLOAT`: Volume factor for breakout confirmation [default: 2.0]
- `--resistance-periods INTEGER`: Number of periods to look back for resistance [default: 24]
- `--risk-reward FLOAT`: Risk-to-reward ratio for take profit calculation [default: 3.0]
- `--position-size FLOAT`: Position size in USD [default: 100]
- `--simulation / --live`: Simulation mode (no real orders) [default: --simulation]

Example:
```
python main.py start --market BTC-USD --timeframe 15m --volume-factor 2.5 --position-size 50 --simulation
```

### Checking Status

```
python main.py status
```

This will display information about your account and any open positions.

### Setting Up Configuration

```
python main.py setup
```

This will guide you through setting up your dYdX mnemonic.

## How It Works

1. The bot monitors price and volume data for the specified market
2. It identifies resistance levels based on recent price history
3. When price breaks above resistance with volume higher than the average by the specified factor, a breakout signal is generated
4. The bot opens a long position at the current price
5. Stop-loss is set just below the resistance level
6. Take-profit is set at a distance that is the risk-reward ratio times the risk
7. The bot continuously monitors the position until either stop-loss or take-profit is hit

## Important Notes

- This bot is designed for educational purposes and should be used at your own risk
- Always start with simulation mode to test the strategy before using real funds
- The bot currently only supports the dYdX v4 testnet
- Your mnemonic is stored locally in the `.env` file - keep it secure!

## License

MIT

## Acknowledgements

- dYdX Protocol for providing the v4 client and documentation
- This project was inspired by the breakout trading strategy described in the dYdX documentation
