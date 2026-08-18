# AUTOMATON Implementation Status

This file replaces the obsolete Mongo-first implementation plan. It describes current stabilization status rather than promising unimplemented architecture.

## Current baseline

- [x] FastAPI runtime starts from `backend/app/main.py`.
- [x] SQLModel + SQLite are the active persistence layer.
- [x] Agents domain reconciled with the active frontend.
- [x] Agents creation, replication, deposit, simulated PnL and termination use one SQLModel contract.
- [x] Dashboard reads real SQLModel metrics instead of hard-coded demo KPIs.
- [x] Crypto page uses the mounted crypto router and does not fabricate RSI values.
- [x] Ops Monitor reads persisted trades through REST polling.
- [x] Settings reflects the actual runtime instead of legacy Mongo/Live controls.
- [x] Frontend has one active API client: `frontend/src/lib/api.js`.
- [x] Legacy system/trading routers remain isolated from `app.main`.
- [x] Repository legacy inventory classified in `docs/LEGACY_AUDIT.md`.

## Confirmed active blocker

### STRATEGY-04 — S4 contract mismatch

The active contract exposes `S1` through `S4`, but `backend/app/services/strategies.py` implements only S1-S3 and currently falls back to S1 for S4. An S4 agent therefore executes S1 behavior while being labelled S4.

This must be resolved before execution certification. Do not invent hybrid semantics during cleanup: either define and test S4 explicitly, or stop accepting/advertising S4 while handling historical S4 rows safely.

## Preserved legacy

The remaining legacy implementation has now been classified in `docs/LEGACY_AUDIT.md`.

High-level decisions:

- **KEEP:** current SQLModel/SQLite runtime, AgentEngine, active agents/trades/crypto routes, active frontend and tooling.
- **MIGRATE / REDESIGN:** paper trading, live-trading boundary, advanced strategies, risk controls, portfolio metrics and notifications/activity where product value remains.
- **DELETE after dependency migration:** Mongo `DatabaseService`, legacy router aggregator, system/dashboard/strategy CRUD contracts, mock/registry layer, old replication implementation, current auth/payments/chat/memory implementations and replaced frontend pages.

No DELETE item should be removed until any selected MIGRATE capability has been detached from it.

## Validation gate

The repository contains backend and frontend regression tests for the stabilized contracts. A phase is only execution-verified after these commands run successfully on the same HEAD:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Current status: **not execution-verified**. GitHub Actions has no usable run for the audited HEAD, and the external execution environment used during the 2026-08-18 audit could not resolve `github.com`, so a fresh checkout could not be created. This is an evidence limitation, not a green or red test result.

## Ordered next work

1. Resolve **STRATEGY-04** and add regression coverage preventing silent strategy aliasing.
2. Run the full executable validation gate on the exact resulting HEAD when an execution environment is available.
3. Specify the SQLModel-compatible Paper Trading / Risk migration boundary before porting legacy engine logic.
4. Review Alpha/Beta/Gamma legacy strategy logic against the active S1-S3 implementations and migrate only validated logic with deterministic tests/backtests.
5. Migrate notifications/activity only if retained as a product capability.
6. Perform the destructive legacy pruning defined in `docs/LEGACY_AUDIT.md`, followed by dependency/config cleanup.
7. Re-run a fresh repository audit and executable gate after pruning.

Future Live trading, authentication, notifications or payment flows must start from explicit product requirements and the active architecture. Do not reactivate the old router aggregator wholesale.
