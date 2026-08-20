# GEMINI.md — AUTOMATON Project Contract

## Read first

Canonical direction: `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/LIVE_TRADING_GATE.md`. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

Build autonomous Paper Trading on **real market data + virtual capital**, supported by reproducible evidence, disciplined Strategy Research and a fail-closed future Live boundary. Never present generated/mock results or Live Readiness as permission to move money.

## Current runtime

- FastAPI + SQLModel + SQLite; React/Vite.
- Phases 1–8: Market Data, Accounting, Paper, Risk, Backtesting, Evolution, autonomous Paper Runtime and Strategy Research.
- Phase 9 physically pruned Mongo/mock/legacy trading architecture.
- Phase 10 adds Live Readiness only.
- Runtime: `paper_trading=autonomous_phase_7`, `paper_runtime=runtime_phase_7`, `automated_trading=paper_enabled_phase_7`, `agent_evolution=evidence_phase_6`, `strategy_research=evidence_phase_8`, `legacy_pruning=pruned_phase_9`, `live_execution=readiness_phase_10`, `real_capital_execution=disabled`.

## Paper and Research

Paper stays virtual and always behind Risk. Research promotion is an evidence classification only; it does not deploy, mutate or authorize Live.

## Phase 10 — Live Readiness

`backend/app/live_execution/` is structurally separate from Paper.

Rules:

- production adapter is `DisabledLiveAdapter`;
- no method may transmit a real exchange order;
- no `/api/live/orders`, buy/sell or activation endpoint;
- no exchange secret persistence/write API;
- venue rules and `live-v1` hard limits fail closed;
- future intents are deterministic/idempotent preparation records only;
- intent preparation requires a promoted candidate, current matching source SHA and prior `ARCHITECTURE_READY` evidence;
- Market Data must report real, no synthetic fallback and no execution capability;
- Risk must be active/unpaused;
- unresolved Paper or Live recovery blocks readiness;
- Live emergency stop is persistent;
- reconciliation ambiguity produces `RECOVERY_REQUIRED` + circuit breaker and is never replayed;
- `RECOVERY_REQUIRED` is resolved only by explicit operator action with a reason;
- every readiness result keeps `real_capital_blocked=true`.

`ARCHITECTURE_READY` means technical gates passed for further review. It is not a trade permission, profitability statement or activation.

## Live authorization boundary

Do not add a concrete exchange trading adapter, credentials or real-capital activation without a new explicit scope. Venue selection, secret management, exchange-specific integration testing, operational drills and explicit authorization are future work.

## Evidence discipline

Never merge Backtest/Paper/Live records silently. Fixture tests prove software behavior, not trading performance. Never report test/build green without fresh exact-HEAD output.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```
