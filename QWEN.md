# QWEN.md — AUTOMATON Project Contract

Use `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md` as the product source of truth. Use `backend/app/main.py` and `frontend/src/App.jsx` to verify what actually runs today.

## Objective

AUTOMATON is being developed toward autonomous Paper Trading using **real market data and virtual capital**. The project must produce evidence, not simulated-looking activity.

## Mode separation

- Synthetic/Test: synthetic market + virtual money; tests only.
- Backtest: historical real market + virtual execution.
- Paper: current real market + virtual money.
- Live: current real market + real money; disabled until `docs/LIVE_TRADING_GATE.md` is satisfied and explicitly authorized.

Do not fabricate market data, fills, PnL, indicators or telemetry for Paper/Backtest/Live.

## Current state

FastAPI + SQLModel + SQLite is the active backend baseline. React/Vite is the active frontend. Normal startup does not start `AgentEngine`; that file remains only as explicit Synthetic/Test utility code.

The runtime reports transition mode with synthetic disabled, real Market Data available, authoritative Phase 2 accounting and Paper not implemented. Historical trade rows lack mode provenance, so they remain `legacy_unclassified` and excluded from verified metrics.

## Required architecture

New trading work must respect:

`Market Data -> Strategy -> Risk -> Paper Execution -> Portfolio/Accounting -> Metrics/Evidence`.

A strategy does not own balances. Paper execution cannot send real orders. Accounting is the sole financial truth.

## Market Data rule

Real-data providers fail closed. Never copy the legacy `BinanceService` mock fallback behavior into a Paper-capable path.

## Phase 2 accounting rule

`backend/app/accounting/` and `backend/app/models/accounting.py` own new financial state.

- `Agent.presupuesto_*` are compatibility mirrors, not accounting authority.
- Deposits are ledger capital flows, not profit.
- Fills enter through `AccountingService`.
- Long-only is the defined scope; do not invent short/margin behavior.
- Do not expose order/fill execution mutation endpoints before Phase 3.
- Killing an agent must not erase its accounting records.
- Replication is blocked until a tested capital-transfer policy prevents money duplication.
- Existing agents bootstrap from initial/funded capital only; legacy current balance is not trusted as PnL.

## Legacy handling

Historical Mongo services, old Paper/Trading engines, auth/payments/chat/notifications and unmounted frontend pages are not current product contracts. Migrate only proven-useful concepts; do not mount legacy routers as shortcuts.

## Strategies

S1-S4 are baseline code, not evidence of profitability. Historical Alpha/Beta/Gamma material contains hypotheses worth testing, not validated statistics. Any strategy promotion requires deterministic tests, real-data backtesting and Paper evidence.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never claim verification without fresh execution on the current HEAD.
