# Backtesting

## Purpose

Backtesting evaluates strategy behavior on historical real-market data before forward Paper testing. It is an evidence tool, not a guarantee of future returns.

## Phase 5 historical execution boundary

`backend/app/backtesting/` owns immutable historical datasets, a public read-only Binance historical provider, isolated deterministic execution/accounting, S1-S4 runner integration, persisted run/trade/equity evidence, strategy-source fingerprints, metrics and `/api/backtests` surfaces.

Backtesting itself still has no optimizer, Live execution or automatic Strategy-to-Paper path.

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

Execution is deterministic and long-only: BUY only while flat, SELL only while long, no pyramiding, no shorts/leverage/margin, 25% default cash allocation, 10 bps adverse slippage and 10 bps fee. There are no random fills/exits or hidden strategy-specific execution rules.

If a position remains open at dataset end it is liquidated at final close under the same costs and labelled `DATASET_END_EXIT`. The bookkeeping equity point from that forced close is included in equity/drawdown but excluded from the time-in-market denominator.

## Financial isolation

Backtesting does not create or mutate active Paper Account, Order, Fill, Position, PaperExecution, PaperRequest or RiskDecision records. `BacktestLedger` carries isolated long-only cash/cost-basis/PnL invariants.

## Reproducibility and source identity

Every run records/references dataset ID/SHA, provider/symbol/timeframe/window, strategy ID/version, `backtest-v1`, capital/cost/allocation assumptions, evidence-policy label, optional code commit, trades/equity/metrics and status/failure reason.

New runs persist `BacktestRunEvidence.strategy_code_sha256`, calculated from active `app.services.strategies` source before financial evidence is created. If source cannot be fingerprinted, the run fails closed before creating run state.

Older runs created before this contract can remain readable with no fingerprint; missing provenance is not fabricated retroactively.

## Persisted evidence

Phase 5 records:

- `BacktestDataset`;
- `BacktestCandle`;
- `BacktestRun`;
- `BacktestRunEvidence`;
- `BacktestTrade`;
- `BacktestEquityPoint`.

A stale `RUNNING` run discovered after restart becomes `INVALID` with `INTERRUPTED_RESTART`.

## Metrics

Completed runs support initial/final equity, net PnL/return, trade count, round trips, wins/losses/win rate, average win/loss, expectancy, gross profit/loss, profit factor where defined, maximum drawdown, total fees, exposure/time in market and dataset-end forced-exit count.

Undefined values remain null. Sharpe remains excluded because its sampling convention has not been specified.

## Phase 8 chronological research orchestration

Chronological validation/walk-forward methodology is now implemented **outside the Backtest runner** by `backend/app/strategy_research/`.

Backtest remains execution/evidence truth; Research links completed runs explicitly as repeating:

```text
TRAIN -> VALIDATION -> OOS
```

A ResearchStudy cannot silently mix different strategy source fingerprints, execution policies, costs, allocations, market/timeframe, initial capital or historical risk-profile versions. Windows must be chronological and non-overlapping.

`research-v1` treats VALIDATION/OOS as independent holdout gates and combines them with completed Phase 7 forward Paper evidence before manual candidate promotion. It does not automatically generate parameter searches or modify strategy code.

This separation is intentional: Backtest executes historical experiments; Research decides whether explicitly selected evidence satisfies a versioned methodology.

## Bias controls

The combined Phase 5/8 contracts address:

- direct same-candle look-ahead through next-candle execution;
- silent source/config drift through SHA/config matching;
- train/evaluation reuse through explicit TRAIN/VALIDATION/OOS roles;
- cost-condition drift through frozen research assumptions;
- historical-only promotion by requiring forward Paper evidence.

They do not eliminate all statistical risks. Researchers must still avoid cherry-picking windows/assets, repeated manual hypothesis fishing, tiny samples and overinterpreting one candidate PASS.

## Strategy discipline

S1-S4 are consumed unchanged. Neither Phase 5 nor Phase 8 modifies thresholds or behavior automatically to improve results. Runnable, backtested or research-promoted does not mean guaranteed profitable, safe or Live-ready.

## API

Backtest execution:

- `GET /api/backtests/status`
- `POST /api/backtests/datasets`
- `GET /api/backtests/datasets`
- `GET /api/backtests/datasets/{id}`
- `POST /api/backtests/runs`
- `GET /api/backtests/runs`
- `GET /api/backtests/runs/{id}`

Research orchestration is exposed separately under `/api/research/*`.

## Completion/evidence status

**Phase 5 source/contract/static gate:** complete.

Phase 8 now supplies the chronological research layer on top of Phase 5 evidence. Fresh executable certification remains separate.

**S1-S4 real-provider baseline performance and real Phase 8 Research PASS results remain unobserved in this environment.** No performance numbers may be inferred from source or fixture tests.
