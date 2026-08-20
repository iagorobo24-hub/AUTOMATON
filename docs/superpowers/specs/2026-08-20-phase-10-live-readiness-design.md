# Phase 10 — Live Readiness Design

## Objective

Prepare AUTOMATON for a future separately authorized real-capital execution mode without enabling real orders in Phase 10.

## Approved runtime boundary

Phase 10 reports:

- `live_execution=readiness_phase_10`
- `real_capital_execution=disabled`

`live_execution=readiness_phase_10` means the Live safety/readiness domain exists. It does **not** mean an executable exchange adapter exists. `real_capital_execution=disabled` is the explicit activation boundary.

## Non-negotiable constraints

Phase 10 MUST NOT:

- implement a production method capable of submitting a real exchange order;
- store or request real exchange API secrets;
- add `/api/live/orders`, `/api/live/buy`, `/api/live/sell` or an activation endpoint;
- allow a config/environment toggle to route Paper into Live;
- change S1–S4;
- auto-deploy a Research candidate;
- interpret readiness as capital authorization.

## Architecture

`backend/app/live_execution/` is independent of Paper Execution:

- `policy.py` — `live-v1` hard limits and bootstrap.
- `adapter.py` — read/reconciliation protocol + `DisabledLiveAdapter`.
- `rules.py` — venue precision/minimum and hard-limit validation.
- `service.py` — idempotent future-intent preparation, emergency stop and explicit recovery resolution.
- `reconciliation.py` — read-only fail-closed venue-state comparison.
- `readiness.py` — immutable readiness evaluation.
- `router.py` — readiness/operations API only.

## Additive persistence

- `live_policies`
- `live_readiness_evaluations`
- `live_order_intents`
- `live_order_records`
- `live_fill_records`
- `live_reconciliations`
- `live_circuit_breaker_events`
- `live_emergency_stop`

No existing Paper/Accounting table is repurposed.

## live-v1

Readiness ceilings:

- deployable capital: 100 USD
- order notional: 25 USD
- symbol exposure: 50 USD
- portfolio exposure: 100 USD
- session loss: 5 USD
- drawdown: 5%
- consecutive execution errors: 3
- stale market data: 30 seconds
- rollout stage: `CANARY`
- rollout fraction: 10%
- manual approval: required

These values are conservative design ceilings and never indicate funded or authorized capital.

## Adapter contract

`LiveExchangeAdapter` exposes only read/reconciliation capabilities:

- capability metadata;
- symbol rules;
- balances;
- open orders;
- lookup by deterministic client id;
- positions;
- fills.

`DisabledLiveAdapter` reports `trading_enabled=False`, no credentials, no withdrawal/trade permission and contains no real-order transmission method.

## Intent preparation

A future command can be represented as a persisted `LiveOrderIntent` with deterministic `live:<sha256>` client id based on candidate, symbol, side and source event.

Preparation requires:

- exact promoted StrategyCandidate;
- current source SHA still matching candidate;
- prior `ARCHITECTURE_READY` evaluation for the candidate;
- Phase 10 invariant `real_capital_blocked=true`;
- emergency stop clear;
- venue rules and hard limits satisfied.

Duplicate client ids return the existing intent. Phase 10 may persist `PREPARED` or `BLOCKED`; it cannot transmit either.

## Venue/hard-limit rules

Validate fail-closed:

- symbol rules present;
- positive quantity/price;
- quantity step size;
- limit-price tick size where applicable;
- minimum notional;
- maximum order notional;
- projected symbol exposure;
- projected portfolio exposure;
- deployable capital ceiling.

## Readiness gate

Every evaluation is fresh and immutable. It checks:

- promoted candidate;
- current candidate source SHA;
- Market Data `evidence_mode=real`, `synthetic_fallback=false`, `execution_capability=false`;
- active unpaused Risk;
- no PaperRequest/PaperExecution recovery ambiguity;
- no unresolved Live reconciliation;
- emergency stop clear;
- valid `live-v1` limits;
- CANARY rollout + manual approval;
- latest Live reconciliation clean/resolved;
- adapter remains non-trading;
- withdrawal capability disabled.

Outputs:

- `ARCHITECTURE_READY` or `BLOCKED`;
- `real_capital_blocked=true` always in Phase 10.

No evaluation changes runtime or candidate state.

## Reconciliation/restart

Reconciliation is read-only. Unexpected venue state or a trading-enabled adapter during Phase 10 creates:

- `LiveReconciliation(status=RECOVERY_REQUIRED)`;
- `LiveCircuitBreakerEvent`.

No order is replayed.

A historical `RECOVERY_REQUIRED` remains blocking even if a later snapshot is CLEAN. The operator must explicitly resolve that exact record with a reason. Only after all unresolved records are resolved can emergency stop be cleared.

Startup bootstraps `live-v1` and emergency-stop state, then runs read-only reconciliation through `DisabledLiveAdapter`. Startup never submits an order or loads secrets.

## Emergency stop

Persistent singleton state blocks new Live intents. Activate/clear require reasons. Clear fails while any reconciliation is `RECOVERY_REQUIRED`. Emergency stop never auto-liquidates.

## API

Allowed:

- `GET /api/live/status`
- `GET /api/live/policy`
- `GET /api/live/readiness`
- `POST /api/live/readiness/evaluate`
- `POST /api/live/emergency-stop`
- `POST /api/live/emergency-stop/clear`
- `GET /api/live/reconciliations`
- `POST /api/live/reconciliations/{id}/resolve`

Forbidden:

- executable order submission;
- credential write/storage;
- real-capital activation;
- generic Paper→Live mode switching.

## UI

Settings displays readiness mode, policy, architecture-ready state, emergency stop and explicit `REAL CAPITAL DISABLED`. No Live trade/activate button is added.

## Security/architecture tests

Guards must prove:

- disabled adapter has no `create_order`, `place_order` or `submit_order` method;
- no executable Live order route;
- Paper domains do not import Live execution;
- no hardcoded/persisted exchange secrets;
- Market Data remains read-only/fail-closed;
- emergency stop and recovery gates fail closed;
- deterministic intent idempotency;
- `real_capital_execution=disabled`;
- `services/strategies.py` remains unchanged from Phase 9.

## Explicit future authorization

Completing Phase 10 is not authorization to move real money. A future executable adapter and any real-capital activation require a separately scoped, explicitly authorized project decision after venue selection, secret-management design, exchange-specific integration testing, operational recovery drills and evidence review.

## Closure

Phase 10 source/contract/static may close only after exact-HEAD audit confirms source, tests, UI and docs match this contract; Git/CI state is checked; S1–S4 are unchanged; and executable test/build status is reported separately rather than inferred.