"""
Test creating a custom network configuration.
"""
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    # Import the Network class
    from v4_client_py.clients.constants import Network, ValidatorConfig, IndexerConfig
    from v4_client_py.clients import CompositeClient
    
    logger.info("Classes imported successfully")
    
    # Create custom network configuration
    logger.info("Creating custom network configuration...")
    
    validator_config = ValidatorConfig(
        rest_endpoint="https://dydx-testnet-api.polkachu.com",
        grpc_endpoint="test-dydx-grpc.kingnodes.com:443",
        chain_id="dydx-testnet-4"
    )
    
    indexer_config = IndexerConfig(
        rest_endpoint="https://dydx-testnet-api.polkachu.com"
    )
    
    network = Network(
        env="testnet",
        validator_config=validator_config,
        indexer_config=indexer_config,
        faucet_endpoint=None
    )
    
    logger.info(f"Custom network configuration created: {network}")
    
    # Create client with custom network configuration
    logger.info("Creating dYdX v4 client...")
    client = CompositeClient(
        network=network,
        api_timeout=10  # 10 seconds timeout
    )
    
    logger.info("Successfully created dYdX v4 client")
    
    # Get indexer client
    logger.info("Getting indexer client...")
    indexer_client = client.indexer_client
    
    # Get markets object
    logger.info("Getting markets object...")
    markets = indexer_client.markets
    
    # Try to get markets
    logger.info("Trying to get perpetual markets...")
    try:
        markets_list = markets.get_perpetual_markets()
        logger.info(f"Markets: {markets_list}")
    except Exception as e:
        logger.error(f"Failed to get markets: {str(e)}")
    
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
except Exception as e:
    logger.error(f"Error: {str(e)}")
