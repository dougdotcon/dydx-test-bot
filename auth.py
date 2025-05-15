"""
Authentication module for connecting to dYdX v4.
"""
import logging
from typing import Optional

from dydx_v4_python.clients import CompositeClient
import config

logger = logging.getLogger(__name__)

def create_client() -> Optional[CompositeClient]:
    """
    Create and initialize a dYdX client using the configured mnemonic.

    Returns:
        CompositeClient: Initialized dYdX client or None if authentication fails
    """
    try:
        if not config.MNEMONIC:
            logger.error("No mnemonic provided. Please set the DYDX_MNEMONIC environment variable.")
            return None

        # Create client with testnet configuration
        client = CompositeClient(
            chain_host=config.TESTNET_ENDPOINTS["GRPC"],
            indexer_host=config.TESTNET_ENDPOINTS["REST"],
            faucet_host=config.TESTNET_ENDPOINTS.get("FAUCET", ""),
            network_id=config.CHAIN_ID,
            mnemonic=config.MNEMONIC
        )

        logger.info(f"Successfully connected to dYdX {config.NETWORK}")
        return client

    except Exception as e:
        logger.error(f"Failed to create dYdX client: {str(e)}")
        return None

def get_account_info(client: CompositeClient) -> dict:
    """
    Get account information from dYdX.

    Args:
        client: Initialized dYdX client

    Returns:
        dict: Account information
    """
    try:
        # Get the subaccount 0 by default
        subaccount_id = 0

        # Get account information
        account_info = client.get_account()

        # Get balance information
        balance_info = client.get_subaccount_balance(subaccount_id)

        return {
            "account_info": account_info,
            "balance": balance_info
        }

    except Exception as e:
        logger.error(f"Failed to get account info: {str(e)}")
        return {}
