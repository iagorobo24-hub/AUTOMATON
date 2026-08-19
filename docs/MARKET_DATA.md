# Market Data

## Goal

Provide trustworthy, timestamped real-market observations to Backtest and Paper without embedding trading decisions.

## Implemented Phase 1 boundary

The active implementation lives under `backend/app/market_data/` and is mounted at `/api/market-data`.

Provider-neutral contracts:

- `Quote`: canonical symbol, positive price, provider timestamp, retrieval timestamp, provider/source metadata and `evidence_mode=real`;
- `Candle`: canonical symbol, interval, UTC open/close time, OHLCV, provider/source metadata and `evidence_mode=real`;
- `MarketDataService`: provider-neutral interface used by the API and intended for future Strategy/Paper consumers.

Initial provider: `BinancePublicMarketDataProvider`.

- public REST only;
- no API key;
- no account methods;
- no order/execution capability;
- current price comes from the latest aggregate trade and therefore carries a provider market timestamp;
- candles come from Binance klines and only closed candles are returned;
- provider failures never fall back to generated/mock values.

The historical `services/binance_service.py` is not this provider and remains legacy because it can silently return mock data.

## Active API

- `GET /api/market-data/status`
- `GET /api/market-data/quote/{symbol}`
- `GET /api/market-data/candles/{symbol}?interval=1m&limit=100`

Path symbols should use forms such as `BTCUSDT` or `BTC-USDT`; the contract normalizes them to `BTC/USDT`.

The current Phase 1 implementation deliberately supports `BASE/USDT` markets only. Widening quote currencies is a future scoped change, not an implicit fallback.

## Quality rules

- Symbols are normalized at the boundary.
- All internal timestamps are timezone-aware UTC.
- Quote freshness is checked; stale or materially future-dated observations are rejected.
- Candle series must be strictly ordered and contiguous for the requested interval.
- Only closed candles cross the real-data contract.
- OHLC values must be structurally valid and prices positive.
- Missing, malformed or stale data is an error, never repaired with synthetic data.
- 429, provider 5xx and transport failures use bounded retries and then fail closed.
- Unsupported intervals are rejected locally before a provider request.
- Every accepted observation carries provider and provider-symbol provenance.

## Provider failure semantics

The API distinguishes:

- `503`: real provider unavailable after bounded retry;
- `502`: provider payload/request violates the real-data quality contract.

Neither case returns a price, candle or generated substitute.

## Backtest data

A future backtest dataset must identify:

- provider/source;
- symbols;
- timeframe;
- start/end timestamps;
- retrieval/version information where available;
- missing-data policy.

The same dataset and strategy configuration should reproduce the same strategy decisions. Building the historical dataset runner belongs to the Backtesting phase; Phase 1 provides the normalized real-data primitives it will consume.

## Paper data

Future Paper execution consumes current real observations through `MarketDataService`. It must reject or pause trading when required data is stale or structurally incomplete rather than invent a price.

Phase 1 does **not** connect agents to trading and does not implement Paper orders, positions or accounting.

## Indicators

Indicators such as EMA, RSI, ATR, MACD and Bollinger Bands are derived data. They must be computed from validated market observations with deterministic implementations and test fixtures. Indicator availability must be explicit; missing inputs produce no valid indicator rather than a fabricated fallback.

## Test coverage authored

The repository now contains tests for:

1. symbol normalization;
2. positive/UTC quote contracts;
3. stale/future quote rejection;
4. candle ordering and gap detection;
5. provider parsing with deterministic HTTP fixtures;
6. closed-candle filtering;
7. retry/fail-closed provider behavior;
8. malformed payload rejection;
9. API provenance and evidence-mode output;
10. API 503/502 failure semantics;
11. route registration in the active runtime.

These tests are authored against the implementation but are **not execution-certified on the current HEAD** until the repository test gate runs successfully in an available environment.

## Phase 1 exit criterion

At source/contract level, Paper/Backtest consumers now have a real-only boundary that cannot generate fallback prices. Phase 1 is considered fully certified only after fresh backend tests, frontend tests and frontend build complete successfully on the exact resulting HEAD.
