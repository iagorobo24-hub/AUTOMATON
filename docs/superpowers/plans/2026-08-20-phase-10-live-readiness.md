# Phase 10 Live Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a separate fail-closed Live Readiness domain that can prove architectural readiness for a future real-capital adapter while keeping real-capital execution disabled.

**Architecture:** Additive SQLModel persistence plus a `live_execution` domain. A disabled venue adapter supplies read/capability contracts only. Readiness, intent validation, hard limits, emergency stop and reconciliation are persistently auditable, but no code path can transmit a real order.

**Tech Stack:** Python 3.11, FastAPI, SQLModel/SQLite, pytest, React/Vite/Vitest.

**Spec:** `docs/superpowers/specs/2026-08-20-phase-10-live-readiness-design.md`

## Global Constraints

- `live_readiness=readiness_phase_10` communicates readiness only.
- `live_adapter=disabled_adapter`, `live_execution=disabled` and `real_capital_execution=disabled` throughout Phase 10.
- No real exchange order transmission method or executable `/api/live/orders` route.
- No exchange credential storage/write API.
- Paper and Live adapters remain structurally separate.
- S1-S4 are not modified.
- All financial ambiguity fails closed and is not replayed.

---

### Task 1: Persistence and live-v1 policy

**Files:**
- Create: `backend/app/models/live_execution.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/app/live_execution/__init__.py`
- Create: `backend/app/live_execution/policy.py`
- Test: `backend/tests/test_live_policy.py`

**Produces:** additive LivePolicy, LiveReadinessEvaluation, LiveOrderIntent, LiveOrderRecord, LiveFillRecord, LiveReconciliation, LiveCircuitBreakerEvent and LiveEmergencyStop records; `bootstrap_live_policy(session)` and `ensure_emergency_stop_baseline(session)`.

- [ ] Write tests asserting `live-v1` bootstrap is idempotent and conservative defaults equal the spec.
- [ ] Implement models and bootstrap helpers.
- [ ] Verify policy remains informational/readiness only and carries no enable flag for real trading.

### Task 2: Disabled adapter and venue rules

**Files:**
- Create: `backend/app/live_execution/adapter.py`
- Create: `backend/app/live_execution/rules.py`
- Test: `backend/tests/test_live_adapter_rules.py`

**Produces:** `LiveExchangeAdapter` read-only protocol, `DisabledLiveAdapter`, `SymbolRules`, `validate_live_intent_rules(...)`.

- [ ] Write tests proving adapter has no order-transmission capability and always reports `trading_enabled=False`.
- [ ] Test step size, tick size, min notional and policy exposure/capital ceilings.
- [ ] Implement fail-closed validation with machine-readable reason codes and downward-only quantity normalization.

### Task 3: Persistent emergency stop and intent preparation

**Files:**
- Create: `backend/app/live_execution/service.py`
- Test: `backend/tests/test_live_intents.py`

**Produces:** deterministic `client_order_id`, idempotent `prepare_intent(...)`, `activate_emergency_stop(...)`, `clear_emergency_stop(...)`.

- [ ] Test duplicate source event returns existing intent.
- [ ] Test emergency stop blocks preparation.
- [ ] Test prepared intent is `PREPARED` only and cannot be transmitted.
- [ ] Test clear is rejected when unresolved Live reconciliation exists.

### Task 4: Reconciliation and circuit breakers

**Files:**
- Create: `backend/app/live_execution/reconciliation.py`
- Test: `backend/tests/test_live_reconciliation.py`

**Produces:** `reconcile_live_state(session, adapter)` and persisted CLEAN/RECOVERY_REQUIRED snapshots.

- [ ] Test exact snapshot agreement yields CLEAN.
- [ ] Test unknown/mismatched intent/order state yields RECOVERY_REQUIRED.
- [ ] Test ambiguity creates a circuit-breaker event and never changes an intent into resendable state.

### Task 5: Readiness evaluator

