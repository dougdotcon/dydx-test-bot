# Configuration Guide

This guide explains how to configure the dYdX v4 Trading Bot for your specific needs.

## Configuration File

The bot is primarily configured through the `config/config.json` file. This file contains all the settings for the bot, including trading parameters, risk management, network endpoints, and debugging options.

Here's an example configuration file with explanations for each section:

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
  "technical": {
    "resistance_period": 24,
    "volume_lookback": 20
  },
  "network": {
    "chain_id": "dydx-testnet-4",
    "endpoints": {
      "rest": "https://dydx-testnet-rpc.polkachu.com",
      "ws": "wss://dydx-testnet-rpc.polkachu.com/websocket",
      "indexer": "https://dydx-testnet-rpc.polkachu.com"
    }
  },
  "execution": {
    "simulation_mode": true
  },
  "debug": {
    "log_api_responses": true,
    "log_market_data": true,
    "save_trades_history": true,
    "ssl_verify": false
  },
  "rpc": {
    "retry_attempts": 3,
    "retry_delay": 1,
    "timeout": 10,
    "subscribe_channels": [
      "trades",
      "orderbook",
      "markets"
    ]
  }
}
```

### Trading Section

- `market`: The trading pair to trade (e.g., "ETH-USD")
- `timeframe`: The timeframe for analysis (e.g., "5m" for 5 minutes)
- `volume_factor`: The volume anomaly detection threshold. A value of 2.5 means the current volume must be 2.5 times the average volume to trigger a breakout signal.
- `risk_reward_ratio`: The risk-to-reward ratio for calculating take profit levels. A value of 3.0 means the take profit will be set at 3 times the distance from entry to stop loss.

### Risk Section

- `max_position_size`: The maximum position size in the base asset (e.g., 0.1 ETH)
- `max_risk_per_trade`: The maximum risk per trade as a percentage of account equity (e.g., 0.02 = 2%)

### Technical Section

- `resistance_period`: The number of periods to look back for calculating resistance levels
- `volume_lookback`: The number of periods to look back for calculating average volume

### Network Section

- `chain_id`: The dYdX chain ID (e.g., "dydx-testnet-4" for testnet)
- `endpoints`: The API endpoints for connecting to the dYdX network
  - `rest`: The REST API endpoint
  - `ws`: The WebSocket endpoint
  - `indexer`: The indexer endpoint

### Execution Section

- `simulation_mode`: Whether to run in simulation mode (true) or place real orders (false)

### Debug Section

- `log_api_responses`: Whether to log API responses
- `log_market_data`: Whether to log market data
- `save_trades_history`: Whether to save trade history
- `ssl_verify`: Whether to verify SSL certificates (should be true in production)

### RPC Section

- `retry_attempts`: The number of retry attempts for failed API requests
- `retry_delay`: The delay between retry attempts in seconds
- `timeout`: The timeout for API requests in seconds
- `subscribe_channels`: The WebSocket channels to subscribe to

## Environment Variables

In addition to the configuration file, the bot also uses environment variables for sensitive information and runtime configuration. These are stored in the `config/.env` file.

Example `.env` file:

```
# dYdX v4 Testnet Credentials
DYDX_TEST_MNEMONIC="word1 word2 word3 ... word24"

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Alerts (optional)
# TELEGRAM_BOT_TOKEN=your_token_here
# TELEGRAM_CHAT_ID=your_chat_id_here
```

### Environment Variables Reference

- `DYDX_TEST_MNEMONIC`: Your dYdX testnet mnemonic (24 words)
- `LOG_LEVEL`: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE`: The path to the log file
- `TELEGRAM_BOT_TOKEN`: (Optional) Telegram bot token for alerts
- `TELEGRAM_CHAT_ID`: (Optional) Telegram chat ID for alerts

## Command-Line Options

You can override some configuration options when starting the bot using command-line options:

```bash
python cli.py start --market ETH-USD --volume-factor 2.5 --simulation
```

Available options:

- `--market`: Override the trading pair
- `--timeframe`: Override the analysis timeframe
- `--volume-factor`: Override the volume anomaly detection threshold
- `--simulation`: Run in simulation mode (no real orders)
- `--config`: Specify a different configuration file path

## Configuration Best Practices

1. **Start with simulation mode**: Always start with `simulation_mode: true` until you're confident in your strategy.
2. **Use testnet first**: Test your configuration on the dYdX testnet before using real funds.
3. **Conservative risk settings**: Start with conservative risk settings (e.g., `max_risk_per_trade: 0.01` for 1% risk).
4. **Regular backups**: Regularly back up your configuration and environment files.
5. **Secure your mnemonic**: Never share your mnemonic or commit it to version control.
