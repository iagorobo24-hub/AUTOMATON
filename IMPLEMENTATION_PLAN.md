# AUTOMATON Implementation Status

This file replaces the obsolete Mongo-first implementation plan. It describes current stabilization status rather than promising unimplemented architecture.

## Current baseline

- [x] FastAPI runtime starts from `backend/app/main.py`.
- [x] SQLModel + SQLite are the active persistence layer.
- [x] Agents domain reconciled with the active frontend.
- [x] Agents creation, replication, deposit, simulated PnL and termination use one SQLModel contract.
- [x] Dashboard reads real SQLModel metrics instead of hard-coded demo KPIs.
- [x] Crypto page uses the mounted crypto router.
- [x] Ops Monitor reads persisted trades through REST polling.
- [x] Settings reflects the actual runtime instead of legacy Mongo/Live controls.
- [x] Frontend has one active API client: `frontend/src/lib/api.js`.
- [x] Legacy system/trading routers remain isolated from `app.main`.

## Preserved legacy

The following are intentionally not classified as active and are not deleted automatically:

- Mongo `DatabaseService` and dependencies.
- TradingEngine / PaperTradingEngine / MockEngine / registry.
- auth, payments, notifications and other historical routers.
- rich Pydantic models from the Mongo architecture.
- frontend pages not registered by `App.jsx`.
- historical launch/infrastructure helpers that may still be useful for reference.

Removing or reviving those pieces requires a separate decision because they form a different architecture, not simple dead-code fragments.

## Validation gate

The repository contains backend and frontend regression tests for the stabilized contracts. A phase is only execution-verified after these commands run successfully on the same HEAD:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

GitHub Actions availability is environmental and must not be confused with code correctness.

## Next work

Future product development should begin from the active SQLModel architecture. Before implementing Live trading, authentication, notifications or payment flows, decide explicitly whether to migrate the corresponding legacy subsystem to SQLModel or redesign it as a separate service. Do not reactivate the old router aggregator wholesale.
