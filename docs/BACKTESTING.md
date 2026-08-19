# Backtesting

## Purpose

Backtesting evaluates strategy behavior on historical real-market data before forward Paper testing. It is an evidence tool, not a guarantee of future returns.

## Current Phase 5 implementation

The active historical-evidence domain is `backend/app/backtesting/`.

It contains:

- immutable historical dataset persistence;
- a public read-only Binance historical provider;
- isolated deterministic execution/accounting;
- S1-S4 runner integration;
- persisted run/trade/equity evidence;
- machine-readable metrics;
- `/api/backtests` dataset/run inspection and execution surfaces.

No optimizer, Live execution or automatic strategy-to-Paper path is part of Phase 5.

## Historical dataset contract

A valid Backtest dataset contains only real closed candles and persists:

- canonical symbol;
- timeframe;
- provider/provider symbol;
- requested UTC start/end;
- actual UTC start/end;
- ordered OHLCV candles;
- candle count;
- canonical SHA-256 of normalized candle content.

The historical provider uses Binance public `/api/v3/klines` with explicit `startTime`/`endTime` pagination and no account credentials.

Dataset creation fails closed on provider failure or invalid data. Production historical code never substitutes generated candles.

Datasets are rejected for:

- empty content;
- duplicate open times;
- out-of-order candles;
- timeframe gaps;
- symbol/timeframe mismatch;
- missing real/provider provenance;
- candles outside the requested window.

Once a snapshot SHA already exists, it is not overwritten as a different dataset.

## `backtest-v1` execution semantics

`backtest-v1` is deterministic and long-only.

For candle `t`:

1. any signal produced previously may execute at candle `t` open;
2. the portfolio is marked at candle `t` close;
3. candle `t` close is appended to strategy history;
4. S1-S4 calculates a new signal from history through `t`;
5. that signal may execute no earlier than candle `t+1` open.

This explicitly prevents using candle `t` close both to generate a signal and to fill at that already-observed close.

Execution rules:

- BUY only while flat;
- SELL only while long;
- no pyramiding;
- no shorts/leverage/margin;
- default position allocation: 25% of available cash;
- default adverse slippage: 10 bps;
- default fee: 10 bps of fill notional;
- no random fills, exits, stops or hidden strategy-specific execution rules.

If a position remains open at the end of the dataset it is liquidated at the final candle close under the same fee/slippage assumptions and the exit is labelled `DATASET_END_EXIT`.

## Financial isolation

Backtesting does not create or mutate active Paper `Account`, `Order`, `Fill`, `Position`, `PaperExecution`, `PaperRequest` or `RiskDecision` rows.

`BacktestLedger` mirrors the long-only cash/cost-basis/PnL conservation rules required for comparable evidence while remaining isolated from the Paper portfolio.

This separation prevents historical experiments from changing forward Paper state.

## Reproducibility contract

Every `BacktestRun` records or references:

- dataset ID and SHA-256;
- dataset provider/symbol/timeframe/window;
- strategy ID/version (`baseline-v1` for current S1-S4);
- execution policy (`backtest-v1`);
- initial capital;
- fee/slippage assumptions;
- position fraction;
- risk/evidence policy label;
- code commit identifier when available;
- resulting metrics/trades/equity series;
- run status and invalidation/failure reason.

Given identical immutable dataset content and configuration, a deterministic strategy must produce the same trades/equity/metrics.

## Persisted evidence

Phase 5 records:

- `BacktestDataset`;
- `BacktestCandle`;
- `BacktestRun`;
- `BacktestTrade`;
- `BacktestEquityPoint`.

A stale `RUNNING` run discovered after restart is changed to `INVALID` with `INTERRUPTED_RESTART`. It is never silently resumed or presented as completed evidence.

## Metrics

Completed runs support:

- initial/final equity;
- net PnL and return;
- trade count;
- completed round trips;
- wins/losses/win rate;
- average win/loss;
- expectancy;
- gross profit/gross loss;
- profit factor where defined;
- maximum drawdown;
- total fees;
- exposure/time-in-market fraction;
- dataset-end forced-exit count.

Undefined values remain null. For example, profit factor is null when there is no gross loss, and win-rate/averages are null when no round trips close.

Sharpe is deliberately excluded from `backtest-v1`; its sampling convention has not yet been specified.

## Bias controls

Phase 5 actively prevents the most immediate look-ahead bug through next-candle execution. Research must additionally avoid:

- parameter tuning and evaluation on the same period without disclosure;
- choosing only favorable assets/periods after seeing results;
- ignoring fees/slippage;
- treating a tiny trade sample as sufficient evidence;
- treating an in-sample positive result as forward validation.

Chronological train/research and validation windows or walk-forward evaluation remain later research methodology on top of this runner.

## Strategy discipline

S1-S4 are consumed unchanged. Phase 5 does **not** modify their thresholds or behavior to improve results.

A strategy being runnable in Backtest means only that the platform can evaluate it reproducibly. `profitable`, `optimized`, `validated` or `promising` require actual persisted evidence and explicit criteria.

## API

Active endpoints:

- `GET /api/backtests/status`
- `POST /api/backtests/datasets`
- `GET /api/backtests/datasets`
- `GET /api/backtests/datasets/{id}`
- `POST /api/backtests/runs`
- `GET /api/backtests/runs`
- `GET /api/backtests/runs/{id}`

The client cannot upload arbitrary candles and label them as real evidence through the active dataset creation endpoint; the provider is called internally.

## Completion status

**Phase 5 source/contract implementation:** present. Final exact-HEAD static audit is required before the source gate is declared closed.

**Execution certification** requires fresh exact-HEAD backend/frontend/build results plus at least one real historical-provider dataset/run smoke.

S1-S4 performance baselines remain **unobserved** until such runs execute. No performance numbers should be inferred from source code or fixtures.
