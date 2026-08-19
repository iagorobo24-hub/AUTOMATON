# Database Architecture

## Active baseline

The runtime uses SQLModel + SQLite through `backend/app/database.py`. MongoDB remains legacy and is not a source of truth for new product work.

## Active records

### Legacy/transition
- `Agent`: identity, strategy and lifecycle state. Budget fields are compatibility mirrors only.
- `Trade`: historical pre-provenance record outside authoritative Paper/Backtest evidence.

### Phase 2 Accounting
- `portfolio_accounts` (`Account`)
- `portfolio_orders` (`Order`)
- `portfolio_fills` (`Fill`)
- `portfolio_positions` (`Position`)
- `portfolio_ledger` (`LedgerEntry`)

These tables are the only active Paper financial source of truth.

### Phase 3 Paper
- `paper_executions` (`PaperExecution`)
- `paper_requests` (`PaperRequest`)

### Phase 4 Risk
- `risk_profiles` (`RiskProfile`)
- `risk_decisions` (`RiskDecision`)

### Phase 5 Backtesting

Backtesting uses dedicated evidence tables rather than active Paper portfolio rows:

- `backtest_datasets` (`BacktestDataset`): immutable dataset provenance and SHA-256.
- `backtest_candles` (`BacktestCandle`): ordered real historical OHLCV.
- `backtest_runs` (`BacktestRun`): strategy/config/execution assumptions, status and aggregate metrics.
- `backtest_run_evidence` (`BacktestRunEvidence`): additive one-to-one provenance such as `strategy_code_sha256`.
- `backtest_trades` (`BacktestTrade`): historical execution evidence.
- `backtest_equity_points` (`BacktestEquityPoint`): chronological cash/market-value/equity/exposure/drawdown.

`backtest_run_evidence` is intentionally separate from `backtest_runs`. SQLite `create_all()` can safely create a new table but does not migrate columns into an already-created table. This preserves compatibility with databases that started during early Phase 5 while preventing fabricated retroactive fingerprints. Pre-fingerprint runs may therefore have no evidence row; new runs must create one before simulation proceeds.

Backtest timestamps use a UTC-preserving SQLAlchemy type so SQLite reads restore explicit UTC semantics.

## Source-of-truth rules

- Accounting owns active Paper balances, positions, PnL, fees and equity.
- PaperExecution owns Paper execution provenance.
- PaperRequest owns Paper mutation idempotency/recovery state.
- RiskProfile owns versioned Paper risk limits.
- RiskDecision owns Paper risk authorization evidence.
- BacktestDataset/BacktestCandle own immutable historical input evidence.
- BacktestRun/RunEvidence/Trade/EquityPoint own historical experiment evidence only.
- Backtest records never become a second Paper accounting system.
- `Agent.presupuesto_*` never becomes a competing accounting source.

## Backtest immutability and reproducibility

Dataset SHA-256 is computed over normalized candle content; numerically equivalent Decimal formatting hashes identically. Mixed providers, gaps, duplicates and ordering errors are rejected.

Every new Backtest run gets a SHA-256 fingerprint of the active strategy module before run state is committed. Two deterministic runs are comparable only when dataset/configuration and source fingerprint match. A missing fingerprint on a historical pre-contract run is missing evidence, not permission to infer one.

Interrupted `RUNNING` runs are invalidated at startup with `INTERRUPTED_RESTART`; they are not silently resumed.

## Startup and recovery

Normal startup:

1. initializes SQLModel tables, including newly additive evidence tables;
2. bootstraps missing Phase 2 Paper accounts from funded capital only;
3. bootstraps `risk-v1`;
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
- Every new Backtest run references immutable real historical provenance and strategy source fingerprint.
- Ambiguous/incomplete evidence fails closed.
- Existing data is migrated or quarantined explicitly; never silently promoted.
- No new active Mongo collection is introduced.
