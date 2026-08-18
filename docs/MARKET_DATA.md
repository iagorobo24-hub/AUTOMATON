# Market Data

## Goal

Provide trustworthy, timestamped real-market observations to Backtest and Paper without embedding trading decisions.

## Requirements

- Normalize symbols, timestamps and numeric precision at the boundary.
- Preserve provider/source metadata for every observation used as evidence.
- Support at least candles/OHLCV required by strategies and a current price/quote source for Paper execution.
- Detect stale data, gaps, out-of-order observations and provider failures.
- Never silently replace missing real data with generated values.
- Provider retries and rate-limit handling must not duplicate observations or reorder time.
- Use UTC internally.

## Provider policy

Initial implementation should prefer a public, read-only crypto market-data source that does not require trading credentials for normal operation. Existing CoinGecko/Binance-related code may be reused only after contract review; historical integration status is not proof of current correctness.

## Backtest data

A backtest dataset must identify:

- provider/source;
- symbols;
- timeframe;
- start/end timestamps;
- retrieval/version information where available;
- missing-data policy.

The same dataset and strategy configuration should reproduce the same strategy decisions.

## Paper data

Paper consumes current real observations. The engine must reject or pause trading when required data is stale or structurally incomplete rather than invent a price.

## Indicators

Indicators such as EMA, RSI, ATR, MACD and Bollinger Bands are derived data. They must be computed from validated market observations with deterministic implementations and test fixtures. Indicator availability must be explicit; missing inputs produce no valid indicator rather than a fabricated fallback.

## Quality gates

Before Market Data is accepted for Paper:

1. deterministic normalization tests;
2. stale/gap/out-of-order tests;
3. recorded fixture tests for provider parsing;
4. time-zone/UTC tests;
5. provider failure behavior verified;
6. no synthetic fallback reachable from Paper mode.