**Files:**
- Create: `backend/app/live_execution/readiness.py`
- Test: `backend/tests/test_live_readiness.py`

**Consumes:** StrategyCandidate/source fingerprint, Risk profile, Paper recovery, Market Data mode, Live policy, emergency stop and reconciliation.

**Produces:** fresh immutable `LiveReadinessEvaluation` with `architecture_ready`, `real_capital_blocked=True` and reason codes.

- [ ] Test missing candidate/source drift/Risk pause/Paper recovery/emergency stop/non-clean reconciliation all fail closed.
- [ ] Test credential permission metadata with withdrawal permission fails closed without storing secret values.
- [ ] Test all technical gates can yield `ARCHITECTURE_READY` while `real_capital_blocked` remains true.
- [ ] Test no evaluation mutates runtime or candidate state.

### Task 6: Readiness API and runtime integration

**Files:**
- Create: `backend/app/live_execution/router.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_live_readiness_api.py`
- Modify: `backend/tests/test_api_integration.py`

**Produces:** status/policy/readiness/evaluate/emergency-stop/reconciliations/reconcile routes only.

- [ ] Test `/api/live/orders`, `/api/live/buy`, `/api/live/sell`, credential-write and activation routes are absent.
- [ ] Mount `/api/live` and bootstrap Live policy/emergency baseline on startup without submission/replay.
- [ ] Bump backend to `2.13.0`.
- [ ] Report `live_readiness=readiness_phase_10`, `live_adapter=disabled_adapter`, `live_execution=disabled`, `real_capital_execution=disabled`.

### Task 7: UI observability

**Files:**
- Modify: `frontend/src/lib/api.js`
- Modify: `frontend/src/pages/SettingsPage.jsx`
- Modify: `frontend/src/pages/SettingsPage.test.jsx`

**Produces:** Live Readiness card with architecture state, hard limits, emergency-stop status and explicit real-capital disabled label.

- [ ] Add read/evaluate/emergency-stop/reconcile clients only; no submit-order, credential or activation methods.
- [ ] Add UI tests asserting no activate/trade button and explicit real-capital disabled copy.

### Task 8: Architecture anti-regression guards

**Files:**
- Create: `backend/tests/test_live_readiness_architecture.py`

- [ ] Assert no real-order exchange client or production submission endpoint exists under active Phase 10 source.
- [ ] Assert no hardcoded credential fields/values or secret write route exists.
- [ ] Assert Paper domain does not import `live_execution` for routing.
- [ ] Assert runtime keeps `live_execution=disabled` and `real_capital_execution=disabled`.
- [ ] Assert `services/strategies.py` remains unchanged from Phase 9.

### Task 9: Documentation

**Files:**
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `IMPLEMENTATION_PLAN.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/LIVE_TRADING_GATE.md`
- Modify: `docs/DATABASE_ARCHITECTURE.md`
- Modify: `GEMINI.md`
- Modify: `QWEN.md`

- [ ] Reconcile Phase 10 as Live Readiness, not Live activation.
- [ ] Record remaining activation prerequisites and explicit authorization boundary.
- [ ] Keep source/static closure pending until exact-HEAD audit.

### Task 10: Exact-HEAD closure

- [ ] Fetch final main HEAD and compare from Phase 9 close `808e34a6815ca4d82c3866f86bceec7acaf15047`.
- [ ] Confirm `backend/app/services/strategies.py` unchanged from Phase 9.
- [ ] Search for real-order transmission, trading SDKs, secret storage/write routes, activation surfaces and Paper→Live routing.
- [ ] Inspect adapter/readiness/reconciliation for fail-open contradictions.
- [ ] Check GitHub CI/status for exact HEAD.
- [ ] Attempt backend pytest, frontend tests and build from fresh checkout; report environmental blocking exactly.
- [ ] Mark Phase 10 source/contract/static gate complete only when exact-HEAD static evidence is coherent; keep execution/venue/real-capital certification separate.
