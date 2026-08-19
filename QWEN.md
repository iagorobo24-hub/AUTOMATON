# QWEN.md — AUTOMATON Project Contract

Use `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md` as product truth. Use `backend/app/main.py` and `frontend/src/App.jsx` to verify what actually runs.

## Objective

AUTOMATON is being developed toward autonomous Paper Trading using **real market data and virtual capital**, with reproducible historical Backtest evidence. It must produce evidence, not simulated-looking activity.

## Mode separation

- Synthetic/Test: synthetic + virtual; tests only.
- Backtest: historical real + virtual execution.
- Paper: current real + virtual capital.
- Live: current real + real capital; disabled until explicit Live gate/authorization.

Do not fabricate market data, fills, PnL, indicators or telemetry for Backtest/Paper/Live.

## Current state

- FastAPI + SQLModel + SQLite.
- React/Vite frontend.
- Synthetic AgentEngine disabled from normal startup.
- Phase 1 real-only Market Data active.
- Phase 2 Accounting authoritative for Paper.
- Phase 3 operator-only deterministic Paper active.
- Phase 4 persistent Risk active and mandatory for normal Paper orders.
- Phase 5 immutable historical Backtesting/evidence active.
- Runtime: `risk=authoritative_phase_4`, `paper_trading=operator_only_phase_4`, `backtesting=evidence_phase_5`, `automated_trading=blocked_until_strategy_integration`, `live_execution=disabled`.
- Legacy Trade rows remain non-evidence.

## Required Paper architecture

`Market Data -> Strategy Intent -> Risk -> Paper Execution -> Portfolio/Accounting -> Metrics/Evidence`.

A strategy does not own balances. Risk does not execute. Paper cannot send real orders. Accounting is the active Paper financial truth.

## Backtest architecture

`real historical data -> immutable dataset SHA -> S1-S4 -> next-candle backtest execution -> isolated ledger -> persisted trades/equity/metrics`.

Backtesting is historical research and does not enable autonomous Paper trading.

## Market Data rule

Real current and historical providers fail closed. Never reproduce legacy BinanceService mock fallback in active paths.

## Accounting/Paper/Risk rules

- `backend/app/accounting/` owns active Paper financial state.
- Agent budget fields are compatibility mirrors only.
- Deposits are capital flows, not profit.
- Paper is operator-only MARKET BUY/SELL with real current price input.
- `paper-v1` is deterministic and request-id idempotent.
- Every normal Paper execution requires persisted current-profile one-time Risk ALLOW.
- Risk rejection creates no Paper financial state.
- Ambiguous recovery fails closed.
- Pause/resume is a circuit breaker only.
- Do not enable autonomous agents merely because Risk exists.

## Phase 5 Backtesting rule

- `backend/app/backtesting/` and `backend/app/models/backtesting.py` own historical evidence.
- Historical dataset creation uses real public provider data internally; clients do not inject arbitrary candles as real evidence.
- Datasets are immutable, SHA-256 identified and carry provider/symbol/interval/UTC-window/count provenance.
- Reject empty, duplicate, out-of-order, gapped or out-of-window historical series.
- Persist UTC semantics explicitly across SQLite.
- A signal from candle `t` cannot execute before candle `t+1` open.
- `backtest-v1`: long-only, no pyramiding, default 25% allocation, 10 bps adverse slippage, 10 bps fee.
- Open final positions are explicitly closed with `DATASET_END_EXIT`.
- Backtest ledger/evidence never mutates active Paper Account/Order/Fill/Position, PaperExecution, PaperRequest or RiskDecision.
- Persist BacktestRun/Trade/EquityPoint and keep undefined metrics null.
- Interrupted RUNNING runs are INVALID, not valid evidence.
- No optimizer in Phase 5.
- S1-S4 remain unchanged `baseline-v1` inputs. Do not tune them based on the evaluated period and then report that period as independent evidence.

## Legacy handling

Mongo services, old Trading/Paper engines, legacy RiskManager, auth/payments/chat/notifications and unmounted pages are not active contracts. Migrate only useful concepts compatible with current architecture.

## Strategy/evidence discipline

S1-S4 are Backtest-capable baseline code, not profitability evidence. Historical Alpha/Beta/Gamma material remains research input only. No profitable/optimized/validated claim without persisted reproducible evidence and explicit criteria.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never claim verification without fresh execution on the current HEAD.
