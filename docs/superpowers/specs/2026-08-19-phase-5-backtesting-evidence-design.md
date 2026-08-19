# Phase 5 Backtesting & Evidence Design

## Objective

Build a reproducible historical-evidence subsystem that evaluates existing strategies S1-S4 on immutable real-market datasets without contaminating Paper state or changing strategy logic.

## Scope

Phase 5 adds:

- immutable historical candle datasets sourced from real public market data;
- deterministic backtest execution with explicit fee/slippage assumptions;
- strict no-look-ahead signal/execution ordering;
- isolated backtest financial state using Accounting invariants;
- persisted run/trade/equity evidence and machine-readable metrics;
- API surfaces for dataset creation/listing and run creation/inspection;
- baseline S1-S4 evaluation only when executable real-data evidence is available.

Out of scope:

- parameter optimization;
- modifying S1-S4 rules to improve outcomes;
- walk-forward optimization framework beyond train/validation metadata;
- autonomous agent execution;
- Agent Evolution/replication;
- 24/7 Paper;
- shorts, leverage or margin;
- Live execution.

## Architecture

### Historical dataset boundary

Create `backend/app/backtesting/datasets.py` and a historical Binance public adapter. A dataset request specifies canonical symbol, interval, UTC start/end and provider. The adapter downloads only closed candles and paginates deterministically.

A dataset snapshot is immutable once persisted. Its canonical payload is normalized by candle open time and includes symbol, interval, OHLCV, provider and provider symbol. A SHA-256 digest over canonical serialized candle content identifies the exact dataset.

Dataset validation rejects:

- empty snapshots;
- non-real provenance;
- duplicate open times;
- gaps relative to the requested interval;
- out-of-order candles;
- open/incomplete candles;
- candles outside the requested UTC window;
- malformed OHLCV.

The active Phase 1 current-market provider remains unchanged. Historical fetching is a separate read-only boundary because current `get_candles(limit=...)` does not define arbitrary historical windows.

### Persistence

Add SQLModel records:

`BacktestDataset`
- symbol, interval, provider, requested_start/end;
- actual_start/end;
- candle_count;
- content_sha256;
- status (`READY`/`INVALID`);
- created_at.

`BacktestCandle`
- dataset_id;
- ordinal;
- open/close timestamps;
- OHLCV;
- provider/provider_symbol.

`BacktestRun`
- dataset_id;
- strategy_id (`S1`-`S4`);
- strategy_version (`baseline-v1` initially);
- execution_policy (`backtest-v1`);
- initial_capital;
- fee_bps;
- slippage_bps;
- position_fraction;
- risk_profile_version or explicit `backtest-risk-v1` label;
- status (`RUNNING`/`COMPLETED`/`FAILED`/`INVALID`);
- started/completed timestamps;
- metrics fields plus failure/invalidation reason.

`BacktestTrade`
- run_id;
- side;
- signal_candle_time;
- execution_candle_time;
- quantity;
- market_price;
- fill_price;
- fee;
- realized_pnl where applicable.

`BacktestEquityPoint`
- run_id;
- candle_time;
- cash;
- market_value;
- equity;
- exposure;
- drawdown.

Backtest records never share Paper `Account`, `PaperExecution`, `PaperRequest` or `RiskDecision` rows. Accounting formulas are reused through an isolated ledger/account state owned by the backtest runner, avoiding contamination of active agents.

## Execution semantics: `backtest-v1`

The runner is deterministic and long-only.

For each closed candle at index `t`:

1. append candle `t` close to strategy history;
2. calculate S1-S4 signal using only history through `t`;
3. record the signal time as candle `t` close;
4. any resulting order executes no earlier than candle `t+1` open;
5. apply adverse slippage and fee explicitly;
6. update isolated accounting state;
7. mark equity using candle `t+1` close after execution.

This prevents using a closing price to generate a signal and also fill at that same already-observed close.

BUY semantics:
- only when flat;
- allocate a fixed configurable fraction of available equity/cash, default 25%;
- quantity is deterministic from next-candle open plus slippage/fee reserve;
- no pyramiding in `backtest-v1`.

SELL semantics:
- only when long;
- close the entire position;
- S1/S3 may therefore hold indefinitely until dataset end because they do not emit SELL;
- S2/S4 SELL follows their existing strategy rules.

At dataset end an open position is forcibly liquidated at the final candle close under the same adverse slippage/fee model and is labelled `DATASET_END_EXIT`. This prevents final-equity comparisons from depending on unrealized open positions while making the artificial exit explicit.

No random fills, random exits, hidden stop-losses or strategy-specific execution rules are allowed.

## Costs

`backtest-v1` defaults to the current Paper assumptions for comparability:

- slippage: 10 bps adverse;
- fee: 10 bps of fill notional.

They are run parameters and persisted. Changing them produces a different run configuration/evidence record.

## Strategy contract

S1-S4 are consumed through `get_strategy()` unchanged. Phase 5 must not modify their algorithms to improve backtest outcomes.

The initial strategy evidence version is `baseline-v1`, referring to the exact current S1-S4 code contract. Unknown strategy IDs fail explicitly.

## Metrics

Every completed run computes from persisted/equity state:

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
- maximum drawdown from the run equity high-water series;
- total fees;
- exposure fraction/time in market;
- dataset-end forced-exit count.

Undefined metrics remain null rather than fabricated (for example profit factor with zero gross loss).

Sharpe is deliberately excluded from `backtest-v1`; its sampling convention is not yet specified.

## Evidence and reproducibility

A run is attributable to:

- immutable dataset SHA-256;
- dataset provider/symbol/interval/time window;
- strategy ID/version;
- execution policy;
- initial capital;
- fee/slippage;
- position fraction;
- code commit identifier when available;
- run ID and exact metrics.

Given identical dataset content and configuration, repeated runs must produce identical trades/equity/metrics within Decimal serialization equality.

Backtest evidence is never merged with Paper or legacy `Trade` history.

## API

Mount read/control boundary at `/api/backtests`:

- `GET /status`
- `POST /datasets` — fetch/validate/persist immutable real dataset;
- `GET /datasets`
- `GET /datasets/{id}`
- `POST /runs` — execute deterministic run against an existing READY dataset;
- `GET /runs`
- `GET /runs/{id}` — include configuration, metrics and compact trade/equity summary.

No optimizer endpoint is introduced.

## Failure semantics

Fail closed:

- provider unavailable -> dataset creation fails without synthetic fallback;
- invalid/gapped data -> dataset marked INVALID or request rejected before READY evidence exists;
- missing dataset -> run 404;
- non-READY dataset -> run rejected;
- unknown strategy -> 422/explicit failure;
- internal accounting invariant failure -> run `INVALID`, not `COMPLETED`;
- interrupted `RUNNING` run is not silently treated as valid evidence; startup/read path may mark stale runs `INVALID_INTERRUPTED` until a future resumable-run design exists.

## Testing

Authored tests must cover:

- canonical dataset hashing and deterministic hash equality;
- historical pagination fixture parsing;
- gap/duplicate/out-of-order rejection;
- no-look-ahead: signal on candle `t`, fill on `t+1` only;
- deterministic identical runs;
- fees/slippage;
- BUY-flat/SELL-long state machine;
- forced dataset-end exit;
- S1-S4 unchanged strategy behavior;
- maximum drawdown and core metrics;
- undefined metric null semantics;
- dataset/run persistence/reload;
- API boundaries and no Live/Paper mutation;
- no synthetic fallback.

Repository executable gate remains:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

If real provider execution is unavailable, no S1-S4 performance numbers may be invented. Phase 5 may be source/contract complete while operational evidence remains pending.
