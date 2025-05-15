# dYdX v4 Trading Bot

A modular, extensible trading bot for the dYdX v4 protocol (testnet), implementing a breakout strategy with volume confirmation.

## Overview

This project implements an automated trading bot for dYdX v4 (testnet). The bot monitors the market, detects potential breakouts (based on price and volume anomalies), and executes buy orders via the REST API. The project follows a modular architecture and best development practices (logging, error handling, CLI, etc.).

## Key Features

- Real-time market data monitoring via WebSocket and REST API
- Breakout trading strategy with volume confirmation
- Risk management with configurable position sizing
- Simulation mode for testing without placing real orders
- Comprehensive logging and trade history
- Modular architecture for easy extension

## Requirements

- Python 3.8 or higher
- pip (package manager)
- dYdX v4 testnet account
- (Optional) Mnemonic for authentication (if required by the API)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/dydx_automate.git
   cd dydx_automate
   ```

2. **Create a virtual environment (recommended):**
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

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp config/.env.example config/.env
   ```
   Edit `config/.env` and add your dYdX testnet mnemonic.

5. **Run the setup command:**
   ```bash
   python cli.py setup
   ```

6. **Start the bot:**
   ```bash
   python cli.py start --simulation
   ```

## Project Structure

The bot follows a modular architecture with clear separation of concerns:

```
dydx_automate/
├── config/                 # Configuration files
├── docs/                   # Documentation
├── logs/                   # Log files
├── src/                    # Source code
│   ├── clients/            # API clients
│   ├── core/               # Core functionality
│   ├── models/             # Data models
│   ├── strategies/         # Trading strategies
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── cli.py                  # Command-line interface
└── requirements.txt        # Dependencies
```

## Configuration

The bot is configured using the `config/config.json` file. Example configuration:

```json
{
  "trading": {
    "market": "ETH-USD",
    "timeframe": "5m",
    "volume_factor": 2.5,
    "risk_reward_ratio": 3.0
  },
  "risk": {
    "max_position_size": 0.1,
    "max_risk_per_trade": 0.02
  },
  "network": {
    "endpoints": {
      "rest": "https://dydx-testnet-rpc.polkachu.com",
      "ws": "wss://dydx-testnet-rpc.polkachu.com/websocket"
    }
  },
  "execution": {
    "simulation_mode": true
  }
}
```

## Command-Line Interface

The bot provides a command-line interface for easy control:

```bash
# Start the bot
python cli.py start

# Start with specific options
python cli.py start --market ETH-USD --volume-factor 2.5 --simulation

# Check market status
python cli.py status ETH-USD

# Show bot version
python cli.py version

# Set up the environment
python cli.py setup
```

## Documentation

Comprehensive documentation is available in the `docs` directory:

- [Getting Started](docs/guides/getting-started.md): Quick start guide
- [Configuration](docs/guides/configuration.md): Detailed configuration information
- [Trading Strategies](docs/guides/strategies.md): Available trading strategies
- [API Reference](docs/api/README.md): dYdX v4 API reference
- [Development Guide](docs/development/README.md): Guide for developers
- [Project Status](docs/development/status.md): Current status and roadmap

## Testing

The bot includes a test suite using pytest. To run the tests:

```bash
pytest
```

## Security

- **Authentication:** If the dYdX API requires authentication (mnemonic or private key), store it in a `.env` file (never in logs or code).
- **Simulation Mode:** It's recommended to use simulation mode (`--simulation` flag) to avoid accidental orders in a real environment.
- **Sensitive Data:** Ensure that sensitive data (mnemonic, keys) are never logged.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests with improvements, fixes, or new features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note:**
This README provides an overview of the project. For detailed information, please refer to the documentation in the `docs` directory.