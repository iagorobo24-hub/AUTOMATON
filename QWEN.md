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

FastAPI + SQLModel + SQLite is the active backend baseline. React/Vite is the active frontend. The current `AgentEngine` contains synthetic price/random-close behavior and therefore is transition/test infrastructure, not compliant Paper execution.

## Required architecture

New trading work must respect the domain flow:

`Market Data -> Strategy -> Risk -> Paper Execution -> Portfolio/Accounting -> Metrics/Evidence`.

Agent lifecycle and UI sit around these contracts. A strategy does not own balances. Paper execution cannot send real orders. Accounting is the sole financial truth.

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
