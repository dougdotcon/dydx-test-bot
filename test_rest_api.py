"""
Test connection to dYdX v4 testnet using direct REST API calls.
"""
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# API endpoints
BASE_URL = "https://indexer.v4testnet.dydx.exchange/v4"

def get_markets():
    """Get all available markets from the dYdX v4 testnet."""
    url = f"{BASE_URL}/perpetualMarkets"
    logger.info(f"Requesting markets from: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses

        data = response.json()
        logger.info(f"Successfully retrieved markets data")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get markets: {str(e)}")
        return None

def get_orderbook(market_id):
    """Get the orderbook for a specific market."""
    url = f"{BASE_URL}/orderbook/{market_id}"
    logger.info(f"Requesting orderbook for {market_id} from: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Successfully retrieved orderbook data for {market_id}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get orderbook for {market_id}: {str(e)}")
        return None

def get_candles(market_id, resolution="1MIN", limit=100):
    """Get candles for a specific market."""
    url = f"{BASE_URL}/candles/perpetualMarkets/{market_id}"
    params = {
        "resolution": resolution,
        "limit": limit
    }
    logger.info(f"Requesting candles for {market_id} from: {url}")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Successfully retrieved candles data for {market_id}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get candles for {market_id}: {str(e)}")
        return None

if __name__ == "__main__":
    # Test getting markets
    logger.info("Testing get_markets()...")
    markets_data = get_markets()
    if markets_data:
        markets = markets_data.get("markets", {})
        logger.info(f"Available markets: {list(markets.keys())}")

        # If ETH-USD market exists, get its orderbook and candles
        if "ETH-USD" in markets:
            logger.info("Testing get_orderbook() for ETH-USD...")
            orderbook_data = get_orderbook("ETH-USD")
            if orderbook_data:
                asks = orderbook_data.get("asks", [])
                bids = orderbook_data.get("bids", [])
                logger.info(f"ETH-USD orderbook: {len(asks)} asks, {len(bids)} bids")

                # Show top 3 asks and bids
                if asks:
                    logger.info(f"Top 3 asks: {asks[:3]}")
                if bids:
                    logger.info(f"Top 3 bids: {bids[:3]}")

            logger.info("Testing get_candles() for ETH-USD...")
            candles_data = get_candles("ETH-USD", resolution="5MIN", limit=10)
            if candles_data:
                candles = candles_data.get("candles", [])
                logger.info(f"Retrieved {len(candles)} candles for ETH-USD")

                # Show the most recent candle
                if candles:
                    logger.info(f"Most recent candle: {candles[0]}")

    logger.info("REST API test completed")
