# AUTOMATON Architecture

## Objective

AUTOMATON researches autonomous crypto-trading agents using **real market data and virtual capital** until explicit evidence/safety gates justify any future Live activation.

## Non-negotiable boundaries

1. Production/Paper evidence never uses generated or mock market data.
2. Backtest and Paper use real market data and virtual capital.
3. Live is a separate execution boundary; Phase 10 prepares it but does not activate real capital.
4. Evidence preserves mode/provenance.
5. SQLModel/SQLite is the active persistence baseline.
6. Accounting is the only active Paper financial authority.
7. Every normal Paper execution requires persisted current-profile Risk ALLOW.
8. Backtest state is isolated from Paper and uses next-candle execution.
9. Replication transfers rather than duplicates funded liquid capital.
10. Autonomous trading exists only inside explicitly started Phase 7 Paper sessions.
11. Restart never silently resumes uncertain financial activity.
12. Research classifies evidence; it does not mutate, optimize, auto-deploy or enable Live.
13. Phase 9 removed the superseded Mongo/mock/trading runtime.
14. Phase 10 `ARCHITECTURE_READY` never implies `real_capital_execution=enabled`.

## Active domains

### Market Data — Phase 1
`backend/app/market_data/` owns real Quote/Candle contracts, provenance and fail-closed quality controls.

### Strategy — S1-S4
`backend/app/services/strategies.py` is the only executable strategy service. Phase 10 does not modify it.

### Risk — Phase 4
`backend/app/risk/` remains mandatory authorization for Paper. Future Live execution must also be independently gated by Live hard limits rather than strategy code.

### Paper Execution / Runtime — Phases 3, 4 and 7
Paper remains virtual-capital execution through `operator` or `strategy_runtime`, always behind Risk. Paper does not import or select a Live adapter.

### Accounting — Phase 2
Accounting owns active Paper money, fills, positions and ledger state. Live Readiness records do not masquerade as Paper Accounting.

### Backtesting / Evolution / Research — Phases 5–8
Backtesting owns historical evidence; Evolution owns fitness/lineage/manual replication; Research owns methodology/evaluation/manual candidate classification. None authorizes Live automatically.

### Legacy boundary — Phase 9
Mongo, mock engines, duplicate trading engines, legacy credentialed Binance code and dead UI were physically pruned. They are not fallback Live implementations.

### Live Readiness — Phase 10

`backend/app/live_execution/` is a separate, fail-closed readiness domain.

```text
StrategyCandidate + current source SHA
          + Risk + Paper recovery
          + live-v1 hard limits
          + emergency-stop state
          + read-only reconciliation
                    ↓
        LiveReadinessEvaluation
                    ↓
 ARCHITECTURE_READY or BLOCKED
                    ↓
   real_capital_execution=disabled
```

Persistent records:

- `LivePolicy`
- `LiveReadinessEvaluation`
- `LiveOrderIntent`
- `LiveOrderRecord`
- `LiveFillRecord`
- `LiveReconciliation`
- `LiveCircuitBreakerEvent`
- `LiveEmergencyStop`

`live-v1` defines conservative readiness ceilings: $100 deployable capital, $25 order notional, $50 symbol exposure, $100 portfolio exposure, $5 session loss, 5% drawdown, three consecutive execution errors, 30-second stale-data threshold and CANARY rollout at 10% with manual approval required. These values are gates, not capital authorization.

#### Adapter boundary

`LiveExchangeAdapter` is a read/reconciliation protocol only. `DisabledLiveAdapter` reports `trading_enabled=False`, has no credentials and exposes no `create_order`, `place_order` or `submit_order` capability.

There is no real venue implementation in Phase 10.

#### Intent preparation

A future command can be represented as `LiveOrderIntent` with deterministic `live:<sha256>` client id. Phase 10 can only classify it as `PREPARED` or `BLOCKED`; it cannot transmit it. Venue precision/min-notional plus `live-v1` capital/exposure limits fail closed.

#### Reconciliation

Read-only reconciliation compares persisted preparation state with adapter observations. Any unexpected venue-side order or forbidden trading-enabled adapter state becomes `RECOVERY_REQUIRED` and emits a circuit-breaker event. Uncertainty is never replayed.

A `RECOVERY_REQUIRED` record remains blocking until the operator explicitly resolves that exact reconciliation with a reason. A later clean snapshot does not erase old ambiguity automatically.

#### Emergency stop

The singleton emergency stop blocks new Live intents. Clearing requires an operator reason and zero unresolved Live reconciliations. Emergency stop does not auto-liquidate positions.

#### Readiness

Every readiness attempt writes a fresh immutable evaluation. Required gates include:

- exact promoted Research candidate;
- current strategy-source SHA unchanged;
- active unpaused Risk;
- no unresolved Paper request/execution recovery;
- valid `live-v1` limits and CANARY/manual approval policy;
- emergency stop clear;
- no unresolved Live reconciliation and a clean/resolved latest snapshot;
- adapter still non-trading and withdrawals disabled.

`architecture_ready=true` is compatible only with `real_capital_blocked=true` during Phase 10.

## Active API/UI boundary

Live Readiness mounts:

- `GET /api/live/status`
- `GET /api/live/policy`
- `GET /api/live/readiness`
- `POST /api/live/readiness/evaluate`
- `POST /api/live/emergency-stop`
- `POST /api/live/emergency-stop/clear`
- `GET /api/live/reconciliations`
- `POST /api/live/reconciliations/{id}/resolve`

There is no `/api/live/orders`, credential-write or activation endpoint. Settings displays readiness and hard limits but contains no Live trade/activation control.

## Current runtime

- `market_data=real_contract_available`
- `accounting=authoritative_phase_2`
- `risk=authoritative_phase_4`
- `paper_trading=autonomous_phase_7`
- `backtesting=evidence_phase_5`
- `agent_evolution=evidence_phase_6`
- `paper_runtime=runtime_phase_7`
- `strategy_research=evidence_phase_8`
- `legacy_pruning=pruned_phase_9`
- `live_execution=readiness_phase_10`
- `real_capital_execution=disabled`
- `automated_trading=paper_enabled_phase_7`

## Verification

Static guards must prove no real-order transport, credential storage/write route, Paper→Live routing or S1-S4 change was introduced. Runtime correctness still requires fresh exact-HEAD backend/frontend execution. Phase 10 completion does not authorize real money.