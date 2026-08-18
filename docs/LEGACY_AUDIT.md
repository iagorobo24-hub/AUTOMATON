# Legacy audit and migration decisions

Audit date: 2026-08-18
Audited HEAD: `bba2c07ea540558279a08748877556771a15842a`

## Purpose

Classify the code that remains outside the active SQLModel runtime before any destructive pruning. This document classifies implementations, not product ideas: a feature can be valuable in the future while its current legacy implementation is still a DELETE candidate.

## Verification status

The active runtime remains `backend/app/main.py` with FastAPI + SQLModel + SQLite + `AgentEngine`, and only mounts agents, trades and crypto plus `/health` and `/api/estado`.

Executable validation is **not currently available**. A fresh external checkout failed before downloading the repository because the execution environment could not resolve `github.com`, and there are no usable GitHub Actions results for this HEAD. Therefore the repository is statically reviewed but not execution-verified.

Required gate when execution is available:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

## Active blocker discovered during this audit

### STRATEGY-04 — S4 contract is not implemented

`StrategyEnum` exposes `S1`, `S2`, `S3`, `S4` and the active Agents UI allows S4. `AgentEngine` resolves the strategy through `services/strategies.py`, but that factory only implements S1-S3 and silently falls back to S1 for any other value. Consequently an S4 agent currently executes S1 behavior while being labelled S4.

Classification: **confirmed active bug**.

Do not invent S4 semantics during cleanup. Before execution certification, make an explicit product decision: either implement a defined S4 Hybrid strategy with tests, or stop accepting/advertising S4 while preserving safe handling of any historical S4 rows.

## Classification rules

- **KEEP** — used by the active runtime or required support for it.
- **MIGRATE / REDESIGN** — product capability remains valuable, but current implementation is coupled to the Mongo/legacy architecture and must not be mounted as-is.
- **DELETE** — current implementation has no justified role in the active product. Delete only after dependent MIGRATE work has been completed where applicable.

## KEEP

| Area | Files / components | Evidence / rationale |
|---|---|---|
| SQLModel persistence | `backend/app/database.py`, `models/sql_models.py` and active model exports | Source of truth used by `app.main`, agents and trades. |
| Agent lifecycle | `services/agent_engine.py`, `services/agent_replication.py`, `routers/agents.py` | Active runtime. |
| Active trades | `routers/trades.py` | Used by Dashboard and Ops Monitor. |
| Market data | `routers/crypto.py`, active `httpx` dependency | Mounted by `app.main` and consumed by Crypto. |
| Active strategy factory | `services/strategies.py` | Used directly by `AgentEngine`; S1-S3 are active. S4 is separately blocked above. |
| Active frontend | `App.jsx`, `src/lib/api.js`, DashboardPro/CryptoPro/OpsMonitorPro/AgentsPage/SettingsPage and their active feature components | These are the only routes registered by `App.jsx`. |
| Desktop/dev tooling | Electron shell, canonical npm scripts, reconciled launcher/Makefile and CI definition | Supports the current 8000/5173 runtime. |

## MIGRATE / REDESIGN

These capabilities fit AUTOMATON's likely product direction, but their existing code is not a safe extension point.

| Capability | Legacy implementation | Decision |
|---|---|---|
| Paper trading with real market data | `routers/simulation.py`, `routers/paper_trading.py`, `services/paper_engine.py` | **MIGRATE / REDESIGN.** Rebuild on SQLModel Agent/Trade and a defined execution abstraction. Do not reuse Mongo agent documents or registry state as source of truth. |
| Real/live trading | `routers/trading.py`, `services/trading_engine.py`, `services/binance_service.py` | **MIGRATE / REDESIGN.** Keep only reviewed exchange/market-data techniques that are still correct. Live execution requires a new explicit safety contract before mounting anything. |
| Advanced strategies | `strategy_alpha.py`, `strategy_beta.py`, `strategy_gamma.py`, `indicators.py`, `regime_detector.py` | **MIGRATE / REVIEW.** Potentially valuable strategy logic, but currently consumed by legacy engines rather than `AgentEngine`. Port only after strategy contracts and backtesting criteria are defined. |
| Risk controls | `risk_manager.py`, legacy `routers/risk.py` | **MIGRATE / REDESIGN.** Risk belongs in the active trading path, not in an unmounted Mongo router. |
| Portfolio snapshots / performance | `portfolio_snapshot.py` and related legacy data paths | **MIGRATE / REDESIGN** if required by the next trading phase. Persist against SQLModel entities. |
| Notifications / activity | `services/notifications.py`, `routers/notifications.py`, historical activity UI | **MIGRATE / REDESIGN.** Useful operational capability, but current injection path belongs to `DatabaseService`. |
| Simulation UI | `frontend/src/pages/SimulationPage.jsx` | **MIGRATE / REDESIGN** only when the SQLModel paper-simulation backend exists. Do not remount it against legacy endpoints. |
| Activity UI | `frontend/src/pages/ActivityPage.jsx` | **MIGRATE / REDESIGN** together with the new notification/event model, if retained as a product capability. |

