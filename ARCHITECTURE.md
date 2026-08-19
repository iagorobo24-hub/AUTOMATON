# AUTOMATON Architecture

## Objective

AUTOMATON is built around autonomous-agent research using **real market data and virtual capital** until explicit evidence/safety gates justify any future Live mode.

## Non-negotiable boundaries

1. Synthetic data is test-only and explicitly labelled.
2. Backtest and Paper use real market data.
3. Backtest and Paper use virtual capital only.
4. Live is a separate future execution adapter.
5. Financial evidence carries explicit mode/provenance.
6. SQLModel/SQLite is the active persistence baseline.
7. Legacy Mongo/trading services are not reactivated as shortcuts.
8. Accounting is the only active Paper financial authority.
9. Paper mutations are idempotent and fail closed on ambiguous recovery.
10. Every normal Paper execution requires a persisted current-profile Phase 4 Risk ALLOW.
11. Backtest state is isolated from active Paper accounts and cannot be merged into Paper evidence.
12. Backtest signals observed on candle `t` cannot execute before candle `t+1`.

## Active domains

### Market Data — Phase 1

`backend/app/market_data/` owns current real Quote/Candle contracts, UTC/provenance, symbol normalization, freshness/gaps/order validation and bounded retries.

`backend/app/backtesting/providers/binance_history.py` is a separate read-only historical adapter. It paginates explicit UTC windows from Binance public market data and has no account/trading capability or synthetic fallback.

### Strategy / Signals

S1-S4 remain the active deterministic baseline implementations in `backend/app/services/strategies.py`.

Phase 5 consumes them unchanged through `get_strategy()`. Backtesting results must not trigger threshold changes inside the evaluated period. No active Strategy -> Risk -> Paper automation exists yet.

### Risk — Phase 4

`backend/app/risk/` is the persistent Paper authorization domain. It owns `RiskProfile`, `RiskDecision`, exposure/loss/drawdown gates and the pause/resume circuit breaker.

Normal Paper execution cannot bypass a persisted current-profile ALLOW decision.

### Paper Execution — Phase 3 + Phase 4 gate

`backend/app/paper_execution/` supports operator-originated MARKET BUY/SELL with real current Quotes and virtual capital. `paper-v1` uses 10 bps adverse slippage, 10 bps fee, persistent request-id idempotency and conservative restart recovery.

```text
request_id -> Real Market Data -> Risk -> Paper Execution -> Accounting
```

There is no normal Paper execution bypass without Risk and no Live exchange adapter.

### Portfolio & Accounting — Phase 2

`backend/app/accounting/` owns active Paper Account, Order, Fill, Position and LedgerEntry state. Funding never counts as PnL and long-only is the defined scope.

`AccountingIntegrityService` provides structural integrity checks for Risk where complete valuation is unavailable.

### Backtesting & Evidence — Phase 5

`backend/app/backtesting/` is a separate historical evidence subsystem.

#### Immutable dataset path

`BacktestDataset` and `BacktestCandle` persist an exact real historical snapshot:

- canonical symbol/timeframe;
- requested and actual UTC windows;
- provider/provider symbol;
- ordered OHLCV candles;
- candle count;
- canonical SHA-256 digest;
- `READY`/invalid state.

Dataset creation rejects empty, duplicate, out-of-order, gapped, provenance-less or out-of-window series. Dataset hashes are calculated from normalized candle content before persistence.

#### Runner

`BacktestRunner` implements `backtest-v1`:

```text
candle t open: execute only signal produced earlier
candle t close: mark equity
candle t close: append close to history and compute new S1-S4 signal
next candle open: signal may execute
```

Therefore a strategy can use candle `t` close but can never also fill at that already-observed close.

Execution is deterministic and isolated:

- long-only;
- BUY only while flat;
- SELL only while long;
- no pyramiding;
- default 25% allocation per entry;
- default 10 bps adverse slippage;
- default 10 bps fee;
- no random fills/stops/exits;
- final open position is explicitly closed at dataset end with `DATASET_END_EXIT`.

`BacktestLedger` mirrors the cash/cost-basis/PnL conservation rules needed for comparable evidence but does **not** create active Paper Account/Order/Fill/Position rows.

#### Persisted evidence

`BacktestRun`, `BacktestTrade` and `BacktestEquityPoint` persist:

- dataset hash;
- strategy ID/version;
- execution policy;
- initial capital;
- fees/slippage/allocation;
- evidence status;
- chronological trades;
- chronological equity/exposure/drawdown;
- resulting metrics.

Interrupted `RUNNING` backtests are invalidated at restart instead of resumed or promoted to valid evidence.

### Metrics & Evidence

Phase 5 computes final equity, net PnL/return, trades, round trips, wins/losses, win rate, average win/loss, expectancy, gross profit/loss, profit factor where defined, maximum drawdown, fees, exposure fraction and forced exits.

Undefined metrics remain null. Sharpe is intentionally absent until its sampling convention is defined.

Legacy `Trade`, Paper, Backtest and future Live histories remain distinct evidence modes.

### Agent Lifecycle

Owns identity, status and future lineage/replication. Replication remains blocked until Phase 6 defines evidence-aware fitness and non-duplicating capital allocation.

## Active API/UI boundary

Trading/research surfaces include:

- `/api/market-data/*`
- `/api/accounting/*`
- `/api/risk/*`
- `/api/paper/*`
- `/api/backtests/status`
- `/api/backtests/datasets`
- `/api/backtests/datasets/{dataset_id}`
- `/api/backtests/runs`
- `/api/backtests/runs/{run_id}`

There is no optimizer endpoint, automatic-trading start endpoint or Live execution endpoint.

## Current runtime

`backend/app/main.py` reports:

- `runtime_mode=transition`;
- `market_data=real_contract_available`;
- `accounting=authoritative_phase_2`;
- `risk=authoritative_phase_4`;
- `paper_trading=operator_only_phase_4`;
- `backtesting=evidence_phase_5`;
- `automated_trading=blocked_until_strategy_integration`;
- `live_execution=disabled`.

Startup initializes persistence, bootstraps Accounting/Risk, invalidates interrupted Backtest runs and reconciles Paper execution/request recovery.

## Target automated Paper flow

```text
Provider -> Market Data -> Strategy Intent -> Risk -> Paper Execution -> Accounting
                                                |
                                                +-> Evidence
```

Backtesting is a parallel historical research path and does not enable this autonomous flow.

## Synthetic and Live isolation

Synthetic code is test-only. Historical/current real-data failures never fall back to fabricated prices. Future Live execution must be a separate explicitly authorized adapter behind `docs/LIVE_TRADING_GATE.md`.

## Verification

Static review can establish source/contract coherence, not runtime correctness or profitability. Exact-HEAD execution certification requires fresh backend tests, frontend tests/build and, for operational evidence, a real-provider historical dataset/run smoke.
