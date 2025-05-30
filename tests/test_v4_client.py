"""
Test connection to dYdX v4 testnet using v4-client-py.
"""
import logging
import os
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get mnemonic from environment
mnemonic = os.getenv("DYDX_MNEMONIC", "")

if not mnemonic:
    logger.error("No mnemonic provided. Please set the DYDX_MNEMONIC environment variable.")
    exit(1)

try:
    # Import the CompositeClient
    from v4_client_py.clients import CompositeClient
    logger.info("CompositeClient imported successfully")

    # Import Network class
    from v4_client_py.clients.constants import Network

    # Create network configuration for testnet
    logger.info("Creating network configuration...")
    network = Network.testnet()

    # Create client with testnet configuration
    logger.info("Creating dYdX v4 client...")
    client = CompositeClient(
        network=network,
        api_timeout=10  # 10 seconds timeout
    )

    logger.info("Successfully created dYdX v4 client")

    # Get account information
    logger.info("Getting account information...")
    account_info = client.get_account()
    logger.info(f"Account info: {account_info}")

    # Get markets
    logger.info("Getting markets...")
    markets = client.get_markets()
    logger.info(f"Available markets: {list(markets.keys())}")

    # Get ETH-USD market
    logger.info("Getting ETH-USD market details...")
    eth_market = markets.get("ETH-USD")
    if eth_market:
        logger.info(f"ETH-USD market: {eth_market}")
    else:
        logger.warning("ETH-USD market not found")

    logger.info("Connection test successful!")

except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    exit(1)
except Exception as e:
    logger.error(f"Error: {str(e)}")
    exit(1)
