# Phase 8 Strategy Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a persistent reproducible research layer that evaluates unchanged strategy configurations across chronological Backtest evidence and completed Phase 7 forward Paper evidence, then records manual evidence-gated promotion without optimization or Live activation.

**Architecture:** Create an additive `strategy_research` domain over existing Backtest, Paper Runtime, PaperExecution, Accounting and strategy fingerprint evidence. Research owns studies/windows/evaluations/candidates only; it never owns trading balances, strategy source mutation or execution.

**Tech Stack:** FastAPI, SQLModel, SQLite, Decimal, React/Vite client status integration, pytest/Vitest contracts.

**Spec:** `docs/superpowers/specs/2026-08-19-phase-8-strategy-research-design.md`

## Global Constraints

- Work directly on `main`; no PR/branch/history rewrite.
- S1-S4 source must remain unchanged.
- Historical evidence must come only from persisted Phase 5 completed runs/datasets/source fingerprints.
- Forward evidence must come only from Phase 7 sessions and `PaperExecution(origin=strategy_runtime)`.
- Missing/ambiguous evidence fails closed.
- No optimizer, strategy mutation, auto-deploy, auto-replication or Live.
- Tables are additive for SQLite compatibility.
- Tests authored are not execution certification without fresh command output.

---

### Task 1: Persist research policy and evidence objects

**Files:**
- Create: `backend/app/models/strategy_research.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/app/strategy_research/__init__.py`
- Create: `backend/app/strategy_research/policy.py`
- Test: `backend/tests/test_strategy_research_policy.py`

**Interfaces:**
- Produces `ResearchPolicy`, `ResearchStudy`, `ResearchWindow`, `ResearchEvaluation`, `StrategyCandidate`.
- Produces `bootstrap_research_policy(session) -> ResearchPolicy` for `research-v1`.

- [ ] Write tests proving additive tables and idempotent `research-v1` bootstrap with exact thresholds.
- [ ] Implement models and bootstrap.
- [ ] Review uniqueness/index constraints so one study/window/evaluation/candidate identity is unambiguous.
- [ ] Commit.

### Task 2: Study and chronological-window service

**Files:**
- Create: `backend/app/strategy_research/service.py`
- Test: `backend/tests/test_strategy_research_windows.py`

**Interfaces:**
- `StrategyResearchService.create_study(name, strategy_id, notes=None)`
- `StrategyResearchService.add_window(study_id, role, backtest_run_id)`
- Window role is one of `TRAIN`, `VALIDATION`, `OOS`.

- [ ] Write tests for study/window persistence.
- [ ] Write tests rejecting non-COMPLETED runs, missing source SHA, strategy mismatch, source mismatch, cost/execution mismatch, overlap and chronology violations.
- [ ] Implement minimal service validation using referenced BacktestDataset actual_start/actual_end and BacktestRunEvidence.
- [ ] Commit.

### Task 3: Historical evaluation engine

**Files:**
- Create: `backend/app/strategy_research/evaluator.py`
- Test: `backend/tests/test_strategy_research_historical_evaluation.py`

**Interfaces:**
- `ResearchEvaluator.evaluate(study_id) -> ResearchEvaluation`
- Evaluation always persists PASS/REJECT with reason code.

- [ ] Write tests for required TRAIN/VALIDATION/OOS coverage.
- [ ] Write tests for >=5 VALIDATION/OOS round trips, positive return/expectancy, OOS drawdown <= 0.15, profit factor >=1.05 when defined, <=50% relative OOS return degradation.
- [ ] Implement conservative aggregation: all required VALIDATION and OOS windows must satisfy gates; missing metrics reject.
- [ ] Commit.

### Task 4: Forward Paper evidence gate

**Files:**
- Modify: `backend/app/strategy_research/evaluator.py`
- Test: `backend/tests/test_strategy_research_forward_evidence.py`

**Interfaces:**
- Qualifying evidence uses STOPPED `PaperRuntimeSession`, attached matching-strategy agents, runtime cycles, FILLED SELL PaperExecution with `origin=strategy_runtime`, and Account.realized_pnl.

