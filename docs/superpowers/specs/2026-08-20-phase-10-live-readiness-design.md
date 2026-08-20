# Phase 10 — Live Readiness Design

## Objective

Prepare AUTOMATON for a future separately authorized real-capital execution mode without enabling real orders in Phase 10.

## Non-negotiable boundary

Phase 10 may create Live-specific contracts, persistence, readiness evaluation, venue rules, reconciliation records, emergency-stop state, staged-rollout policy, API/UI observability and a disabled adapter. It MUST NOT contain an adapter implementation capable of placing a real exchange order, store real exchange credentials, add an executable `/orders` route, or change Paper into Live through configuration.

Runtime after Phase 10:

- `live_execution=readiness_phase_10`
- `real_capital_execution=disabled`

## Architecture

Create `backend/app/live_execution/` as a domain independent of Paper Execution.

Components:

1. `policy.py` — bootstrap and retrieve versioned `live-v1` hard limits.
2. `adapter.py` — venue-neutral interfaces plus `DisabledLiveAdapter`; no real-order implementation.
3. `rules.py` — precision, tick-size, step-size, minimum-notional and hard-limit validation.
4. `readiness.py` — fail-closed readiness evaluation over Research, Risk, Paper recovery, Market Data, reconciliation, emergency-stop and rollout controls.
5. `service.py` — persist Live intents/order records in PREPARED/BLOCKED states only and deterministic client-order ids; it cannot transmit orders.
6. `reconciliation.py` — compare expected Live records with adapter snapshots; uncertainty becomes `RECOVERY_REQUIRED`.
7. `router.py` — status/policy/readiness/emergency-stop/reconciliation observability only.

## Persistence

Additive SQLModel tables:

- `live_policies`
- `live_readiness_evaluations`
- `live_order_intents`
- `live_order_records`
- `live_fill_records`
- `live_reconciliations`
- `live_circuit_breaker_events`
- `live_emergency_stop`

No existing table is altered.

## live-v1 policy

Initial conservative defaults:

- max deployable capital: 100 USD
- max order notional: 25 USD
- max symbol exposure: 50 USD
- max portfolio exposure: 100 USD
- max session loss: 5 USD
- max drawdown: 5%
- max consecutive execution errors: 3
- stale market-data limit: 30 seconds
- rollout stage: `CANARY`
- rollout capital fraction: 10%
- manual approval required: true

These are readiness ceilings, not permission to trade.

## Adapter contract

`LiveExchangeAdapter` exposes read/reconciliation capabilities and a capability descriptor:

- venue id
- trading enabled flag
- credential permission metadata
- symbol rules
- balances
- open orders
- order lookup by deterministic client id
- positions
- fills

`DisabledLiveAdapter` always reports `trading_enabled=False` and provides no method that can transmit a real order.

## Order intent and idempotency

A future Live order begins as a persisted `LiveOrderIntent` with deterministic client id derived from strategy candidate, symbol, side and intent nonce/source event.

Phase 10 service may validate and persist an intent as `PREPARED` or `BLOCKED`, but MUST NOT transmit it.

Duplicate deterministic client ids return the existing intent rather than create a second financial command.

## Readiness gate

A fresh `LiveReadinessEvaluation` returns READY only when all applicable gates pass:

- one exact promoted `StrategyCandidate` exists;
- current strategy source still matches candidate SHA;
- active Risk profile exists and is not paused;
- no PaperRequest/PaperExecution recovery ambiguity exists;
- Market Data contract reports real/fail-closed mode;
- emergency stop is not active;
- Live policy limits are valid and non-zero;
- rollout stage is CANARY with manual approval required;
- latest reconciliation is CLEAN;
- adapter is installed but trading remains disabled in Phase 10;
- credential metadata, if supplied in future, must indicate trade-only least privilege and withdrawals disabled.

Because real trading is intentionally disabled, Phase 10 distinguishes:

- `ARCHITECTURE_READY`: all technical/pre-operational gates except activation are satisfied.
- `REAL_CAPITAL_BLOCKED`: always true in Phase 10.

No readiness result automatically changes runtime mode.

## Precision and hard limits

Venue rules validate:

- normalized symbol exists;
- quantity conforms to step size;
- price conforms to tick size when relevant;
- notional meets venue minimum;
- order notional <= live-v1 max order notional;
- projected symbol exposure <= max symbol exposure;
- projected portfolio exposure <= max portfolio exposure;
- deployable capital <= max deployable capital.

Validation fails closed and returns reason codes.

## Reconciliation and restart

No uncertain Live state is replayed.

If a record cannot be reconciled uniquely against adapter snapshots, create `LiveReconciliation(status=RECOVERY_REQUIRED)` and activate a circuit-breaker event. Phase 10 never resubmits anything.

Startup may ensure policy/emergency-stop baseline and inspect persisted unresolved records, but it does not clear ambiguity automatically.

## Emergency stop

Persistent singleton state blocks all new Live intents when active.

API actions:

- activate with required reason;
- clear with required reason and only when no reconciliation is RECOVERY_REQUIRED.

Emergency stop does not automatically liquidate positions.

## API

Allowed:

- `GET /api/live/status`
- `GET /api/live/policy`
- `GET /api/live/readiness`
- `POST /api/live/readiness/evaluate`
- `POST /api/live/emergency-stop`
- `POST /api/live/emergency-stop/clear`
- `GET /api/live/reconciliations`

Forbidden in Phase 10:

- executable `POST /api/live/orders`
- exchange-key write endpoints
- activation endpoint for real capital

## UI

Settings may show Live Readiness, policy limits, architecture readiness, emergency-stop status and explicit `REAL CAPITAL DISABLED` state. No trade/activate button is added.

## Tests

Tests must cover:

- policy bootstrap idempotence;
- disabled adapter cannot trade;
- no executable order route;
- Paper cannot route into Live;
- venue precision/min-notional rules;
- hard capital/exposure limits;
- deterministic idempotent intent ids;
- emergency stop blocks intents;
- emergency stop clear fails with unresolved reconciliation;
- readiness fails without candidate/source match/Risk/recovery cleanliness;
- architecture readiness can be true while real-capital execution remains false;
- uncertain reconciliation becomes RECOVERY_REQUIRED and is never replayed;
- no hardcoded secret/key material;
- runtime reports Phase 10 readiness and separate real-capital disabled flag.

## Out of scope

- real exchange order transmission;
- actual Binance/Coinbase/Kraken trading adapter;
- storing API secrets;
- automatic liquidation;
- strategy changes;
- auto-deployment of Research candidates;
- automatic replication;
- increasing Paper autonomy.

## Closure

Phase 10 source/contract/static closes when the exact-HEAD audit confirms all readiness components exist, S1–S4 are unchanged, no real-order transport surface exists, `real_capital_execution=disabled`, docs are reconciled and executable verification is reported separately.