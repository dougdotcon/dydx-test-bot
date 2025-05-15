"""
Test connection to dYdX v4 testnet.
"""
import logging
import os
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
    # Import the dYdX v4 client
    from dydx_v4_python.clients import CompositeClient
    
    # Create client with testnet configuration
    client = CompositeClient(
        chain_host="test-dydx-grpc.kingnodes.com:443",
        indexer_host="https://dydx-testnet-api.polkachu.com",
        faucet_host="",
        network_id="dydx-testnet-4",
        mnemonic=mnemonic
    )
    
    logger.info("Successfully created dYdX v4 client")
    
    # Get account information
    account_info = client.get_account()
    logger.info(f"Account info: {account_info}")
    
    # Get markets
    markets = client.get_markets()
    logger.info(f"Available markets: {list(markets.keys())}")
    
    logger.info("Connection test successful!")
    
except Exception as e:
    logger.error(f"Failed to connect to dYdX v4 testnet: {str(e)}")
    exit(1)
