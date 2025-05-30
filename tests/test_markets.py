"""
Test the markets object of the indexer_client.
"""
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    # Import the CompositeClient
    from v4_client_py.clients import CompositeClient
    from v4_client_py.clients.constants import Network

    logger.info("CompositeClient imported successfully")

    # Create network configuration
    logger.info("Creating network configuration...")
    network = Network.config_network()

    # Create client
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

    # Get methods of the markets object
    logger.info("Methods available in markets object:")
    for method in dir(markets):
        if not method.startswith('__'):
            logger.info(f"  {method}")

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
