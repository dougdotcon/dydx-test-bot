# Trading Strategies

This guide explains the trading strategies implemented in the dYdX v4 Trading Bot.

## Breakout Strategy

The primary strategy implemented in the bot is a breakout strategy with volume confirmation. This strategy looks for price breakouts above resistance levels with abnormal trading volume, which can indicate strong momentum and potential for continued price movement.

### Strategy Logic

1. **Resistance Level Calculation**: The strategy calculates resistance levels based on recent price highs over a configurable lookback period.
2. **Volume Anomaly Detection**: The strategy monitors trading volume and detects abnormal volume spikes compared to the average volume.
3. **Breakout Signal**: A breakout signal is generated when the price breaks above the resistance level AND the volume is above the configured threshold.
4. **Position Sizing**: Position size is calculated based on account equity and risk parameters.
5. **Exit Strategy**: The strategy sets stop loss just below the resistance level and take profit based on the configured risk-reward ratio.

### Configuration Parameters

The breakout strategy is configured in the `trading` and `technical` sections of the configuration file:

```json
{
  "trading": {
    "market": "ETH-USD",
    "timeframe": "5m",
    "volume_factor": 2.5,
    "risk_reward_ratio": 3.0
  },
  "technical": {
    "resistance_period": 24,
    "volume_lookback": 20
  }
}
```

- `volume_factor`: The volume anomaly detection threshold. A value of 2.5 means the current volume must be 2.5 times the average volume to trigger a breakout signal.
- `risk_reward_ratio`: The risk-to-reward ratio for calculating take profit levels. A value of 3.0 means the take profit will be set at 3 times the distance from entry to stop loss.
- `resistance_period`: The number of periods to look back for calculating resistance levels.
- `volume_lookback`: The number of periods to look back for calculating average volume.

### Strategy Performance Factors

The performance of the breakout strategy depends on several factors:

1. **Market Volatility**: The strategy tends to perform better in volatile markets with clear trends.
2. **Volume Factor**: A higher volume factor (e.g., 3.0) will generate fewer but potentially more reliable signals, while a lower volume factor (e.g., 1.5) will generate more signals but with potentially more false positives.
3. **Resistance Period**: A longer resistance period will identify stronger resistance levels but may miss shorter-term opportunities.
4. **Risk-Reward Ratio**: A higher risk-reward ratio will set take profit levels further from entry, potentially capturing larger moves but with a lower win rate.

### Example Scenario

Here's an example of how the breakout strategy works:

1. The bot calculates a resistance level at $2,000 for ETH-USD based on the last 24 periods.
2. The average volume over the last 20 periods is 100 ETH.
3. The current price breaks above $2,000 with a volume of 300 ETH (3x the average).
4. The volume factor is set to 2.5, so the volume condition is met (3 > 2.5).
5. The bot generates a breakout signal and places a buy order at the current price.
6. The stop loss is set just below the resistance level at $1,980 (1% below entry).
7. With a risk-reward ratio of 3.0, the take profit is set at $2,060 (3x the distance from entry to stop loss).

## Implementing Custom Strategies

The bot is designed with a modular architecture that allows for easy implementation of custom strategies. To implement a custom strategy:

1. Create a new strategy class in the `src/strategies` directory that inherits from `BaseStrategy`.
2. Implement the required methods: `analyze`, `should_enter`, `should_exit`, `calculate_position_size`, `calculate_entry_price`, and `calculate_exit_targets`.
3. Update the bot to use your custom strategy.

See the [Development Guide](../development/README.md) for more information on implementing custom strategies.

## Future Strategy Enhancements

Future versions of the bot may include additional strategies such as:

- Mean reversion strategies
- Moving average crossover strategies
- Bollinger Band strategies
- Multi-timeframe strategies
- Machine learning-based strategies

Stay tuned for updates!
