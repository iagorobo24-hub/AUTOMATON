# Phase 4 Risk Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a persistent fail-closed Risk Engine that authorizes every operator Paper order before Paper Execution while keeping autonomous and Live execution disabled.

**Architecture:** Add `app.risk` as an independent domain consuming Market Data and Accounting state. Persist versioned `RiskProfile` and immutable `RiskDecision` evidence, then require a one-time matching ALLOW decision inside `PaperExecutionService`.

**Tech Stack:** FastAPI, SQLModel, SQLite, Decimal, pytest, React/Vite/Vitest.

**Spec:** `docs/superpowers/specs/2026-08-19-phase-4-risk-engine-design.md`

## Global Constraints

- Active persistence remains SQLModel + SQLite.
- Phase 4 remains long-only; no short, margin or leverage semantics.
- Market data used for Risk must be real and fail closed.
- Accounting remains the only financial authority.
- Risk never mutates cash/positions and never executes orders.
- Paper remains operator-only in Phase 4.
- Live execution remains disabled.
- `risk-v1` defaults: 250 USDT order cap, 25% equity/order, 60% total exposure, 35% symbol exposure, 4 open positions, 10% realized-loss limit, 15% drawdown limit, 30s quote age.
- SELL that reduces an existing long position is not blocked by exposure/order-size/loss/drawdown caps, but all integrity/recovery/data gates still apply.

---

### Task 1: Risk persistence and profile bootstrap

**Files:**
- Create: `backend/app/models/risk.py`
- Create: `backend/app/risk/__init__.py`
- Create: `backend/app/risk/bootstrap.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_risk_profile.py`

**Interfaces:**
- Produces `RiskProfile`, `RiskDecision`, `ensure_active_risk_profile(session) -> RiskProfile`.

- [ ] Write tests proving bootstrap is idempotent and persists exact `risk-v1` defaults.
- [ ] Run targeted test and observe RED because models/bootstrap do not exist.
- [ ] Implement SQLModel records and bootstrap.
- [ ] Run targeted test and observe PASS.
- [ ] Commit.

### Task 2: Deterministic Risk evaluation

**Files:**
- Create: `backend/app/risk/service.py`
- Test: `backend/tests/test_risk_service.py`

**Interfaces:**
- Produces `RiskService.evaluate(account_id, symbol, side, quantity, quote, marks=None) -> RiskDecision`.
- Consumes AccountingService snapshots/reconciliation and Phase 1 Quote.

- [ ] Write failing tests for ALLOW within limits and REJECT reason codes for inactive agent, stale/non-real quote, currency mismatch and paused profile.
- [ ] Add tests for max order notional/equity, total exposure, symbol concentration and max open positions.
- [ ] Add tests for insufficient cash reserve, realized-loss limit and drawdown limit.
- [ ] Add tests that accounting reconciliation/recovery ambiguity fail closed.
- [ ] Add SELL tests proving valid position reduction bypasses exposure/order-size/loss/drawdown caps but rejects oversell/integrity failures.
- [ ] Implement minimal deterministic evaluation and persisted decisions.
- [ ] Run targeted suite.
- [ ] Commit.

### Task 3: One-time Risk authorization in Paper Execution

**Files:**
- Modify: `backend/app/models/paper_execution.py` only if linkage belongs there; prefer `RiskDecision.paper_execution_id` to avoid schema churn in existing tables.
- Modify: `backend/app/paper_execution/service.py`
- Test: `backend/tests/test_paper_risk_gate.py`

**Interfaces:**
- `PaperExecutionService.execute_market_order(..., risk_decision: RiskDecision, request: PaperRequest | None = None)`.

- [ ] Write tests showing Paper rejects missing decision, REJECT decision, mismatched payload/profile and consumed decision.
- [ ] Write test showing matching ALLOW executes once and links/consumes decision.
- [ ] Implement validation before `AccountingService.create_order`.
- [ ] Consume/link the decision in the same transaction that persists `PaperExecution` linkage.
- [ ] Run targeted tests.
- [ ] Commit.

### Task 4: Mandatory Risk evaluation in Paper API and idempotency

**Files:**
- Modify: `backend/app/paper_execution/router.py`
- Test: `backend/tests/test_paper_risk_api.py`
- Modify existing Paper API/idempotency tests as required.

**Interfaces:**
- Paper route reserves `request_id`, fetches real Quote, evaluates Risk, executes only on ALLOW.

- [ ] Write test: Risk rejection returns 409, persists one RiskDecision, creates no Paper Order/Fill.
- [ ] Write test: approved command creates one decision + one execution/fill.
- [ ] Write test: completed idempotent replay creates no second decision or fill.
- [ ] Write test: provider failure creates neither financial state nor Risk decision.
- [ ] Implement route integration.
- [ ] Run targeted API tests.
- [ ] Commit.

### Task 5: Risk API and circuit breaker

**Files:**
- Create: `backend/app/risk/router.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_risk_api.py`
- Modify: `backend/tests/test_api_integration.py`

**Interfaces:**
- `GET /api/risk/status`
- `GET /api/risk/profiles/active`
- `GET /api/risk/decisions`
- `POST /api/risk/pause`
- `POST /api/risk/resume`

- [ ] Write route-registration/status/profile/list tests.
- [ ] Write pause/resume tests and prove paused Risk rejects new Paper orders.
- [ ] Implement router and mount it.
- [ ] Update `/health`/`/api/estado` to `risk=authoritative_phase_4` while `automated_trading=blocked_until_strategy_integration` and Live disabled.
- [ ] Run targeted backend API tests.
- [ ] Commit.

### Task 6: Frontend operational truth

**Files:**
- Modify: `frontend/src/lib/api.js`
- Modify: `frontend/src/pages/SettingsPage.jsx`
- Modify: `frontend/src/pages/SettingsPage.test.jsx`
- Optionally modify Ops Monitor only if a concise Risk status improves truthfulness.

**Interfaces:**
- Add read-only/control `riskAPI` status/profile/decisions/pause/resume client.

- [ ] Write/update Vitest expectations for Risk profile/version and automation still disabled.
- [ ] Implement minimal UI status; do not add autonomous/Live controls.
- [ ] Run frontend targeted tests when execution environment exists.
- [ ] Commit.

### Task 7: Documentation and final audit

**Files:**
- Rewrite: `docs/RISK_MANAGEMENT.md`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `IMPLEMENTATION_PLAN.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/DATABASE_ARCHITECTURE.md`
- Modify: `GEMINI.md`
- Modify: `QWEN.md`

- [ ] Reconcile current runtime vs target architecture.
- [ ] Mark Phase 4 source gate complete only after source review.
- [ ] Search for stale `blocked_until_risk`/`Risk not implemented` claims and correct only current files.
- [ ] Compare Phase 3 HEAD `ae03daa6a8b67d0977ad7af30e791c8103417785` to final HEAD and verify scope.
- [ ] Check exact final HEAD, combined status and workflow runs.
- [ ] Run full gate when possible:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

- [ ] Run real-provider virtual-capital smoke when an executable environment exists.
- [ ] Report source/contract completion separately from executable certification.
