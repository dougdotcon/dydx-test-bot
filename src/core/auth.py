"""
Authentication module for connecting to dYdX v4.
"""
import logging
from typing import Optional

from .dydx_client import DydxClientWrapper
from . import config

logger = logging.getLogger(__name__)

def create_client(simulation_mode: bool = True) -> Optional[DydxClientWrapper]:
    """
    Create and initialize a dYdX client using the configured mnemonic.

    Args:
        simulation_mode: If True, run in simulation mode

    Returns:
        Optional[DydxClientWrapper]: Initialized client or None if failed
    """
    try:
        # Create client wrapper
        client = DydxClientWrapper(simulation_mode=simulation_mode)

        # Get mnemonic from environment
        mnemonic = config.MNEMONIC
        if not mnemonic and not simulation_mode:
            logger.error("DYDX_MNEMONIC not found in environment variables")
            return None

        # Connect to dYdX
        if client.connect(mnemonic):
            logger.info(f"dYdX client created successfully (simulation_mode={simulation_mode})")
            return client
        else:
            logger.error("Failed to connect to dYdX")
            return None

    except Exception as e:
        logger.error(f"Failed to create dYdX client: {str(e)}")
        return None

def get_account_info(client: DydxClientWrapper) -> dict:
    """
    Get account information from dYdX.

    Args:
        client: Initialized dYdX client

    Returns:
        dict: Account information
    """
    try:
        # Get account information using the wrapper
        account_info = client.get_account_info()

        if account_info:
            logger.info("Successfully retrieved account information")
            return account_info
        else:
            logger.error("Failed to retrieve account information")
            return {}

    except Exception as e:
        logger.error(f"Failed to get account info: {str(e)}")
        return {}
