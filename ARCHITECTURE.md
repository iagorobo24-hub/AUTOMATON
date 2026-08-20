# AUTOMATON Architecture

## Objective

AUTOMATON researches autonomous crypto-trading agents using **real market data and virtual capital** until explicit evidence/safety gates justify any future Live activation.

## Non-negotiable boundaries

1. Production/Paper evidence never uses generated or mock market data.
2. Backtest and Paper use real market data and virtual capital.
3. Live is a separate execution boundary; Phase 10 prepares readiness but does not enable execution.
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
14. `ARCHITECTURE_READY` never changes `live_execution=disabled` or `real_capital_execution=disabled`.

## Active domains

### Market Data — Phase 1
`backend/app/market_data/` owns real Quote/Candle contracts, symbol normalization, provenance and fail-closed quality controls.

### Strategy — S1-S4
`backend/app/services/strategies.py` is the only executable strategy service. Phase 10 does not modify it.

### Risk — Phase 4
`backend/app/risk/` remains mandatory authorization for Paper. Future Live execution would require its own explicit activation boundary plus Live-specific hard limits.

### Paper Execution / Runtime — Phases 3, 4 and 7
Paper remains virtual-capital execution through `operator` or `strategy_runtime`, always behind Risk. Paper does not import or select Live.

### Accounting — Phase 2
Accounting owns active Paper money, fills, positions and ledger state. Live Readiness records do not masquerade as Paper Accounting.

### Backtesting / Evolution / Research — Phases 5–8
Backtesting owns historical evidence; Evolution owns fitness/lineage/manual replication; Research owns methodology/evaluation/manual candidate classification. None authorizes Live automatically.

### Legacy boundary — Phase 9
Mongo, mock engines, duplicate trading engines, legacy credentialed Binance code and dead UI were physically pruned. They are not fallback Live implementations.

### Live Readiness — Phase 10

`backend/app/live_execution/` is a separate, fail-closed readiness domain.

```text
ResearchStudy PROMOTED
        ↓
ResearchEvaluation PASS
        ↓
StrategyCandidate PROMOTED
        + current matching source SHA
        + real fail-closed Market Data
        + active Risk + clean Paper recovery
        + live-v1 policy + CANARY limits
        + emergency stop clear
        + CLEAN Live reconciliation
        + disabled non-withdrawing adapter
                    ↓
        LiveReadinessEvaluation
                    ↓
 ARCHITECTURE_READY or BLOCKED
                    ↓
 live_execution=disabled
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

`live-v1` defines absolute readiness ceilings of $100 deployable capital, $25 order notional, $50 symbol exposure, $100 portfolio exposure, $5 session loss and 5% drawdown, with three consecutive execution errors and 30-second stale-data threshold. `CANARY` rollout is 10%, making the current effective prepared-intent deployable-capital ceiling $10. These values are gates, not capital authorization.

#### Adapter boundary

`LiveExchangeAdapter` is read/reconciliation only. `DisabledLiveAdapter` reports `trading_enabled=False`, has no credentials and exposes no `create_order`, `place_order` or `submit_order` capability. There is no real venue implementation in Phase 10.

#### Intent preparation

A future command can be represented as `LiveOrderIntent` with deterministic `live:<sha256>` client id. Market symbols are normalized using the Market Data contract before identity derivation. An identical retry returns the existing intent; the same client id with a changed financial payload is an idempotency conflict.

Phase 10 can only classify an intent as `PREPARED` or `BLOCKED`; it cannot transmit it. Venue step/minimum rules, nonnegative exposure context, absolute Live ceilings and the CANARY fraction all fail closed. Quantity normalization, when needed by a future adapter, is downward-only.

#### Reconciliation

Read-only reconciliation treats as ambiguous any unexpected venue order, position or fill, any lookup match for a PREPARED intent, a trading-enabled adapter, or any persisted Live order record that claims transmission. Ambiguity creates `RECOVERY_REQUIRED` plus a circuit-breaker event and is never replayed, adopted or auto-cleared.

A positive readiness gate requires the latest reconciliation to be exactly `CLEAN` and no unresolved `RECOVERY_REQUIRED` record anywhere in Live reconciliation history. Phase 10 intentionally provides no manual resolution endpoint that can make ambiguous state trusted from a text reason alone.

#### Emergency stop

The singleton emergency stop blocks new Live intents. Activate/clear transitions are persisted as circuit-breaker audit events. Clearing requires an operator reason and zero unresolved Live reconciliations. Emergency stop does not auto-liquidate positions or cancel orders.

#### Readiness

Every readiness attempt writes a fresh immutable evaluation. It verifies the Research Study/Evaluation/Candidate chain and matching identity, current source SHA, Market Data mode, Risk, Paper recovery, active `live-v1`, CANARY/manual approval, exact CLEAN Live reconciliation, emergency stop and adapter permission metadata.

`architecture_ready=true` is always paired with `real_capital_blocked=true` during Phase 10.

## Active API/UI boundary

Live Readiness mounts:

- `GET /api/live/status`
- `GET /api/live/policy`
- `GET /api/live/readiness`
- `POST /api/live/readiness/evaluate`
- `POST /api/live/emergency-stop`
- `POST /api/live/emergency-stop/clear`
- `GET /api/live/reconciliations`
- `POST /api/live/reconcile`

There is no `/api/live/orders`, buy/sell route, credential-write route, recovery-resolution shortcut or activation endpoint. Settings shows readiness separately from `Live Execution: DISABLED` and `REAL CAPITAL: DISABLED`.

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
- `live_readiness=readiness_phase_10`
- `live_adapter=disabled_adapter`
- `live_execution=disabled`
- `real_capital_execution=disabled`
- `automated_trading=paper_enabled_phase_7`

## Verification

Static guards must prove no real-order transport, credential storage/write route, Paper→Live routing or S1-S4 change was introduced. Runtime correctness still requires fresh exact-HEAD backend/frontend execution. Phase 10 completion does not authorize real money.
