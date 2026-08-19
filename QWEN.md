# QWEN.md — AUTOMATON Project Contract

Use `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md` as product truth. Use `backend/app/main.py` and `frontend/src/App.jsx` to verify what actually runs.

## Objective

AUTOMATON is being developed toward autonomous Paper Trading using **real market data and virtual capital**. It must produce evidence, not simulated-looking activity.

## Mode separation

- Synthetic/Test: synthetic + virtual; tests only.
- Backtest: historical real + virtual execution.
- Paper: current real + virtual capital.
- Live: current real + real capital; disabled until explicit Live gate/authorization.

Do not fabricate market data, fills, PnL, indicators or telemetry for Paper/Backtest/Live.

## Current state

- FastAPI + SQLModel + SQLite.
- React/Vite frontend.
- Synthetic AgentEngine disabled from normal startup.
- Phase 1 real-only Market Data active.
- Phase 2 Accounting authoritative.
- Phase 3 operator-only deterministic Paper active.
- Phase 4 persistent Risk active and mandatory for active Paper HTTP orders.
- Runtime: `risk=authoritative_phase_4`, `paper_trading=operator_only_phase_4`, `automated_trading=blocked_until_strategy_integration`, `live_execution=disabled`.
- Legacy Trade rows remain non-evidence.

## Required architecture

`Market Data -> Strategy Intent -> Risk -> Paper Execution -> Portfolio/Accounting -> Metrics/Evidence`.

A strategy does not own balances. Risk does not execute. Paper cannot send real orders. Accounting is the sole financial truth.

## Market Data rule

Real-data providers fail closed. Never reproduce the legacy BinanceService mock fallback in active trading paths.

## Accounting rule

- `backend/app/accounting/` owns financial state.
- Agent budget fields are compatibility mirrors only.
- Deposits are capital flows, not profit.
- Fills enter through AccountingService.
- Long-only scope; no invented short/margin/leverage semantics.
- Replication stays blocked until tested non-duplicating capital transfer exists.

## Paper rule

- Operator-only MARKET BUY/SELL.
- Price comes from real Market Data, never client input.
- `paper-v1` deterministic/versioned fee/slippage.
- Required persistent request-id idempotency.
- Ambiguous restart state -> `RECOVERY_REQUIRED`, never blind retry.
- No Live credentials/adapter.

## Risk rule

- `backend/app/risk/` and `backend/app/models/risk.py` own Risk policy/evidence.
- `risk-v1` is the initial active profile.
- Every active Paper HTTP order is evaluated before Paper Order/Fill creation.
- RiskDecision persists ALLOW/REJECT, profile/version, market provenance and exposure context.
- ALLOW decisions are one-time and payload-bound.
- REJECT decisions create no Paper financial state.
- Fail closed on paused Risk, inactive agent, stale/non-real data, missing real marks, Accounting mismatch or unresolved Paper recovery.
- BUY is constrained by order size/equity, total exposure, symbol concentration, open positions, realized loss, drawdown and cash reserve.
- A valid SELL reducing an existing long can bypass size/loss caps, but never integrity/recovery/data gates or oversell checks.
- Pause/resume is a circuit breaker only.
- Do not enable autonomous agents merely because Risk exists; strategy-to-Risk integration is a separate future step.

## Legacy handling

Mongo services, old Trading/Paper engines, legacy RiskManager, auth/payments/chat/notifications and unmounted pages are not active contracts. Migrate only useful concepts compatible with the current architecture.

## Strategies

S1-S4 are baseline code, not profitability evidence. Historical Alpha/Beta/Gamma material is research input only. Strategy promotion requires reproducible backtest and Paper evidence.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never claim verification without fresh execution on the current HEAD.
