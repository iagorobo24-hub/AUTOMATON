# Phase 10 — Live Readiness Design

## Objective

Prepare AUTOMATON for a future separately authorized real-capital execution mode without enabling real orders in Phase 10.

## Non-negotiable boundary

Phase 10 may create Live-specific contracts, persistence, readiness evaluation, venue rules, reconciliation records, emergency-stop state, staged-rollout policy, API/UI observability and a disabled adapter. It MUST NOT contain an adapter implementation capable of placing a real exchange order, store real exchange credentials, add an executable `/orders` route, or change Paper into Live through configuration.

Runtime after Phase 10:

- `live_readiness=readiness_phase_10`
- `live_adapter=disabled_adapter`
- `live_execution=disabled`
- `real_capital_execution=disabled`

`live_readiness` communicates that the safety/evidence boundary exists. It must never be used as a synonym for execution capability.

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

`DisabledLiveAdapter` always reports `trading_enabled=False` and provides no production path that can transmit a real order. Any submission-shaped interface used to keep the future adapter contract complete must fail closed unconditionally in this adapter.

No environment variable or ordinary settings change may replace the disabled adapter with an executable one in Phase 10.

## Order intent and idempotency

A future Live order begins as a persisted `LiveOrderIntent` with deterministic client id derived from strategy candidate, symbol, side and intent nonce/source event.

Phase 10 service may validate and persist an intent as `PREPARED` or `BLOCKED`, but MUST NOT transmit it.

Duplicate deterministic client ids return the existing intent rather than create a second financial command.

## Readiness gate

A fresh `LiveReadinessEvaluation` evaluates all applicable gates:

- one exact promoted `StrategyCandidate` exists;
- current strategy source still matches candidate SHA;
- active Risk profile exists and is not paused;
- no PaperRequest/PaperExecution recovery ambiguity exists;
- Market Data contract reports real/fail-closed mode;
- emergency stop state is known and observable;
- Live policy limits are valid and non-zero;
- rollout stage is CANARY with manual approval required;
- latest reconciliation is CLEAN;
- credential metadata, if supplied in future, must indicate trade-only least privilege and withdrawals disabled;
- adapter capability is explicit.

Phase 10 distinguishes two decisions:

- `ARCHITECTURE_READY`: technical/pre-operational readiness gates other than actual execution activation are satisfied.
- `REAL_CAPITAL_BLOCKED`: always true in Phase 10 because the only production adapter is disabled and no activation authorization exists.

`ARCHITECTURE_READY` must never automatically change runtime mode or enable an adapter.

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

Normalization must not round quantity upward into additional exposure. Validation fails closed and returns reason codes.

## Reconciliation and restart

No uncertain Live state is replayed.

If a record cannot be reconciled uniquely against adapter snapshots, create `LiveReconciliation(status=RECOVERY_REQUIRED)` and activate a circuit-breaker event. Phase 10 never resubmits anything.

Startup may ensure policy/emergency-stop baseline and inspect persisted unresolved records, but it does not clear ambiguity automatically and never performs order submission.

## Emergency stop

Persistent singleton state blocks all new Live intents when active.

API actions:

- activate with required reason;
- clear with required reason and only when no reconciliation is `RECOVERY_REQUIRED`.

Emergency stop survives restart. Clearing it does not imply `ARCHITECTURE_READY` and does not enable execution.

Emergency stop does not automatically liquidate positions or cancel orders; those are separate future operational procedures requiring their own explicit design.

## API

Allowed:

- `GET /api/live/status`
- `GET /api/live/policy`
- `GET /api/live/readiness`
- `POST /api/live/readiness/evaluate`
- `POST /api/live/emergency-stop`
- `POST /api/live/emergency-stop/clear`
- `GET /api/live/reconciliations`
- `POST /api/live/reconcile`

Forbidden in Phase 10:

- executable `POST /api/live/orders`
- `/api/live/buy` or `/api/live/sell`
- exchange-key write endpoints
- activation endpoint for real capital
- generic mode switch that routes Paper commands to Live

## Secret and credential contract

Phase 10 does not store or request real exchange secrets.

Future credential handling must satisfy all of the following:

- secret values supplied through a reviewed external secret mechanism;
- no API key/secret persisted in SQLite;
- no secret values exposed in API/UI/logs;
- trading permission explicit;
- withdrawal permission prohibited wherever independently configurable;
- credential presence never enables execution;
- future executable adapter installation requires a separate code/product authorization gate.

