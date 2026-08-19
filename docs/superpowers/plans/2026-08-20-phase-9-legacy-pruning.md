# Phase 9 — Legacy Pruning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the superseded Mongo/mock/trading architecture and dead frontend surfaces without changing active Phase 1–8 financial/evidence behavior.

**Architecture:** Prune by dependency evidence in destructive waves. Add architecture guards first, delete only zero-consumer legacy code, clean dependencies/config after final consumers disappear, then reconcile documentation and perform an exact-HEAD audit. SQLModel/SQLite and the Phase 1–8 domains remain authoritative.

**Tech Stack:** Python 3, FastAPI, SQLModel/SQLite, pytest, React/Vite, Vitest, GitHub Contents API.

**Spec:** `docs/superpowers/specs/2026-08-20-phase-9-legacy-pruning-design.md`

## Global Constraints

- Work directly on `main`, as explicitly authorized for AUTOMATON.
- Do not change S1–S4 algorithms or `research-v1`, `risk-v1`, `paper-v1`, `runtime-v1`, Accounting semantics, recovery or idempotency contracts.
- Do not add Live execution, credentials, strategy mutation, auto-replication or auto-deployment.
- Fetch and reference-audit every destructive candidate before deletion.
- Do not delete `backend/app/models/enums.py`; active `models/sql_models.py` imports `AgentStatus`, `StrategyEnum` and `TradeType` from it.
- Do not remove a dependency/config key until its final retained consumer is proven absent.
- Preserve useful Alpha/Beta/Gamma concepts in documentation, not legacy executable code.
- Tests authored but not executable in this tool environment remain explicitly unverified.

---

### Task 1: Freeze the active boundary and add pruning guards

**Files:**
- Create: `backend/tests/test_legacy_pruning_architecture.py`
- Modify: `backend/tests/test_api_integration.py`
- Modify late in phase: `docs/LEGACY_AUDIT.md`

**Interfaces:**
- Consumes: active `app.main`, `backend/requirements.txt`, repository paths.
- Produces: regression guards that fail while prohibited legacy architecture remains.

- [ ] Write tests asserting final legacy engine/router/Mongo files do not exist.
- [ ] Assert active `app.main` has no Mongo/DatabaseService/AgentEngine imports and no legacy routes.
- [ ] Assert requirements contain no Mongo/auth/python-binance/legacy-rate-limit dependencies once final consumers are removed.
- [ ] Assert active financial/evidence domain source does not import legacy mock/synthetic/Mongo engines.
- [ ] Keep S1–S4 behavior/source untouched.
- [ ] Run targeted tests if an executable checkout becomes available; otherwise record as authored/unexecuted.

### Task 2: Remove superseded financial/orchestration engines

**Delete candidates after zero-retained-consumer search:**
- `backend/app/routers/simulation.py`
- `backend/app/routers/paper_trading.py`
- `backend/app/routers/trading.py`
- `backend/app/routers/risk.py` (legacy router only)
- `backend/app/services/paper_engine.py`
- `backend/app/services/trading_engine.py`
- `backend/app/services/replication.py`
- `backend/app/services/mock_engine.py`
- `backend/app/services/registry.py`
- `backend/app/services/portfolio_snapshot.py`
- `backend/app/services/risk_manager.py`

- [ ] Search imports/references for each candidate.
- [ ] Delete only candidates whose retained consumers are absent or are deleted in the same wave.
- [ ] Search again for dangling imports/names.
- [ ] Verify the active `app/risk/` domain remains untouched.

### Task 3: Retire synthetic SQLModel legacy engine

**Delete candidates if zero valid test/tool consumers:**
- `backend/app/services/agent_engine.py`
- `backend/app/services/agent_replication.py`

- [ ] Search `AgentEngine`, `agent_engine`, `replicate_agent` and `agent_replication` consumers.
- [ ] If no retained test/tool consumer exists, delete both; do not preserve capital-duplicating replication for compatibility.
- [ ] Confirm `AgentEvolutionService` remains the only active replication path.

### Task 4: Remove Mongo-backed inactive product stack

**Delete candidates after graph confirmation:**
- `backend/app/api/api.py`
- `backend/app/api/deps.py`
- `backend/app/core/seed.py`
- `backend/app/services/database.py`
- `backend/app/services/notifications.py`
- `backend/app/services/auth_service.py`
- inactive routers: auth/chat/payments/notifications/dashboard/strategies/audit/signals/system plus any remaining Mongo-only router
- legacy Pydantic model modules used only by that stack: `models/auth.py`, `models/agent.py`, `models/requests.py`, `models/system.py`, `models/trading.py`

