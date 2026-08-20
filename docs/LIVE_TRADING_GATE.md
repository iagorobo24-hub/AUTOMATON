# Live Trading Gate

## Current status

Phase 10 implements **Live Readiness**, not Live trading.

Runtime contract:

- `live_readiness=readiness_phase_10`
- `live_adapter=disabled_adapter`
- `live_execution=disabled`
- `real_capital_execution=disabled`
- production adapter: `DisabledLiveAdapter`
- executable Live-order endpoint: absent
- credential-write/activation endpoint: absent

`ARCHITECTURE_READY` means only that the current technical/pre-operational controls satisfy `live-v1`. It never authorizes real money or changes either execution flag.

## Implemented Phase 10 prerequisites

### Architecture
- Paper and Live Readiness are separate domains; Paper cannot route into Live.
- `DisabledLiveAdapter` exposes only read/reconciliation capabilities and has no order-transmission method.
- No environment toggle activates a real adapter.
- Live persistence is separate and additive.

### Market data / venue constraints
- Readiness verifies Market Data is real, fail-closed and non-executing.
- Future intent identity canonicalizes the market symbol using the active Market Data contract before deriving its deterministic client id.
- Venue-rule contracts cover step size, tick size and minimum notional.
- Quantity normalization is downward-only so it cannot add exposure.
- `live-v1` caps absolute order/symbol/portfolio/deployable exposure and enforces its CANARY rollout fraction. With the current defaults, the $100 absolute deployable ceiling plus 10% CANARY fraction limits a prepared intent to $10 deployable capital context.

### Risk / circuit breakers
- Readiness requires active, unpaused Risk.
- Paper recovery ambiguity blocks readiness.
- Persistent Live emergency stop blocks new Live intents and its activate/clear transitions are audited.
- Reconciliation ambiguity produces `RECOVERY_REQUIRED` plus a circuit-breaker event.
- Uncertainty is never replayed, adopted or cleared automatically.

### Strategy evidence
- Readiness requires an exact `StrategyCandidate(status=PROMOTED)`.
- Its referenced `ResearchStudy` must be `PROMOTED`, its referenced `ResearchEvaluation` must be `PASS`, and study/evaluation/candidate strategy ID, version and source SHA must all match.
- Current active strategy source SHA must still equal the candidate SHA.
- Candidate promotion itself never activates Live.

### Operations
- Reconciliation snapshots are persistent.
- A positive readiness gate requires the latest reconciliation to be exactly `CLEAN` and no historical `RECOVERY_REQUIRED` record to remain unresolved.
- Phase 10 deliberately exposes no API or service shortcut that changes an ambiguous reconciliation to trusted state merely from an operator note.
- Emergency stop cannot clear while any Live reconciliation remains `RECOVERY_REQUIRED`.
- CANARY rollout and manual approval remain mandatory under `live-v1`.

## live-v1 readiness ceilings

- absolute deployable capital: $100
- CANARY rollout fraction: 10%
- effective current rollout-capital ceiling: $10
- order notional: $25
- symbol exposure: $50
- portfolio exposure: $100
- session loss: $5
- drawdown: 5%
- consecutive execution errors: 3
- stale market data: 30 seconds
- rollout stage: CANARY
- manual approval: required

These are conservative design ceilings. They are not funded or authorized capital.

## Active Phase 10 API

Allowed:

- `GET /api/live/status`
- `GET /api/live/policy`
- `GET /api/live/readiness`
- `POST /api/live/readiness/evaluate`
- `POST /api/live/emergency-stop`
- `POST /api/live/emergency-stop/clear`
- `GET /api/live/reconciliations`
- `POST /api/live/reconcile`

Absent by design:

- `/api/live/orders`
- `/api/live/buy`
- `/api/live/sell`
- `/api/live/activate`
- exchange-credential write routes
- manual reconciliation-resolution shortcut

## Remaining prerequisites before real capital can ever be considered

Phase 10 deliberately does **not** implement these:

1. choose and separately approve a target exchange/venue;
2. design and audit a concrete executable adapter for that venue;
3. define an external secret mechanism and least-privilege credential process;
4. ensure withdrawal permission is disabled;
5. test exchange-specific filters, error semantics, idempotency and reconciliation against a deliberately selected non-production environment where appropriate;
6. obtain fresh exact-HEAD backend/frontend certification;
7. obtain meaningful real historical + forward Paper evidence for the exact candidate;
8. run operational failure/recovery drills;
9. define an evidence-backed procedure for resolving future real venue ambiguity;
10. review hard limits and staged-rollout values for the actual venue/account;
11. make a **separate explicit product authorization** to permit real capital.

Even satisfying items 1–10 does not perform item 11 automatically.

## Explicit authorization boundary

No code, config value, Research promotion, readiness result, reconciliation or emergency-stop clear operation may change `live_execution` or `real_capital_execution` from `disabled` in Phase 10.

A future request to implement/enable real-capital execution is a new high-risk scope and must be reviewed separately.

## Prohibited shortcuts

- Do not reintroduce the deleted legacy TradingEngine/Binance implementation.
- Do not turn Paper into Live with a mode flag.
- Do not persist exchange secrets in SQLite.
- Do not expose secret values in API/UI/logs.
- Do not grant withdrawal permissions.
- Do not auto-liquidate on emergency stop without a separately designed procedure.
- Do not infer Live safety from a profitable backtest, Research PASS or short Paper run.
