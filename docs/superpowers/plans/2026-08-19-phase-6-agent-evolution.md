# Phase 6 — Agent Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add evidence-aware lifecycle/fitness and non-duplicating agent replication while leaving automatic trading and Live disabled.

**Architecture:** Add an isolated `agent_evolution` domain and additive SQLModel tables. Fitness consumes existing Backtest/Paper evidence but never mutates those domains. Replication delegates all money movement to Accounting through a paired parent→child capital transfer transaction.

**Tech Stack:** FastAPI, SQLModel, SQLite, pytest, React/Vite/Vitest.

**Spec:** `docs/superpowers/specs/2026-08-19-phase-6-agent-evolution-design.md`

## Global Constraints

- No destructive SQLite column migration.
- Accounting remains the sole financial authority.
- Legacy Trade rows never count as fitness evidence.
- S1-S4 remain unchanged; no parameter mutation.
- Automated trading remains disabled.
- Live execution remains disabled.
- No success/green claim without exact-HEAD execution evidence.

---

### Task 1: Additive evolution records and bootstrap

**Files:**
- Create: `backend/app/models/agent_evolution.py`
- Create: `backend/app/agent_evolution/__init__.py`
- Create: `backend/app/agent_evolution/policy.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_agent_evolution_policy.py`

**Produces:** `EvolutionPolicy`, `AgentFitnessEvaluation`, `AgentLineage`, `AgentLifecycleEvent`, `bootstrap_evolution_policy()` and `bootstrap_lifecycle_baselines()`.

- [ ] Write tests for idempotent `evolution-v1` bootstrap and legacy baseline creation.
- [ ] Implement additive models and bootstrap helpers.
- [ ] Verify targeted tests when executable.
- [ ] Commit.

### Task 2: Evidence-aware fitness

**Files:**
- Create: `backend/app/agent_evolution/fitness.py`
- Test: `backend/tests/test_agent_fitness.py`

**Consumes:** Agent, Account, Fill, BacktestRun, BacktestRunEvidence, EvolutionPolicy.

**Produces:** `FitnessService.evaluate(agent_id) -> AgentFitnessEvaluation`.

- [ ] Write tests for missing evidence, strategy mismatch/source fingerprint absence, insufficient round trips, non-positive return/expectancy, excessive drawdown, insufficient Paper closes, non-positive Paper realized PnL, valid PASS, and legacy Trade exclusion.
- [ ] Implement the minimal fail-closed evaluator.
- [ ] Verify targeted tests when executable.
- [ ] Commit.

### Task 3: Atomic parent→child capital transfer

**Files:**
- Modify: `backend/app/accounting/service.py`
- Test: `backend/tests/test_agent_capital_transfer.py`

**Produces:** `AccountingService.transfer_to_child(parent_account_id, child_agent_id, amount, reason) -> tuple[Account, Account]`.

- [ ] Write tests for exact cash/funded-capital conservation, reserved-cash exclusion, insufficient funded/cash rejection, paired ledger entries and flat child account.
- [ ] Implement one-transaction transfer without creating external funding.
- [ ] Verify targeted tests when executable.
- [ ] Commit.

### Task 4: Replication service and lineage

**Files:**
- Create: `backend/app/agent_evolution/service.py`
- Modify: `backend/app/routers/agents.py`
- Test: `backend/tests/test_agent_replication_phase6.py`

**Produces:** `AgentEvolutionService.replicate(parent_agent_id)` and active replication endpoint.

- [ ] Write tests for REJECT without PASS fitness, ACTIVE requirement, same strategy inheritance, unique child, generation increment, lineage/events, allocation fraction, financial conservation and no strategy mutation.
- [ ] Implement replication using a fresh fitness evaluation for every attempt.
- [ ] Keep parent ACTIVE; do not use REPLICADO as an execution state.
- [ ] Verify targeted tests when executable.
- [ ] Commit.

### Task 5: Lifecycle reasons and evolution API

**Files:**
- Create: `backend/app/agent_evolution/router.py`
- Modify: `backend/app/routers/agents.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_agent_evolution_api.py`

**Produces:** `/api/evolution/status`, `/policies/active`, `/agents/{id}/fitness`, `/agents/{id}/lineage` plus kill reason persistence.

- [ ] Write API tests for status/no-Live/no-auto-trading, fitness inspection, lineage and explicit kill reason.
- [ ] Mount router and startup bootstrap.
- [ ] Update runtime markers to `agent_evolution=evidence_phase_6` while keeping automation blocked.
- [ ] Verify targeted tests when executable.
- [ ] Commit.

### Task 6: Frontend/runtime/documentation

**Files:**
- Modify: `frontend/src/lib/api.js`
- Modify: `frontend/src/pages/AgentsPage.jsx`
- Modify: `frontend/src/pages/SettingsPage.jsx`
- Modify related tests.
- Modify: `README.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `docs/ROADMAP.md`, `docs/AGENT_LIFECYCLE.md`, `docs/DATABASE_ARCHITECTURE.md`, `GEMINI.md`, `QWEN.md`.

- [ ] Restore replication UI only as an evidence-gated action with clear rejection messages; do not add automatic replication.
- [ ] Show lineage/fitness as evidence, not profitability claims.
- [ ] Reconcile runtime/docs to Phase 6.
- [ ] Verify frontend tests/build when executable.
- [ ] Commit.

### Task 7: Exact-HEAD audit

- [ ] Compare Phase 5 baseline `3757100513e643c4fb6c14eff21b2d5ff9d93d03` to final HEAD.
- [ ] Search for stale `replication blocked until Phase 6` and any accidental automatic/Live endpoints.
- [ ] Inspect CI/status/workflow runs on exact HEAD.
- [ ] Attempt `cd backend && pytest tests/ -v`, `cd frontend && npm test`, `cd frontend && npm run build` on a fresh checkout if environment allows.
- [ ] Report source/static closure separately from execution certification.