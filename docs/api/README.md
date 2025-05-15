# dYdX v4 API Reference

This document provides reference information for the dYdX v4 API endpoints used by the trading bot.

## API Endpoints

The dYdX v4 API consists of several components:

- **REST API**: Used for retrieving market data, account information, and placing orders
- **WebSocket API**: Used for real-time market data updates
- **Cosmos RPC**: Used for blockchain interactions

### REST API Endpoints

The bot uses the following REST API endpoints:

| Endpoint | Description |
|----------|-------------|
| `/perpetual/markets` | Get information about all markets |
| `/perpetual/markets/{market}/orderbook` | Get the orderbook for a specific market |
| `/perpetual/markets/{market}/trades` | Get recent trades for a specific market |
| `/perpetual/orders` | Place an order |
| `/perpetual/account` | Get account information |
| `/perpetual/positions` | Get open positions |

### WebSocket Channels

The bot subscribes to the following WebSocket channels:

| Channel | Description |
|---------|-------------|
| `trades` | Real-time trade updates |
| `orderbook` | Real-time orderbook updates |
| `markets` | Market data updates |

## Authentication

The dYdX v4 API requires authentication for certain endpoints, particularly those related to account information and order placement. Authentication is done using a mnemonic (24-word seed phrase) to derive the necessary keys.

The bot handles authentication internally using the mnemonic provided in the `.env` file.

## Rate Limits

The dYdX v4 API has rate limits to prevent abuse. The bot implements retry logic and backoff strategies to handle rate limiting gracefully.

## Error Handling

The API may return various error codes. The bot includes comprehensive error handling to deal with common error scenarios:

| Error Code | Description | Bot Behavior |
|------------|-------------|-------------|
| 429 | Rate limit exceeded | Wait and retry with exponential backoff |
| 400 | Bad request | Log error and continue |
| 401 | Unauthorized | Check authentication and retry |
| 500 | Server error | Wait and retry |

## API Client Implementation

The bot implements several API clients to interact with the dYdX v4 API:

- `DydxRestClient`: Handles REST API interactions
- `DydxWebSocketClient`: Handles WebSocket connections
- `DydxCosmosClient`: Handles Cosmos RPC interactions

These clients are implemented in the `src/clients` directory.

## Example API Requests

### Getting Market Data

```python
async def get_market_data(market: str) -> Optional[Dict]:
    """
    Get market data for the specified market.
    
    Args:
        market: Trading pair (e.g., 'ETH-USD')
        
    Returns:
        Market data or None if error
    """
    url = f"{self.rest_endpoint}/perpetual/markets"
    data = await self._make_request('GET', url)
    
    if data and 'markets' in data:
        return data['markets'].get(market)
    return None
```

### Placing an Order

```python
async def place_order(self, order_params: Dict) -> Optional[Dict]:
    """
    Place an order.
    
    Args:
        order_params: Order parameters
        
    Returns:
        Order response or None if error
    """
    url = f"{self.rest_endpoint}/perpetual/orders"
    return await self._make_request('POST', url, data=order_params)
```

## Further Reading

For more detailed information about the dYdX v4 API, refer to the official documentation:

- [dYdX v4 API Documentation](https://docs.dydx.exchange/)
