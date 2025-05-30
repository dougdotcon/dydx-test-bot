"""
Check the methods available in CompositeClient.
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
    
    # Get methods of the client
    logger.info("Methods available in CompositeClient:")
    for method in dir(client):
        if not method.startswith('__'):
            logger.info(f"  {method}")
    
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
except Exception as e:
    logger.error(f"Error: {str(e)}")