## DELETE

The following implementations should be removed in the later pruning phase, not reactivated.

| Area | Files / components | Reason |
|---|---|---|
| Mongo source of truth | `services/database.py` (`DatabaseService`), `api/deps.py` Mongo dependencies | Replaced by SQLModel/SQLite. Retain only until all selected MIGRATE capabilities stop importing it. |
| Legacy router aggregator | `api/api.py` | Registers a second application surface that `app.main` intentionally does not use. Mounting it would reintroduce the split architecture. |
| Legacy system/settings controls | `routers/system.py` and associated Mongo/engine controls | Already replaced by honest runtime Settings. |
| Legacy dashboard API | `routers/dashboard.py` | Active Dashboard derives metrics from agents/trades/health. Second dashboard contract is unnecessary. |
| Legacy strategy CRUD router | `routers/strategies.py` | Stores Mongo strategy documents unrelated to the active S1-S4 enum contract. |
| Mock engine / registry | `services/mock_engine.py`, `services/registry.py` | Global engine registry is only support for legacy paper/mock architecture. Replace through explicit active runtime ownership if paper trading is rebuilt. |
| Old replication service | `services/replication.py` | Active SQLModel replication uses `services/agent_replication.py`. |
| Auth implementation | `routers/auth.py`, Mongo-backed auth service/models once dependencies are removed | Current product is local and auth is unmounted/Mongo-backed; implementation is incomplete (for example register calls an undefined `get_password_hash`). If multi-user auth becomes a requirement, design it for the active persistence model rather than reviving this code. |
| Payments implementation | `routers/payments.py` and payment-specific legacy configuration/dependencies | Unmounted, Mongo-backed and tied to historical Stripe/Emergent integration. Payments are not part of the current product contract. Rebuild only after a monetization requirement exists. |
| Chat / LLM legacy surface | `routers/chat.py`, old Chat page and LLM-specific configuration not used elsewhere | Not present in the active product. Reintroduce only as a new scoped feature with an explicit contract. |
| Memory legacy UI | `frontend/src/pages/Memory.jsx` and related unused components | Not registered by the active application and not part of the current trading runtime. |
| Replaced pages | `DashboardPage.jsx`, `Dashboard.jsx`, `Agents.jsx`, `Settings.jsx`, `Trades.jsx`, `CryptoPage.jsx` and other pages superseded by the five routes in `App.jsx` | Duplicate historical UI. Delete after a final import/reference check. |
| Wallet/Login pages | `WalletPage.jsx`, `LoginPage.jsx` | Depend conceptually on payments/auth capabilities that are not active. Rebuild only if those product requirements return. |
| Mongo infrastructure | `.devops/docker-compose.yml` and Mongo-only settings/dependencies | Delete after no remaining MIGRATE candidate imports Mongo. |

## Dependency cleanup after migration decisions

Do not remove Python dependencies before their final consumers disappear. After the MIGRATE/DELETE work, re-scan imports and then remove legacy-only packages such as `motor`, `pymongo`, `python-binance`, JWT/auth packages or other integration libraries only when no retained code imports them.

Likewise prune legacy settings from `core/config.py` only after the corresponding code has been deleted or migrated. At present the configuration file still contains Mongo, JWT, Stripe, Live/Paper, notification and risk settings that do not govern `AgentEngine`.

## Ordered next work

1. **Resolve STRATEGY-04**: define S4 or stop exposing it; add regression coverage so no strategy silently aliases another.
2. **Execution certification**: run backend tests, frontend tests and frontend build on the exact resulting HEAD once an execution environment is available.
3. **Paper/risk migration design**: specify a SQLModel-compatible execution interface, persistence semantics, market-data boundary and safety rules. Extract only validated logic from legacy engines.
4. **Advanced strategy review**: compare S1-S3 active strategies with Alpha/Beta/Gamma legacy algorithms; port only evidence-backed logic and add deterministic tests/backtests.
5. **Notifications/activity migration** if retained.
6. **Destructive pruning**: delete DatabaseService, legacy aggregator, rejected routers/services/pages and then remove unused dependencies/configuration.
7. **Fresh full audit + executable gate** after pruning.

## Stop conditions

- Do not mount `api/api.py` or Mongo routers to make tests/UI pass.
- Do not implement Live trading as part of cleanup.
- Do not silently invent S4 behavior.
- Do not delete a legacy module while a selected MIGRATE capability still imports it.
- Do not claim tests/build are green without fresh execution on the reported HEAD.
