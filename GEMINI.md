# GEMINI.md — AUTOMATON Project Contract

## Read first

Canonical product direction is defined by `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md`. Inspect `backend/app/main.py` and `frontend/src/App.jsx` before claiming current implementation status.

## Product objective

Build a trustworthy autonomous-agent trading platform whose immediate target is **Paper Trading on real market data with virtual capital**, supported by reproducible historical evidence.

Never present synthetic/random/mock results as Backtest, Paper or Live evidence.

## Current runtime

- FastAPI + SQLModel + SQLite.
- React/Vite frontend.
- Synthetic `AgentEngine` is not started by normal runtime.
- Phase 1 Market Data is real-only and fail-closed.
- Phase 2 Accounting is authoritative for active Paper financial state.
- Phase 3 Paper MARKET execution is operator-only, deterministic and idempotent.
- Phase 4 Risk is active and mandatory for normal Paper execution.
- Phase 5 Backtesting is active as an isolated historical-evidence subsystem.
- Runtime reports `risk=authoritative_phase_4`, `paper_trading=operator_only_phase_4`, `backtesting=evidence_phase_5`, `automated_trading=blocked_until_strategy_integration`, `live_execution=disabled`.
- Historical Trade rows remain `legacy_unclassified`.

## Trading architecture

Active/future Paper path:

`Market Data -> Strategy Intent -> Risk -> Paper Execution -> Portfolio/Accounting -> Metrics/Evidence`.

Current Backtest path:

`real historical dataset -> S1-S4 -> next-candle backtest execution -> isolated ledger -> persisted Backtest evidence`.

Backtesting does not enable autonomous Paper trading.

## Market Data constraint

Real-data providers fail closed. Never copy legacy `BinanceService` mock/generated fallback behavior into active current or historical market-data paths.

## Accounting constraint

- `backend/app/accounting/` owns active Paper financial state.
- `Agent.presupuesto_*` are compatibility mirrors only.
- Deposits are funding, never profit.
- Paper fills go through `AccountingService`.
- Long-only is the defined scope; do not invent short/margin/leverage semantics.
- Replication stays blocked until explicit non-duplicating capital transfer exists.

## Paper/Risk constraint

- Paper is operator-only MARKET BUY/SELL.
- Price comes from real current Market Data, never client input.
- `paper-v1` is deterministic/versioned and request-id idempotent.
- Every normal Paper execution requires a persisted current-profile one-time Risk ALLOW.
- REJECT creates no Paper Order/Fill.
- Risk pause/resume is a circuit breaker only; it does not enable autonomous trading.
- Ambiguous Paper recovery fails closed.
- Paper has no Live credentials/adapter.

## Phase 5 Backtesting constraint

`backend/app/backtesting/` and `backend/app/models/backtesting.py` own historical evidence.

- Historical datasets must be real, immutable and SHA-256 identified.
- Historical Binance access is public/read-only and never falls back to generated candles.
- Reject empty, duplicate, out-of-order, gapped or out-of-window datasets.
- Persist explicit UTC semantics across SQLite.
- A signal computed from candle `t` may execute no earlier than candle `t+1` open.
- `backtest-v1` is long-only, no pyramiding, default 25% allocation, 10 bps adverse slippage and 10 bps fee.
- Final open positions are explicitly liquidated as `DATASET_END_EXIT`.
- Backtest financial state must not mutate Paper Account/Order/Fill/Position, PaperExecution, PaperRequest or RiskDecision rows.
- Persist BacktestRun/Trade/EquityPoint evidence and keep undefined metrics null.
- Interrupted RUNNING runs become INVALID; never silently resume or promote them.
- Do not add an optimizer or modify S1-S4 to improve evaluated results during Phase 5.
- Current S1-S4 are `baseline-v1` Backtest inputs. They remain performance-unverified until valid real-provider runs exist.

## Legacy

Mongo DatabaseService, old Trading/Paper engines, legacy RiskManager, auth/payments/chat/notifications and unmounted pages are not active contracts. Migrate only useful concepts compatible with the current architecture.

## Evidence rules

- Never mix Synthetic, Backtest, Paper and Live performance histories silently.
- No profitable/optimized/validated/safe claim without reproducible evidence and explicit criteria.
- Fixture tests prove software behavior, not trading performance.
- Backtest numbers must reference immutable dataset/config/run evidence.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report green status without fresh output for the exact HEAD.
