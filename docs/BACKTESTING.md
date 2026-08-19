# Backtesting

## Purpose

Backtesting evaluates strategy behavior on historical real-market data before forward Paper testing. It is an evidence tool, not a guarantee of future returns.

## Current Phase 5 implementation

The active historical-evidence domain is `backend/app/backtesting/` and includes immutable historical datasets, a public read-only Binance historical provider, isolated deterministic execution/accounting, S1-S4 runner integration, persisted run/trade/equity evidence, strategy-source fingerprints, metrics and `/api/backtests` surfaces.

No optimizer, Live execution or automatic Strategy-to-Paper path is part of Phase 5.

## Historical dataset contract

A valid Backtest dataset contains only real closed candles and persists canonical symbol, timeframe, provider/provided symbol, requested/actual UTC window, ordered OHLCV, candle count and canonical SHA-256 of normalized content.

The historical provider uses Binance public `/api/v3/klines` with explicit time pagination and no account credentials. Dataset creation fails closed on provider failure or invalid data. Production historical code never substitutes generated candles.

Datasets are rejected for empty content, duplicates, out-of-order candles, gaps, symbol/timeframe mismatch, missing real/provider provenance, mixed providers or candles outside the requested window. Numerically equivalent Decimal values hash identically. An existing snapshot SHA is not silently overwritten.

## `backtest-v1` execution semantics

For candle `t`:

1. a previously produced signal may execute at candle `t` open;
2. the portfolio is marked at candle `t` close;
3. candle `t` close is appended to strategy history;
4. S1-S4 calculates a new signal through `t`;
5. that signal may execute no earlier than candle `t+1` open.

This prevents using a candle close to generate a signal and filling retroactively at that already-observed close.

Execution is deterministic and long-only: BUY only while flat, SELL only while long, no pyramiding, no shorts/leverage/margin, 25% default cash allocation, 10 bps adverse slippage and 10 bps fee. There are no random fills/exits or hidden strategy-specific execution rules.

If a position remains open at dataset end it is liquidated at final close under the same costs and labelled `DATASET_END_EXIT`. The bookkeeping equity point from that forced close is included in equity/drawdown but excluded from the time-in-market denominator.

## Financial isolation

Backtesting does not create or mutate active Paper Account, Order, Fill, Position, PaperExecution, PaperRequest or RiskDecision records. `BacktestLedger` carries isolated long-only cash/cost-basis/PnL invariants so historical experiments cannot change forward Paper state.

## Reproducibility and code identity

Every run records/references dataset ID/SHA, provider/symbol/timeframe/window, strategy ID/version, `backtest-v1`, capital/cost/allocation assumptions, evidence-policy label, optional code commit, trades/equity/metrics and status/failure reason.

New runs also persist `BacktestRunEvidence.strategy_code_sha256`, calculated from the active `app.services.strategies` source before financial evidence is created. This catches strategy-code drift even when a human forgets to bump `baseline-v1`. If source cannot be fingerprinted, the run fails closed before creating run state.

The fingerprint is kept in an additive one-to-one evidence table rather than adding a column to `backtest_runs`, because SQLite `create_all()` does not migrate existing tables. Older runs created before this contract can remain readable with no fingerprint; missing provenance is not fabricated retroactively.

Given identical dataset content, strategy source and configuration, deterministic execution must produce identical trades/equity/metrics.

## Persisted evidence

Phase 5 records:

- `BacktestDataset`;
- `BacktestCandle`;
- `BacktestRun`;
- `BacktestRunEvidence`;
- `BacktestTrade`;
- `BacktestEquityPoint`.

A stale `RUNNING` run discovered after restart becomes `INVALID` with `INTERRUPTED_RESTART`; it is never silently resumed as completed evidence.

## Metrics

Completed runs support initial/final equity, net PnL/return, trade count, round trips, wins/losses/win rate, average win/loss, expectancy, gross profit/loss, profit factor where defined, maximum drawdown, total fees, exposure/time in market and dataset-end forced-exit count.

Undefined values remain null. Sharpe is deliberately excluded because its sampling convention has not yet been specified.

## Bias controls

Phase 5 prevents the direct same-candle look-ahead bug through next-candle execution. Research must still avoid tuning/evaluating on the same window without disclosure, cherry-picking favorable periods/assets, ignoring costs, treating tiny samples as sufficient or treating in-sample positivity as forward validation.

Chronological validation/walk-forward methodology remains later research work on top of this runner.

## Strategy discipline

S1-S4 are consumed unchanged. Phase 5 does not modify thresholds or behavior to improve results. Runnable/backtested does not mean profitable, optimized, validated or promising without actual persisted evidence and explicit criteria.

## API

- `GET /api/backtests/status`
- `POST /api/backtests/datasets`
- `GET /api/backtests/datasets`
- `GET /api/backtests/datasets/{id}`
- `POST /api/backtests/runs`
- `GET /api/backtests/runs`
- `GET /api/backtests/runs/{id}`

Run payloads expose `strategy_code_sha256` when that provenance exists. The client cannot upload arbitrary candles and label them real through the active dataset creation endpoint; the real historical provider is called internally.

## Completion status

**Phase 5 source/contract/static gate:** complete.

**Execution certification remains pending** until fresh exact-HEAD backend tests, frontend tests/build and at least one real historical-provider dataset/run smoke are observed.

**S1-S4 real-provider baseline performance remains unobserved.** No performance numbers may be inferred from source code or fixture runs.
