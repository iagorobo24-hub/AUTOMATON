# Phase 7 — 24/7 Paper Operation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a persistent autonomous Paper runtime that evaluates each configured agent once per new real closed candle and routes actionable strategy intents through Risk, Paper Execution and Accounting.

**Architecture:** Add an additive SQLModel runtime domain plus an in-process asyncio scheduler. Persistent session/cycle state is authoritative; restart never silently resumes prior RUNNING sessions. Existing S1-S4, Market Data, Risk, Paper and Accounting domains remain responsible for their own contracts.

**Tech Stack:** FastAPI, asyncio, SQLModel, SQLite, React/Vite/Vitest.

**Spec:** `docs/superpowers/specs/2026-08-19-phase-7-paper-runtime-design.md`

## Global Constraints

- Virtual capital only; Live remains disabled.
- No Redis/Celery in Phase 7.
- No synthetic fallback.
- No auto-replication or strategy mutation.
- Do not modify S1-S4 logic.
- Every autonomous trade requires real Market Data, persisted Risk ALLOW, Paper Execution and Accounting.
- A session/agent/candle may be evaluated once only.
- Persisted RUNNING sessions become RECOVERY_REQUIRED after process restart.
- Static tests authored are not execution evidence.

---

### Task 1: Runtime persistence and session lifecycle

**Files:**
- Create: `backend/app/models/paper_runtime.py`
- Create: `backend/app/paper_runtime/__init__.py`
- Create: `backend/app/paper_runtime/service.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_paper_runtime_sessions.py`

**Interfaces:**
- Produces `PaperRuntimeSession`, `PaperRuntimeAgent`, `PaperRuntimeCycle`, `PaperRuntimeEvent`.
- Produces `PaperRuntimeService.create_session/start/pause/resume/recover/stop`.

- [ ] Write tests for valid lifecycle, invalid transitions, unique agent assignment and restart recovery.
- [ ] Execute targeted test when environment allows and verify RED.
- [ ] Implement additive models and minimal service.
- [ ] Execute targeted test and verify GREEN when possible.
- [ ] Commit.

### Task 2: Deterministic cycle evaluation

**Files:**
- Create: `backend/app/paper_runtime/cycle.py`
- Test: `backend/tests/test_paper_runtime_cycle.py`

**Interfaces:**
- Consumes `MarketDataService`, `get_strategy`, active Account/Position state.
- Produces one durable cycle per `(session_id, agent_id, candle_close)` and deterministic BUY/SELL/HOLD intent.

- [ ] Test repeated polling of the same candle produces no second cycle/action.
- [ ] Test HOLD, BUY-flat, BUY-already-long, SELL-long and SELL-flat.
- [ ] Test inactive agent fails closed.
- [ ] Implement runtime-v1 sizing and signal evaluation without changing strategy code.
- [ ] Commit.

### Task 3: Risk-gated autonomous Paper execution

**Files:**
- Create: `backend/app/paper_runtime/execution.py`
- Modify only if necessary: `backend/app/paper_execution/service.py`
- Test: `backend/tests/test_paper_runtime_execution.py`

**Interfaces:**
- Stable request id: `runtime-v1|session|agent|symbol|candle_close|signal` SHA-256.
- Origin: `strategy_runtime`.
- Every action gets Risk ALLOW before Paper execution.

- [ ] Test successful BUY/SELL persists Risk + Paper provenance.
- [ ] Test Risk reject produces no Paper fill.
- [ ] Test duplicate cycle/request cannot double execute.
- [ ] Test Paper recovery ambiguity moves session to RECOVERY_REQUIRED.
- [ ] Implement minimal orchestration using existing domains.
- [ ] Commit.

### Task 4: Scheduler, recovery and provider resilience

**Files:**
- Create: `backend/app/paper_runtime/scheduler.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_paper_runtime_recovery.py`

**Interfaces:**
- One asyncio task per running session in the current process.
- Startup `recover_interrupted_runtime_sessions(session)`.

- [ ] Test persisted RUNNING/DEGRADED sessions become RECOVERY_REQUIRED after restart.
- [ ] Test provider unavailable/invalid produces skipped cycle/event and no fake data.
- [ ] Test five consecutive operational failures mark DEGRADED.
- [ ] Test financial ambiguity marks RECOVERY_REQUIRED immediately.
- [ ] Implement scheduler with explicit start/pause/resume/stop task ownership.
- [ ] Commit.

### Task 5: Runtime API and observability

**Files:**
- Create: `backend/app/paper_runtime/router.py`
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_api_integration.py`
- Test: `backend/tests/test_paper_runtime_api.py`

**Interfaces:**
- Mount `/api/runtime` surfaces defined by spec.

- [ ] Test create/list/detail/cycles/start/pause/resume/recover/stop.
- [ ] Test status reports virtual-only, real-data-only, no Live, no auto-replication.
- [ ] Mount router and runtime v2.10.0 state.
- [ ] Commit.

### Task 6: Frontend operational visibility

**Files:**
- Modify: `frontend/src/lib/api.js`
- Modify: `frontend/src/pages/SettingsPage.jsx`
- Modify: active Ops Monitor feature/page after inspection.
- Test: corresponding Vitest files.

- [ ] Add runtime API client.
- [ ] Show session state, heartbeat, last cycle/signal/outcome/failure count.
- [ ] Ensure UI has no Live or auto-replication controls.
- [ ] Commit.

### Task 7: Documentation and exact-HEAD audit

**Files:**
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `IMPLEMENTATION_PLAN.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/PAPER_TRADING.md`
- Modify: `docs/DATABASE_ARCHITECTURE.md`
- Modify: `GEMINI.md`
- Modify: `QWEN.md`

- [ ] Reconcile runtime state and Phase 7 contracts.
- [ ] Compare exact Phase 6 baseline to final HEAD; verify scope and no divergence.
- [ ] Search for obsolete `blocked_until_phase_7_runtime` / `operator_only_phase_4` active-state claims.
- [ ] Check GitHub statuses/workflow runs.
- [ ] Attempt `pytest tests/ -v`, `npm test`, `npm run build` on exact HEAD.
- [ ] Attempt sustained real-provider Paper smoke only if executable environment exists.
- [ ] Mark source/static gate complete only if code/docs audit is coherent; keep execution certification pending without fresh evidence.
