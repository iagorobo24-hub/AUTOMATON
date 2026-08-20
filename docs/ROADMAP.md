# AUTOMATON Roadmap

This roadmap defines dependency order. Source/static closure and executable certification are intentionally separate.

## Phases 0–4
Transition safety, Real Market Data, Accounting, deterministic Paper and Risk source contracts are implemented. Fresh exact-HEAD executable certification remains cross-phase debt.

## Phase 5 — Backtesting & Evidence
Immutable real historical snapshots, source SHA-256, next-candle deterministic execution and isolated evidence are implemented.

**Status:** source/contract/static gate satisfied; execution/performance evidence remains pending.

## Phase 6 — Agent Evolution
`evolution-v1` implements evidence-aware fitness, lineage/lifecycle and manual capital-conserving replication.

**Status:** source/contract/static gate satisfied; execution certification pending.

## Phase 7 — 24/7 Paper Operation
Persistent `runtime-v1` sessions execute unchanged S1-S4 through real Market Data -> Risk -> Paper -> Accounting with durable cycles, idempotency, recovery and source provenance.

**Status:** source/contract/static gate satisfied; sustained real-provider operational certification pending.

## Phase 8 — Strategy Research
`research-v1` uses chronological comparable TRAIN/VALIDATION/OOS plus fingerprinted stopped forward Paper evidence. Promotion is manual and never mutates or auto-deploys.

**Status:** source/contract/static gate satisfied; observed real research evidence pending.

## Phase 9 — Legacy Pruning
The superseded Mongo/mock/trading architecture, dead UI and dependencies were physically removed. Active `services/` contains only S1-S4 strategy code.

**Status:** source/contract/static gate satisfied; executable certification pending.

## Phase 10 — Live Readiness

Implementation currently present:

- separate additive `backend/app/live_execution/` domain;
- versioned conservative `live-v1` readiness policy;
- `DisabledLiveAdapter` with no order-transmission capability;
- venue step/tick/min-notional rules and downward-only quantity normalization;
- absolute order/symbol/portfolio/deployable ceilings plus enforced CANARY 10% rollout-capital fraction;
- canonical market identity before deterministic Live intent idempotency;
- PREPARED/BLOCKED future intent records only; no transmit path;
- full Research Study PROMOTED → Evaluation PASS → Candidate PROMOTED identity verification plus current source SHA;
- real/fail-closed Market Data, active Risk and Paper recovery gates;
- read-only reconciliation that treats unexplained orders/positions/fills, impossible transmitted records and trading-enabled adapters as `RECOVERY_REQUIRED`;
- persistent circuit-breaker and emergency-stop audit evidence;
- no automatic replay/adoption or manual text-only reconciliation-resolution shortcut;
- positive readiness requires latest reconciliation exactly CLEAN and no unresolved historical Live recovery;
- `/api/live` status/policy/readiness/emergency/reconciliation surfaces only;
- no order/buy/sell/credential-write/activation endpoint;
- Settings visibility for readiness separately from disabled execution;
- backend v2.13.0 runtime identifiers:
  - `live_readiness=readiness_phase_10`
  - `live_adapter=disabled_adapter`
  - `live_execution=disabled`
  - `real_capital_execution=disabled`;
- architecture guards against real-order transport, secret storage and Paper→Live routing.

Phase 10 intentionally does **not** include a concrete exchange trading adapter, real credentials, real fills or real-capital activation.

**Status:** implementation and documentation reconciliation are present. Final exact-HEAD static audit and executable certification gate remain before declaring source/contract/static closure.

## Future real-capital activation

This is not an automatic “Phase 11”. Any real-capital capability requires a separately scoped and explicitly authorized decision after venue selection, executable adapter review, external secret-management design, venue-specific integration/recovery tests, operational drills, an evidence-backed ambiguity-resolution procedure and candidate evidence review.

## Cross-phase certification debt

Fresh exact-HEAD backend tests, frontend tests/build and relevant real-provider smoke evidence remain required. Static closure must never be reported as a green runtime, profitable strategy or permission to move real money.
