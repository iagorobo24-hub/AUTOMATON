# Database Architecture

## Active baseline

The runtime uses SQLModel + SQLite through `backend/app/database.py`. MongoDB remains legacy and is not a source of truth for new product work.

## Active records

### Legacy/transition

- `Agent`: identity, strategy and lifecycle state. Budget fields are compatibility mirrors only.
- `Trade`: historical pre-provenance record. Existing rows remain `legacy_unclassified` and are outside authoritative Paper/Backtest evidence.

### Phase 2 Accounting

- `portfolio_accounts` (`Account`)
- `portfolio_orders` (`Order`)
- `portfolio_fills` (`Fill`)
- `portfolio_positions` (`Position`)
- `portfolio_ledger` (`LedgerEntry`)

These tables are the only active Paper financial source of truth.

### Phase 3 Paper

- `paper_executions` (`PaperExecution`): real quote/fill-policy provenance linked to Accounting.
- `paper_requests` (`PaperRequest`): request-id idempotency and recovery state.

### Phase 4 Risk

- `risk_profiles` (`RiskProfile`): versioned risk policy.
- `risk_decisions` (`RiskDecision`): persisted ALLOW/REJECT evidence and one-time Paper-consumption linkage.

### Phase 5 Backtesting

Backtesting uses dedicated evidence tables rather than active Paper portfolio rows:

- `backtest_datasets` (`BacktestDataset`): immutable dataset metadata including symbol, interval, provider, requested/actual UTC window, candle count, SHA-256 and status.
- `backtest_candles` (`BacktestCandle`): ordered OHLCV observations keyed by dataset + ordinal/open time.
- `backtest_runs` (`BacktestRun`): strategy/configuration/execution assumptions, run status and aggregate metrics.
- `backtest_trades` (`BacktestTrade`): chronological historical execution evidence, signal candle, next execution candle, quantity, prices, fee, realized PnL and exit reason.
- `backtest_equity_points` (`BacktestEquityPoint`): chronological cash/market-value/equity/exposure/drawdown series.

Backtest timestamps use a UTC-preserving SQLAlchemy type so SQLite reads restore explicit UTC semantics rather than silently returning ambiguous local-naive timestamps.

## Source-of-truth rules

- Accounting owns active Paper balances, positions, PnL, fees and equity.
- PaperExecution owns Paper execution provenance.
- PaperRequest owns Paper mutation idempotency/recovery state.
- RiskProfile owns versioned Paper risk limits.
- RiskDecision owns Paper risk authorization evidence.
- BacktestDataset/BacktestCandle own immutable historical input evidence.
- BacktestRun/Trade/EquityPoint own historical experiment evidence only.
- Backtest records never become a second Paper accounting system.
- `Agent.presupuesto_*` never becomes a competing accounting source.

## Backtest immutability and reproducibility

A dataset SHA-256 is computed over normalized candle content before persistence. Duplicate hashes are not overwritten as a different snapshot.

A BacktestRun references the dataset SHA and stores strategy version, execution policy, initial capital, fee/slippage/allocation and evidence status. Two identical deterministic runs may produce separate run rows but must produce identical trade/equity/metric content.

Interrupted `RUNNING` BacktestRun rows are invalidated at startup with `INTERRUPTED_RESTART`; they are not silently resumed or treated as completed evidence.

## Startup and recovery

Normal startup:

1. initializes SQLModel tables;
2. bootstraps missing Phase 2 Paper accounts from initial/funded capital only;
3. bootstraps `risk-v1` idempotently;
4. invalidates interrupted Backtest runs;
5. reconciles pending Paper executions;
6. reconciles Paper request reservations.

## Current scope limits

- Paper: long-only, operator-only MARKET execution, Risk mandatory;
- Backtest: long-only `backtest-v1`, no pyramiding, deterministic next-candle execution;
- Backtest state isolated from Paper Account/Order/Fill/Position tables;
- no leverage/margin/shorts;
- no automatic strategy execution yet;
- no Backtest optimizer;
- no Live execution.

## Rules

- Never mix evidence modes silently.
- Every Paper order has real current-market provenance and a Risk decision.
- Every Backtest run references immutable real historical provenance.
- Ambiguous/incomplete evidence fails closed.
- Existing data is migrated or quarantined explicitly; never silently promoted.
- No new active Mongo collection is introduced.
