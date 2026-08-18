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
- [x] STRATEGY-04 resolved: S4 has an explicit deterministic hybrid implementation and unknown strategy ids no longer silently alias S1.

## Strategy contract

The active strategy ids are S1-S4.

- **S1:** simple momentum.
- **S2:** 20-sample mean reversion.
- **S3:** 10-sample breakout.
- **S4:** deterministic hybrid of S1-S3. BUY requires at least two component BUY signals. The S2 SELL signal is accepted only when S1 and S3 are not signalling BUY; otherwise S4 returns HOLD.

`backend/tests/test_strategies_active.py` provides regression coverage for S4 confirmation, SELL behavior, HOLD behavior and rejection of unknown strategy ids.

## Preserved legacy

The remaining legacy implementation has been classified in `docs/LEGACY_AUDIT.md`.

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

1. Run the full executable validation gate on the exact resulting HEAD when an execution environment is available.
2. Specify the SQLModel-compatible Paper Trading / Risk migration boundary before porting legacy engine logic.
3. Review Alpha/Beta/Gamma legacy strategy logic against the active S1-S4 implementations and migrate only validated logic with deterministic tests/backtests.
4. Migrate notifications/activity only if retained as a product capability.
5. Perform the destructive legacy pruning defined in `docs/LEGACY_AUDIT.md`, followed by dependency/config cleanup.
6. Re-run a fresh repository audit and executable gate after pruning.

Future Live trading, authentication, notifications or payment flows must start from explicit product requirements and the active architecture. Do not reactivate the old router aggregator wholesale.
