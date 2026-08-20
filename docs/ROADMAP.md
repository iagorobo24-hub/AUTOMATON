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

Implemented in source:

- separate additive `backend/app/live_execution/` domain;
- versioned conservative `live-v1` readiness policy;
- `DisabledLiveAdapter` read/reconciliation contract with no order-transmission method;
- venue step-size/tick-size/min-notional validation;
- hard deployable-capital/order/symbol/portfolio ceilings;
- deterministic idempotent future Live intent ids;
- intent preparation that requires a promoted candidate, unchanged source SHA and prior `ARCHITECTURE_READY` evidence;
- persistent emergency stop;
- fail-closed read-only reconciliation and circuit-breaker events;
- explicit operator resolution for `RECOVERY_REQUIRED` records;
- readiness gates over candidate/source, real fail-closed Market Data, Risk, Paper recovery, Live recovery, rollout policy and adapter capabilities;
- `ARCHITECTURE_READY` separated from `real_capital_blocked=true`;
- `/api/live` status/policy/readiness/emergency-stop/reconciliation surfaces;
- no executable `/api/live/orders`, credential-write or real-capital activation endpoint;
- Settings visibility for readiness, limits and `REAL CAPITAL DISABLED`;
- runtime `v2.13.0` with `live_execution=readiness_phase_10` and `real_capital_execution=disabled`;
- architecture guards against real-order transport, secret storage and Paper→Live routing.

Phase 10 intentionally does **not** include a concrete exchange trading adapter, real credentials, real fills or real-capital activation.

**Status:** implementation present. Final exact-HEAD static audit/documentation reconciliation and executable certification gate are still required before declaring source/contract/static closure.

## Future real-capital activation

This is not an automatic “Phase 11”. Any real-capital capability requires a separately scoped and explicitly authorized decision after venue selection, executable adapter review, secret-management design, venue-specific integration tests, operational drills and candidate evidence review.

## Cross-phase certification debt

Fresh exact-HEAD backend tests, frontend tests/build and relevant real-provider smoke evidence remain required. Static closure must never be reported as a green runtime, profitable strategy or permission to move real money.