- [ ] Search retained consumers before each deletion set.
- [ ] Preserve `models/enums.py` because SQLModel active models depend on it.
- [ ] Delete the obsolete aggregator/injection stack so importing `app` cannot initialize Mongo through legacy modules.
- [ ] Re-search `DatabaseService`, `motor`, `pymongo`, `get_db_service`, `get_notification_service`.

### Task 5: Remove unsafe legacy Binance and historical strategy executables

**Delete candidates after reference proof:**
- `backend/app/services/binance_service.py`
- `backend/app/services/strategy_alpha.py`
- `backend/app/services/strategy_beta.py`
- `backend/app/services/strategy_gamma.py`
- `backend/app/services/indicators.py`
- `backend/app/services/regime_detector.py`

- [ ] Confirm active crypto UI route uses CoinGecko/httpx and active Market Data uses `BinancePublicMarketDataProvider`, not legacy `BinanceService`.
- [ ] Confirm old strategies are no longer imported after Tasks 2–4.
- [ ] Verify `docs/STRATEGIES.md` already preserves regime/ATR/liquidity/time-exit/trailing/range/momentum hypotheses without accepting historical performance claims.
- [ ] Delete executable legacy files.
- [ ] Search for mock fallback helpers and `python-binance` imports afterward.

### Task 6: Prune unreachable frontend legacy surfaces

**Protected entry graph:** `main.jsx -> App.jsx -> DashboardPro/CryptoPro/OpsMonitorPro/AgentsPage/SettingsPage` plus their imported feature/shared/UI components.

**Candidates:** old Activity/Chat/Login/Memory/Agents/Dashboard/DashboardPage/Trades/Settings/CryptoPage pages; obsolete layout/memory/old dashboard/agent components; mock data/types and empty feature placeholders, only when zero retained imports are proven.

- [ ] Search each candidate from active imports, tests and current source.
- [ ] Delete pages that are not routed/imported and already depend on removed/nonexistent clients such as `notificationsAPI`, `chatAPI` or `../services/api.js`.
- [ ] Delete mock financial data not used by the active tree.
- [ ] Delete orphan components only after their final page consumer is removed and search confirms zero retained import.
- [ ] Keep ErrorBoundary, active feature components and all UI primitives referenced by the active tree.
- [ ] Do not redesign active UI.

### Task 7: Clean dependencies and configuration

**Files:**
- Modify: `backend/requirements.txt`
- Modify or delete if fully orphaned: `backend/app/core/config.py`
- Inspect environment/example/script files before deleting settings.

- [ ] Search final retained source for `motor`, `pymongo`, `jwt`, `passlib`, `multipart`, `binance`, `slowapi`.
- [ ] Remove packages only when zero retained consumers remain.
- [ ] Search retained source for `settings`/`core.config`; if none, delete the legacy config module, otherwise reduce only proven-dead fields.
- [ ] Do not remove numpy/pandas/asyncpg/aiosqlite or other uncertain dependencies without complete retained-consumer proof.

### Task 8: Make Phase 9 status observable and reconcile API guards

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_api_integration.py`
- Modify: frontend Settings only if status display needs a minimal new field.

- [ ] Bump backend version to `2.12.0` only after pruning is coherent.
- [ ] Add `legacy_pruning=pruned_phase_9` to root/health/estado without changing financial behavior.
- [ ] Keep Live disabled and Phase 1–8 runtime identifiers unchanged.
- [ ] Update route-inventory tests to assert legacy surfaces remain absent.

### Task 9: Reconcile documentation with the remaining tree

**Files:**
- Modify: `docs/LEGACY_AUDIT.md`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `IMPLEMENTATION_PLAN.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/DATABASE_ARCHITECTURE.md`
- Modify: `GEMINI.md`
- Modify: `QWEN.md`
- Modify if needed: `docs/STRATEGIES.md`

- [ ] Replace old pre-Phase-1 runtime description with exact Phase 9 inventory.
- [ ] Record each legacy classification/delete decision and special-case rationale.
- [ ] State Mongo/old engines/mock fallback status based on actual remaining files.
- [ ] Keep execution certification and source/static closure separate.

### Task 10: Exact-HEAD closure

- [ ] Fetch final `main` HEAD.
- [ ] Compare from Phase 8 close `6fd2a0597849202af9bb6af55ef5d6d413c0b272` to final HEAD.
- [ ] Confirm `backend/app/services/strategies.py` is absent from the diff.
- [ ] Search for Mongo/DatabaseService/mock_engine/paper_engine/trading_engine/binance_service/legacy route references in retained production source.
- [ ] Search for Live/order-credential capability accidentally introduced by Phase 9.
- [ ] Check GitHub status checks/workflow runs for final HEAD.
- [ ] Attempt fresh clone + backend pytest + frontend test/build. If DNS still blocks clone, report exact failure without claiming green.
- [ ] Mark Phase 9 source/contract/static gate complete only after these checks are coherent.
