# GEMINI.md — AUTOMATON Project Contract

## Read first

Canonical product direction is defined by `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md`. Inspect `backend/app/main.py` and `frontend/src/App.jsx` before claiming current implementation status.

## Product objective

Build a trustworthy autonomous-agent trading platform whose immediate target is **Paper Trading on real market data with virtual capital**.

Never present synthetic/random/mock results as Paper, Backtest or Live evidence.

## Current runtime

- FastAPI + SQLModel + SQLite.
- React/Vite frontend.
- Synthetic `AgentEngine` is not started by normal runtime.
- Phase 1 Market Data is real-only and fail-closed.
- Phase 2 Accounting is authoritative for financial state.
- Phase 3 Paper MARKET execution is operator-only, deterministic and idempotent.
- Phase 4 Risk is active and mandatory for the active Paper HTTP order path.
- Runtime reports `risk=authoritative_phase_4`, `paper_trading=operator_only_phase_4`, `automated_trading=blocked_until_strategy_integration`, `live_execution=disabled`.
- Historical Trade rows remain `legacy_unclassified`.

## Architecture boundaries

New trading work follows:

`Market Data -> Strategy Intent -> Risk -> Paper Execution -> Portfolio/Accounting -> Metrics/Evidence`.

Strategy code does not own balances or execute orders. Risk never mutates balances. Paper never sends real exchange orders. Accounting remains the sole financial truth.

## Market Data constraint

Real-data providers fail closed. Never copy legacy `BinanceService` mock/generated fallback behavior into active trading paths.

## Accounting constraint

- `backend/app/accounting/` owns new financial state.
- `Agent.presupuesto_*` are compatibility mirrors only.
- Deposits are funding, never profit.
- Fills go through `AccountingService`.
- Long-only is the defined scope; do not invent short/margin/leverage semantics.
- Replication stays blocked until explicit non-duplicating capital transfer exists.

## Paper constraint

- Current Paper is operator-only MARKET BUY/SELL.
- Execution price comes from real Market Data, never client input.
- `paper-v1` is deterministic/versioned.
- Paper mutations require persistent `request_id` idempotency.
- Ambiguous recovery becomes `RECOVERY_REQUIRED`; never blindly retry.
- Paper has no Live credentials/adapter.

## Phase 4 Risk constraint

`backend/app/risk/` and `backend/app/models/risk.py` own active Risk policy/evidence.

- Active initial profile is `risk-v1`.
- Risk decisions are persisted ALLOW/REJECT evidence with profile/version, real-market provenance and account/exposure context.
- Active Paper API orders must receive Risk ALLOW before Paper Order/Fill creation.
- ALLOW is one-time consumable and payload-bound.
- REJECT creates no Paper financial state.
- Risk fails closed on stale/non-real data, inactive agent, missing real marks, accounting mismatch, unresolved Paper recovery or paused circuit breaker.
- BUY limits include order/equity, total exposure, symbol concentration, open positions, realized loss, drawdown and cash reserve.
- Valid risk-reducing SELL may bypass size/loss caps but cannot bypass integrity/recovery/data checks or oversell protection.
- `/api/risk/pause` and `/resume` are circuit-breaker controls only; they do not enable autonomous trading.
- Do not connect strategies automatically just because Risk exists. That integration is a later explicit step.

## Legacy

Mongo DatabaseService, old Trading/Paper engines, legacy RiskManager, auth/payments/chat/notifications and unmounted pages are not active contracts. Migrate only useful concepts compatible with the current architecture.

## Strategy/evidence rules

- S1-S4 are baseline implementations, not proven profitable strategies.
- Alpha/Beta/Gamma historical ideas are hypotheses only.
- No profitable/optimized/safe claim without reproducible evidence.
- Financial telemetry must preserve mode/provenance.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report green status without fresh output for the exact HEAD.
