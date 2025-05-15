# Development Guide

This guide provides information for developers who want to extend or modify the dYdX v4 Trading Bot.

## Project Structure

The bot is organized into the following directory structure:

```
dydx_automate/
├── config/                 # Configuration files
│   ├── .env                # Environment variables
│   ├── .env.example        # Example environment file
│   └── config.json         # Bot configuration
├── docs/                   # Documentation
├── logs/                   # Log files
├── src/                    # Source code
│   ├── clients/            # API clients
│   │   ├── base_client.py  # Base client class
│   │   ├── rest_client.py  # REST API client
│   │   ├── websocket_client.py # WebSocket client
│   │   └── cosmos_client.py # Cosmos RPC client
│   ├── core/               # Core functionality
│   │   ├── bot.py          # Main bot class
│   │   ├── market_data.py  # Market data service
│   │   └── execution.py    # Order execution service
│   ├── models/             # Data models
│   │   ├── order.py        # Order model
│   │   └── market.py       # Market data model
│   ├── strategies/         # Trading strategies
│   │   ├── base_strategy.py # Base strategy class
│   │   └── breakout_strategy.py # Breakout strategy
│   └── utils/              # Utility functions
│       ├── config.py       # Configuration utilities
│       ├── logging.py      # Logging utilities
│       └── helpers.py      # Helper functions
├── tests/                  # Test suite
├── cli.py                  # Command-line interface
└── requirements.txt        # Dependencies
```

## Architecture

The bot follows a modular architecture with clear separation of concerns:

1. **API Clients**: Handle communication with the dYdX v4 API
2. **Core Services**: Provide high-level functionality (market data, execution)
3. **Trading Strategies**: Implement trading logic
4. **Models**: Define data structures
5. **Utilities**: Provide common functionality

### Component Interactions

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Bot      │────▶│  Strategy   │◀────│ Market Data │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Execution  │────▶│ REST Client │◀────│   WebSocket │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Extending the Bot

### Adding a New Strategy

To add a new trading strategy:

1. Create a new file in the `src/strategies` directory (e.g., `my_strategy.py`)
2. Implement a class that inherits from `BaseStrategy`
3. Implement the required methods:
   - `analyze`: Analyze market data and generate signals
   - `should_enter`: Determine if a position should be entered
   - `should_exit`: Determine if a position should be exited
   - `calculate_position_size`: Calculate position size
   - `calculate_entry_price`: Calculate entry price
   - `calculate_exit_targets`: Calculate exit targets (stop loss, take profit)

Example:

```python
from typing import Dict, Optional
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    """
    My custom trading strategy.
    """
    def __init__(self, config: Dict):
        super().__init__(config)
        # Initialize strategy-specific parameters
        
    async def analyze(self, market_data: Dict) -> Dict:
        # Implement analysis logic
        return {
            'signal': 'buy',  # or 'sell', 'neutral'
            'current_price': market_data['current_price'],
            # Add other analysis results
        }
    
    def should_enter(self, analysis: Dict) -> bool:
        # Implement entry logic
        return analysis.get('signal') == 'buy'
    
    def should_exit(self, analysis: Dict, position: Dict) -> bool:
        # Implement exit logic
        return False
    
    def calculate_position_size(self, analysis: Dict, account_info: Dict) -> float:
        # Implement position sizing logic
        return 0.01
    
    def calculate_entry_price(self, analysis: Dict) -> float:
        # Implement entry price calculation
        return analysis.get('current_price', 0)
    
    def calculate_exit_targets(self, analysis: Dict, entry_price: float) -> Dict:
        # Implement exit targets calculation
        return {
            'stop_loss': entry_price * 0.95,
            'take_profit': entry_price * 1.15,
            'risk_reward_ratio': 3.0
        }
```

### Adding a New API Client

To add a new API client:

1. Create a new file in the `src/clients` directory (e.g., `my_client.py`)
2. Implement a class that inherits from `BaseClient` or implements the same interface
3. Implement the required methods

### Adding a New Command

To add a new command to the CLI:

1. Open `cli.py`
2. Add a new command using the Click library:

```python
@cli.command()
@click.option('--option', help='Description of the option')
def my_command(option):
    """Description of the command"""
    # Implement command logic
```

## Testing

The bot includes a test suite using pytest. To run the tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_strategy.py
```

### Writing Tests

When adding new functionality, also add corresponding tests:

1. Create a new test file in the `tests` directory (e.g., `test_my_strategy.py`)
2. Implement test functions using pytest

Example:

```python
import pytest
from src.strategies.my_strategy import MyStrategy

@pytest.fixture
def strategy():
    config = {
        'trading': {'market': 'ETH-USD'},
        'risk': {'max_position_size': 0.1}
    }
    return MyStrategy(config)

def test_should_enter(strategy):
    analysis = {'signal': 'buy', 'current_price': 1000.0}
    assert strategy.should_enter(analysis) is True
    
    analysis = {'signal': 'neutral', 'current_price': 1000.0}
    assert strategy.should_enter(analysis) is False
```

## Coding Standards

The bot follows these coding standards:

1. **PEP 8**: Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
2. **Type Hints**: Use type hints for function parameters and return values
3. **Docstrings**: Include docstrings for all classes and functions
4. **Error Handling**: Use try/except blocks for error handling
5. **Logging**: Use the logging module instead of print statements
6. **Async/Await**: Use async/await for I/O-bound operations

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Write tests for your changes
5. Submit a pull request

## Resources

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [pytest documentation](https://docs.pytest.org/)
- [dYdX v4 API documentation](https://docs.dydx.exchange/)
