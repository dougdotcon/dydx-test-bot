"""
Check the network configuration.
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
    from v4_client_py.clients.constants import Network
    
    logger.info("Network class imported successfully")
    
    # Create network configuration
    logger.info("Creating network configuration...")
    network = Network.config_network()
    
    # Print network configuration
    logger.info(f"Network configuration: {network}")
    
    # Print network attributes
    logger.info("Network attributes:")
    for attr in dir(network):
        if not attr.startswith('__'):
            value = getattr(network, attr)
            logger.info(f"  {attr}: {value}")
    
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
except Exception as e:
    logger.error(f"Error: {str(e)}")
