# Metrics and Evidence

## Principle

AUTOMATON is useful only if results can be traced to real inputs and explicit assumptions. A dashboard value is not evidence by itself.

## Evidence modes stay separate

Every financial result must identify its mode:

- synthetic;
- backtest;
- paper;
- future live.

Backtest, Paper and legacy `Trade` histories must not be merged into one undifferentiated performance curve.

## Required provenance

A valid Backtest result references:

- immutable dataset ID/SHA-256;
- provider;
- symbol/timeframe;
- UTC window;
- strategy ID/version;
- execution policy;
- initial capital;
- fee/slippage/allocation assumptions;
- run ID;
- code commit when available;
- status/invalidation reason.

A Paper result instead references its real-time market observations, RiskDecision, PaperExecution and Accounting records.

## Phase 5 Backtest metrics

Completed `BacktestRun` records support:

- initial/final equity;
- net PnL;
- net return;
- trade count;
- completed round trips;
- wins/losses;
- win rate;
- average win/loss;
- expectancy per closed round trip;
- gross profit/gross loss;
- profit factor where defined;
- maximum drawdown from chronological equity high-water;
- total fees;
- exposure/time-in-market fraction;
- dataset-end forced-exit count.

Undefined metrics remain null rather than being converted into misleading zeroes. Examples:

- no closed round trips -> win rate/average win/average loss/expectancy are null;
- zero gross loss -> profit factor is null rather than infinite or fabricated.

Sharpe is not part of `backtest-v1`; no sampling convention has been defined yet.

## Reproducibility

Two runs over the same immutable dataset content and the same configuration should produce identical trades, equity sequence and metrics for deterministic S1-S4.

The dataset SHA protects against comparing runs that appear to use the same symbol/window but actually contain different market observations.

## Evidence labels

Use conservative language:

- **Observed**: directly measured from a valid persisted run.
- **Reproduced**: independently rerun with matching output under the same inputs/configuration.
- **Hypothesis**: design or trading idea without supporting valid runs.
- **Historical claim**: assertion from legacy docs/code not revalidated under current contracts.

Do not use `optimized`, `validated`, `profitable`, `safe`, `promising` or `production-ready` without an explicit criterion and supporting reproducible evidence.

## Invalidation

Backtest evidence is invalid for decision-making if affected by:

- synthetic/fabricated data in a purported real-data run;
- dataset corruption/gaps/duplicates/out-of-order observations;
- look-ahead or same-candle fill leakage;
- incorrect fee/slippage accounting;
- incomplete/interrupted run state;
- code/config metadata mismatch;
- known execution/accounting defects.

Phase 5 marks stale `RUNNING` runs found after restart as `INVALID` / `INTERRUPTED_RESTART` rather than silently treating them as evidence.

## UI/reporting rules

UI and reports must show Backtest as Backtest. Missing/undefined metrics stay missing. A positive Backtest does not imply forward Paper performance, and a fixture-based test run is not financial evidence.