Only non-secret permission declarations/metadata may be stored for readiness evidence.

## UI

Settings and/or Ops Monitor may show Live Readiness, policy limits, architecture readiness, emergency-stop status, latest reconciliation and explicit `REAL CAPITAL DISABLED` state. No trade/activate button is added.

## Tests

Tests must cover:

- policy bootstrap idempotence;
- disabled adapter cannot trade;
- no executable order route;
- Paper cannot route into Live;
- venue precision/min-notional rules;
- quantity normalization never increases requested exposure;
- hard capital/exposure limits;
- deterministic idempotent intent ids;
- emergency stop blocks intents and survives persistence;
- emergency stop clear fails with unresolved reconciliation;
- readiness fails without candidate/source match/Risk/recovery cleanliness;
- architecture readiness can be true while real-capital execution remains false;
- uncertain reconciliation becomes `RECOVERY_REQUIRED` and is never replayed;
- no hardcoded secret/key material;
- no Live secret fields persisted in SQLModel tables;
- runtime reports Phase 10 readiness separately from `live_execution=disabled` and `real_capital_execution=disabled`.

## Static safety guard

Add an architecture regression that fails if:

- deleted legacy exchange/trading modules reappear;
- `python-binance` or another real trading SDK is added without later explicit authorization;
- a production real-order endpoint appears;
- Paper imports `live_execution` or selects it through configuration;
- `live_execution` or `real_capital_execution` stops being `disabled`;
- secret-looking exchange credential fields are persisted;
- `services/strategies.py` changes during Phase 10.

## Out of scope

- real exchange order transmission;
- actual Binance/Coinbase/Kraken trading adapter;
- storing API secrets;
- automatic liquidation;
- strategy changes;
- auto-deployment of Research candidates;
- automatic replication;
- increasing Paper autonomy.

## Documentation

Update at minimum:

- `README.md`
- `ARCHITECTURE.md`
- `IMPLEMENTATION_PLAN.md`
- `docs/ROADMAP.md`
- `docs/LIVE_TRADING_GATE.md`
- `docs/DATABASE_ARCHITECTURE.md`
- `GEMINI.md`
- `QWEN.md`

Documentation must distinguish Phase 10 source/static readiness, executable certification, any future venue integration evidence and the separately authorized decision to move real capital.

## Git and scope rules

Implementation is authorized directly on `main` under the established repository strategy.

Allowed:

- additive Phase 10 domain/models/tests/API/UI/docs;
- small existing-domain changes required only to read evidence or expose readiness;
- runtime/version-status updates.

Not allowed:

- real trading credentials;
- real order submission implementation;
- deployment;
- Live activation;
- PR creation/merge as part of this phase;
- S1–S4 changes;
- unrelated refactors.

## Closure

Phase 10 source/contract/static closes only when exact-HEAD audit confirms:

1. separate Live Readiness domain exists;
2. only disabled/non-executable adapter exists in production;
3. `live_readiness=readiness_phase_10` is distinct from execution;
4. `live_execution=disabled`;
5. `real_capital_execution=disabled`;
6. no production order-submission endpoint exists;
7. readiness policy/evaluation persistence exists;
8. venue precision/minimum/hard-limit validation exists;
9. deterministic idempotency exists;
10. reconciliation/restart fail closed;
11. persistent emergency stop exists;
12. Research/Risk/recovery gates are enforced;
13. secrets are not persisted/exposed;
14. API/UI communicate readiness vs execution clearly;
15. static guards cover routing/secrets/legacy reintroduction;
16. S1–S4 are unchanged from Phase 9;
17. docs match source;
18. exact Git compare from Phase 9 close is coherent;
19. CI/status is checked;
20. executable validation is reported truthfully.

## Execution certification

The normal gate remains:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

If checkout/execution is blocked by the environment, source/static closure may still be audited but execution certification remains pending.

A future executable Live adapter requires its own dedicated integration testing against a deliberately selected venue environment and separate explicit authorization. Phase 10 does not satisfy that future gate.

## Final safety statement

Completing Phase 10 means AUTOMATON has a designed and audited boundary for deciding whether future Live execution could be enabled safely enough to evaluate further. It does **not** mean the system is authorized to move real money, and the Phase 10 production implementation is intentionally incapable of doing so.
