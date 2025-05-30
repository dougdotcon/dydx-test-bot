"""
Configuration settings for the dYdX trading bot.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# dYdX network settings
NETWORK = "testnet"  # Options: "testnet", "mainnet"
CHAIN_ID = "dydx-testnet-4"

# API endpoints
TESTNET_ENDPOINTS = {
    "REST": "https://dydx-testnet-api.polkachu.com",
    "GRPC": "test-dydx-grpc.kingnodes.com:443",
    "INDEXER_WS": "wss://indexer.v4testnet.dydx.exchange/v4/ws"
}

# Authentication
MNEMONIC = os.getenv("DYDX_MNEMONIC", "")

# Trading parameters
DEFAULT_MARKET = "ETH-USD"
DEFAULT_TIMEFRAME = "5m"  # Options: "1m", "5m", "15m", "1h", "4h", "1d"
DEFAULT_VOLUME_FACTOR = 2.0  # Volume must be this times the average to confirm breakout
DEFAULT_RESISTANCE_PERIODS = 24  # Number of periods to look back for resistance
DEFAULT_RISK_REWARD_RATIO = 3.0  # Take profit at 3x the risk
DEFAULT_POSITION_SIZE_USD = 100  # Position size in USD

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "logs", "dydx_bot.log")
