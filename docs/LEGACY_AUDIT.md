# Legacy audit and migration decisions

Audit origin: 2026-08-18  
Reconciled for Phase 0.1 synthetic isolation: 2026-08-19

## Purpose

Classify code that remains outside the active SQLModel runtime before destructive pruning. This document classifies implementations, not product ideas: a future capability can be valuable while its current legacy implementation is still unsuitable.

## Current runtime boundary

`backend/app/main.py` uses FastAPI + SQLModel + SQLite and mounts only agents, trades and crypto plus `/health` and `/api/estado`.

The normal runtime **does not start `AgentEngine`**. `services/agent_engine.py` remains versioned only as explicit Synthetic/Test utility code. Synthetic price generation and random-close behavior must not be reconnected to normal startup, Paper or evidence metrics.

S4 is explicitly implemented in `services/strategies.py`; the former silent S4->S1 fallback blocker is closed in source.

Pre-provenance `Trade` rows remain stored but are exposed as `legacy_unclassified` with `evidence_valid=false`. They are not valid Paper/Backtest evidence.

Executable validation remains pending whenever no environment can run the repository gate:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

## Classification rules

- **KEEP** — active baseline or required support for current/future phases.
- **TEST-ONLY** — useful only for deterministic/synthetic tests and prohibited from production/Paper evidence paths.
- **MIGRATE / REDESIGN** — product capability remains valuable, but implementation violates current architecture/contracts.
- **DELETE** — implementation has no justified role after dependencies/migrations are resolved.

## KEEP

| Area | Files / components | Decision |
|---|---|---|
| SQLModel persistence baseline | `backend/app/database.py`, `models/sql_models.py` | Keep as active persistence baseline. Evolve schema phase-by-phase rather than reviving Mongo. |
| Agent inventory/lifecycle API | `routers/agents.py`, `services/agent_replication.py` | Keep. Manual lifecycle actions are operator actions; automatic evidence-based evolution belongs to later phases. |
| Historical trade inspection | `routers/trades.py` | Keep temporarily. It must quarantine old rows from verified metrics until provenance-aware accounting replaces it. |
| UI market browser | `routers/crypto.py` | Keep as UI-facing real-data integration. It is not yet the engine Market Data contract. |
| Strategy baselines | `services/strategies.py` | Keep S1-S4 as deterministic baselines, not profitability claims. |
| Active frontend | `App.jsx`, `src/lib/api.js`, DashboardPro/CryptoPro/OpsMonitorPro/AgentsPage/SettingsPage and active feature components | Keep. Financial telemetry must respect evidence validity. |
| Desktop/dev tooling | Electron shell, npm scripts, launcher/Makefile and CI definition | Keep. |

## TEST-ONLY

| Area | Files / components | Constraint |
|---|---|---|
| Synthetic agent simulator | `services/agent_engine.py` | May be used only by explicit tests/test harnesses. Must not start from `app.main`, feed Paper, or write indistinguishable evidence into a normal runtime. |

## MIGRATE / REDESIGN

| Capability | Legacy implementation | Decision |
|---|---|---|
| Market data provider | `services/binance_service.py` | **REDESIGN.** Potentially reusable parsing/provider knowledge, but current behavior silently returns mock data when credentials/provider calls fail. Phase 1 must fail closed. |
| Paper trading | `routers/simulation.py`, `routers/paper_trading.py`, `services/paper_engine.py` | **REDESIGN.** Rebuild after Market Data and Accounting contracts; do not mount Mongo/registry implementation. |
| Live trading | `routers/trading.py`, `services/trading_engine.py`, parts of `binance_service.py` | **REDESIGN LATER.** No Live adapter before `LIVE_TRADING_GATE.md`. |
| Advanced strategies | `strategy_alpha.py`, `strategy_beta.py`, `strategy_gamma.py`, `indicators.py`, `regime_detector.py` | **REVIEW/MIGRATE.** Treat historical thresholds/performance statements as hypotheses until reproducible backtests. |
| Risk controls | `risk_manager.py`, legacy `routers/risk.py` | **REDESIGN.** Risk must sit independently between strategy intent and execution. |
| Portfolio/performance | `portfolio_snapshot.py` and legacy data paths | **REDESIGN.** Future accounting is authoritative; no competing balance/PnL calculations. |
| Notifications/activity | legacy notifications service/router/UI | **REDESIGN IF NEEDED.** Not a current core dependency. |

## DELETE after dependencies are resolved

- Mongo `DatabaseService` and Mongo injection stack.
- `api/api.py` legacy router aggregator.
- Legacy system/dashboard/strategy-CRUD routers.
- `services/mock_engine.py` and registry layer once no migration candidate needs them.
- `services/replication.py` legacy replication implementation.
- Current Mongo-backed auth/payments/chat/memory implementations unless separately redesigned as future product initiatives.
- Replaced/unreachable frontend pages after final reference audit.
- Mongo infrastructure/config/dependencies after all retained migration candidates are detached.

## Special Phase 1 warning

Do not import `BinanceService` as the new Market Data adapter merely because it already exposes `get_price`, `get_klines` or orderbook methods. Its current contract converts missing credentials and provider exceptions into generated data. That is incompatible with `docs/MARKET_DATA.md` and would recreate the original Paper-vs-synthetic defect.

## Dependency cleanup

Do not remove a dependency until its final retained consumer disappears. `core/config.py` and `backend/requirements.txt` still contain legacy Mongo/auth/Binance/risk settings/packages because legacy source remains versioned. Prune them during the later destructive cleanup, not during Market Data unless the relevant dependency becomes actively redesigned.

## Ordered next work

1. Obtain fresh execution certification for the Phase 0.1 HEAD when an execution environment is available.
2. Begin Phase 1 with a provider-neutral, fail-closed Real Market Data contract.
3. Build accounting before Paper execution.
4. Add Risk before unattended Paper operation.
5. Add reproducible Backtesting/Evidence before evidence-driven automatic agent evolution.
6. Review/migrate legacy advanced strategies only after those foundations exist.
7. Perform destructive legacy pruning only after selected migration value has been extracted.

## Stop conditions

- Do not reconnect `AgentEngine` to normal startup.
- Do not treat `legacy_unclassified` rows as strategy evidence.
- Do not use mock/generated provider fallback in Paper-capable paths.
- Do not mount `api/api.py` or Mongo routers as shortcuts.
- Do not implement Live trading during cleanup/Market Data.
- Do not claim tests/build green without fresh execution on the reported HEAD.
