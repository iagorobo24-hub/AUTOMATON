# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable autonomous Paper Trading research platform: **real market data, virtual capital, deterministic accounting/execution, explicit risk, reproducible historical/forward evidence and disciplined strategy promotion**, with a separately gated future Live boundary.

## Current baseline

- FastAPI + SQLModel + SQLite and React/Vite are active.
- Phases 1–10 source/contract/static gates are present.
- Phase 7 provides explicit persistent autonomous Paper sessions; no session starts/resumes merely because the process boots.
- Phase 8 Research classifies evidence and does not mutate or auto-deploy.
- Phase 9 physically removed Mongo/mock/legacy trading architecture.
- Phase 10 adds a Live Readiness boundary while keeping Live execution and real capital disabled.
- Fresh exact-HEAD execution evidence remains cross-phase debt.

## Ordered implementation program

### 0–5 — Foundation and evidence
Market Data, Accounting, Paper Execution, Risk and Backtesting/Evidence source/static gates are complete. Fresh execution certification and observed S1-S4 performance remain separate evidence.

### 6. Agent Evolution
- [x] Versioned fitness, lineage/lifecycle and capital-conserving manual replication.
- [x] Current-source and Paper evidence gates.
- [x] Source/static audit.
- [ ] Execute exact-HEAD backend/frontend/build gate.

**Phase 6 source/contract/static gate:** complete.

### 7. 24/7 Paper Operation
- [x] Persistent runtime sessions/cycles, Risk→Paper→Accounting, idempotency and recovery.
- [x] Strategy source provenance and no auto-resume.
- [x] Source/static audit.
- [ ] Execute exact-HEAD gate and sustained real-provider runtime smoke.

**Phase 7 source/contract/static gate:** complete.

### 8. Strategy Research
- [x] TRAIN/VALIDATION/OOS methodology and comparable Backtest evidence.
- [x] Fingerprinted forward Paper evidence and manual candidate promotion.
- [x] No optimizer/mutation/auto-deployment/Live.
- [x] Source/static audit.
- [ ] Execute exact-HEAD gate plus observed historical/forward research smoke.

**Phase 8 source/contract/static gate:** complete.

### 9. Legacy Pruning
- [x] Remove Mongo, legacy engines/routes/mock fallbacks/dead UI and dependencies after reference audits.
- [x] Preserve S1-S4 and active evidence/recovery domains.
- [x] Add anti-regression guards and reconcile docs.
- [x] Exact-HEAD source/static audit.
- [ ] Execute exact-HEAD backend/frontend/build gate.

**Phase 9 source/contract/static gate:** complete.

### 10. Live Readiness
See `docs/LIVE_TRADING_GATE.md`, `docs/superpowers/specs/2026-08-20-phase-10-live-readiness-design.md` and `docs/superpowers/plans/2026-08-20-phase-10-live-readiness.md`.

- [x] Add separate additive Live Readiness domain and persistence.
- [x] Bootstrap conservative versioned `live-v1` policy and persistent emergency-stop singleton.
- [x] Add `DisabledLiveAdapter` with read/reconciliation capabilities only and no real-order transport.
- [x] Add venue step/tick/min-notional validation and downward-only quantity normalization.
- [x] Enforce absolute capital/exposure ceilings plus current CANARY 10% rollout-capital fraction.
- [x] Canonicalize market identity before deterministic idempotency keys.
- [x] Persist PREPARED/BLOCKED future Live intents only; no transmission path.
- [x] Require full promoted Research Study → PASS Evaluation → PROMOTED Candidate identity chain plus current source SHA.
- [x] Require real/fail-closed/non-executing Market Data, active Risk and clean Paper recovery.
- [x] Fail closed on unexplained venue orders/positions/fills, lookup matches, impossible transmitted records or trading-enabled adapter.
- [x] Persist `RECOVERY_REQUIRED` and circuit-breaker evidence without replay/adoption.
- [x] Require latest reconciliation exactly CLEAN and no unresolved historical Live recovery for positive readiness.
- [x] Add persistent audited emergency-stop activation/clear; clear cannot cross unresolved recovery.
- [x] Keep manual reconciliation-resolution shortcut absent in Phase 10.
- [x] Mount Live status/policy/readiness/evaluate/emergency/reconciliation surfaces only.
- [x] Keep order/buy/sell/credential/activation routes absent.
- [x] Expose `live_readiness=readiness_phase_10`, `live_adapter=disabled_adapter`, `live_execution=disabled`, `real_capital_execution=disabled` in backend v2.13.0.
- [x] Update Settings to display readiness separately from disabled execution and real capital.
- [x] Add static architecture guards for routing, secrets, Paper→Live isolation and execution flags.
- [x] Reconcile core documentation with the strengthened Phase 10 contract.
- [x] Complete exact-HEAD static audit from Phase 9 close: 89 commits ahead, 0 behind at the audited pre-closure HEAD; S1-S4 blob unchanged.
- [ ] Execute exact-HEAD backend/frontend/build gate. Last fresh attempt stopped at clone with DNS `Could not resolve host: github.com` (exit 128), before tests could run.

**Phase 10 source/contract/static gate:** complete. `ARCHITECTURE_READY` remains a readiness classification only. `live_execution=disabled` and `real_capital_execution=disabled` remain mandatory.

## Future real-capital activation

This is not automatically the next numbered phase. A concrete venue adapter, external secret-management design, exchange-specific integration/recovery testing, operational drills, evidence-backed ambiguity-resolution procedure and an explicit product authorization are all separately required before real capital could be considered.

## Validation gate

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Static review is not fresh execution evidence. `ARCHITECTURE_READY` is not venue certification, profitability evidence or permission to move money.
