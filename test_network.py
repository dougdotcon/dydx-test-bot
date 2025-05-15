"""
Test creating a Network object.
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
    
    # Create a Network object for testnet
    logger.info("Creating Network object...")
    
    # Try different approaches
    
    # Approach 1: Call config_network directly
    logger.info("Approach 1: Call config_network directly")
    try:
        network1 = Network.config_network()
        logger.info(f"network1: {network1}")
    except Exception as e:
        logger.error(f"Approach 1 failed: {str(e)}")
    
    # Approach 2: Create an instance of Network
    logger.info("Approach 2: Create an instance of Network")
    try:
        network2 = Network()
        logger.info(f"network2: {network2}")
    except Exception as e:
        logger.error(f"Approach 2 failed: {str(e)}")
    
    # Approach 3: Look for constants in Network
    logger.info("Approach 3: Look for constants in Network")
    try:
        for attr in dir(Network):
            if not attr.startswith('__'):
                value = getattr(Network, attr)
                logger.info(f"  {attr}: {value}")
    except Exception as e:
        logger.error(f"Approach 3 failed: {str(e)}")
    
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
except Exception as e:
    logger.error(f"Error: {str(e)}")