- [ ] Write tests rejecting RUNNING/DEGRADED/RECOVERY_REQUIRED sessions.
- [ ] Write tests rejecting strategy mismatch, no runtime cycles, <3 FILLED closing SELL executions, non-runtime Paper origin, non-positive realized PnL and unresolved Paper recovery.
- [ ] Implement forward evidence collection and persist referenced session ids/count/PnL snapshot into ResearchEvaluation.
- [ ] Commit.

### Task 5: Current-source drift and promotion

**Files:**
- Create: `backend/app/strategy_research/promotion.py`
- Test: `backend/tests/test_strategy_research_promotion.py`

**Interfaces:**
- `promote(study_id, note=None) -> StrategyCandidate`
- Every call creates a fresh evaluation first.

- [ ] Write tests that current strategy SHA drift rejects promotion.
- [ ] Write test proving an old PASS cannot be reused after evidence/source drift.
- [ ] Write tests that REJECT creates no candidate and PASS creates one candidate linked to the fresh evaluation.
- [ ] Write duplicate-promotion idempotency/uniqueness test.
- [ ] Implement promotion without source/runtime mutation.
- [ ] Commit.

### Task 6: Research API and runtime contract

**Files:**
- Create: `backend/app/strategy_research/router.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_strategy_research_api.py`
- Modify: `backend/tests/test_api_integration.py`

**Interfaces:**
- `/api/research/status`
- `/api/research/policies/active`
- `/api/research/studies`
- `/api/research/studies/{id}`
- `/api/research/studies/{id}/windows`
- `/api/research/studies/{id}/evaluate`
- `/api/research/studies/{id}/evaluations`
- `/api/research/studies/{id}/promote`
- `/api/research/candidates`

- [ ] Write route/status tests and explicit absence tests for `/api/research/optimize`, mutation and Live routes.
- [ ] Bootstrap `research-v1` at startup and mount router.
- [ ] Update runtime to `strategy_research=evidence_phase_8`; keep Paper/Live contracts unchanged.
- [ ] Commit.

### Task 7: Client and Settings observability

**Files:**
- Modify: `frontend/src/lib/api.js`
- Modify: `frontend/src/pages/SettingsPage.jsx`
- Modify: `frontend/src/pages/SettingsPage.test.jsx`
- Test/modify: `frontend/src/lib/api.test.js`

**Interfaces:**
- `researchAPI.status/activePolicy/studies/study/addWindow/evaluate/evaluations/promote/candidates`.

- [ ] Write frontend tests for Phase 8 runtime status and no optimizer/Live controls.
- [ ] Add client methods and Settings readout explaining promotion is manual evidence classification, not profitability proof.
- [ ] Commit.

### Task 8: Documentation and exact-HEAD audit

**Files:**
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `IMPLEMENTATION_PLAN.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/STRATEGIES.md`
- Modify: `docs/BACKTESTING.md`
- Modify: `docs/METRICS_AND_EVIDENCE.md`
- Modify: `docs/DATABASE_ARCHITECTURE.md`
- Modify: `GEMINI.md`
- Modify: `QWEN.md`

- [ ] Reconcile current Phase 8 contract, methodology and explicit exclusions.
- [ ] Search current HEAD for stale claims that Strategy Research is not implemented or that an optimizer exists.
- [ ] Compare exact Phase 7 close HEAD `e76cea10173e386219635c4c2b6220a50a1cbf24` to final HEAD; verify S1-S4 source untouched and no Live/auto-mutation scope creep.
- [ ] Query exact-HEAD status checks/workflow runs.
- [ ] Attempt `cd backend && pytest tests/ -v`, `cd frontend && npm test -- --run`, `npm run build` from a fresh checkout; report environmental blockers exactly.
- [ ] Mark only the source/contract/static gate complete unless fresh executable evidence exists.
- [ ] Commit final documentation status.
