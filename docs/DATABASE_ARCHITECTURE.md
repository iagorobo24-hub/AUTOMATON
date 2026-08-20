# Database Architecture

## Active baseline

The runtime uses SQLModel + SQLite. Mongo was physically removed in Phase 9 and is not an alternate runtime.

## Active records

### Legacy/transition
- `Agent`: active identity/strategy/status anchor.
- `Trade`: quarantined historical pre-provenance record with no validity as modern financial evidence.

### Phase 2 Accounting
- `portfolio_accounts`
- `portfolio_orders`
- `portfolio_fills`
- `portfolio_positions`
- `portfolio_ledger`

### Phase 3 Paper
- `paper_executions`
- `paper_requests`

### Phase 4 Risk
- `risk_profiles`
- `risk_decisions`

### Phase 5 Backtesting
- `backtest_datasets`
- `backtest_candles`
- `backtest_runs`
- `backtest_run_evidence`
- `backtest_trades`
- `backtest_equity_points`

### Phase 6 Agent Evolution
- `evolution_policies`
- `agent_fitness_evaluations`
- `agent_lineage`
- `agent_lifecycle_events`

### Phase 7 Paper Runtime
- `paper_runtime_sessions`
- `paper_runtime_agents`
- `paper_runtime_cycles`
- `paper_runtime_events`
- `paper_runtime_strategy_evidence`

### Phase 8 Strategy Research
- `research_policies`
- `research_studies`
- `research_windows`
- `research_evaluations`
- `strategy_candidates`

### Phase 10 Live Readiness

All Phase 10 tables are additive. They prepare/audit a future Live boundary and are **not real exchange financial truth**:

- `live_policies` — versioned `live-v1` ceilings and rollout requirements.
- `live_readiness_evaluations` — immutable READY/BLOCKED technical snapshots; every Phase 10 result keeps `real_capital_blocked=true`.
- `live_order_intents` — deterministic future-command preparation records with stable client id and SHA-256 payload fingerprint. `PREPARED` does not mean transmitted.
- `live_order_records` — reserved future venue-order representation; Phase 10 permits only `NOT_TRANSMITTED` as coherent state.
- `live_fill_records` — schema boundary for future reconciled venue fills; Phase 10 creates no real fills.
- `live_reconciliations` — CLEAN / RECOVERY_REQUIRED snapshots. Phase 10 does not expose a shortcut for relabeling ambiguity as resolved.
- `live_circuit_breaker_events` — persistent reconciliation and emergency-stop audit events.
- `live_emergency_stop` — singleton persistent emergency-stop state.

No existing Paper/Accounting table is repurposed for Live Readiness. No table persists API keys, exchange secrets or private keys.

## Source-of-truth rules

- Accounting owns active Paper money, positions, PnL and fees.
- PaperExecution/PaperRequest own Paper execution provenance and recovery.
- Risk owns authorization policy/evidence.
- Backtest owns historical evidence.
- Evolution owns fitness/lineage/lifecycle evidence.
- Paper Runtime owns session/cycle/source provenance.
- Research owns methodology/evaluation/candidate evidence.
- Live Readiness owns only readiness, future-intent, reconciliation and circuit-breaker evidence.
- `LiveOrderIntent(PREPARED)` is not an exchange order.
- `LiveReadinessEvaluation(ARCHITECTURE_READY)` is not capital authorization.
- No Phase 10 record can change `live_execution=disabled` or `real_capital_execution=disabled`.

## Phase 10 invariants

A future intent identity uses a deterministic client id derived from candidate, canonical Market Data symbol, side and source-event id. The stored payload fingerprint additionally includes policy version, quantity, reference price, projected symbol/portfolio exposure and deployable-capital context.

An identical retry returns the existing intent. Reusing the same deterministic client id with a different fingerprint is an idempotency conflict. Symbol aliases normalize before identity creation so equivalent markets cannot silently produce duplicate commands.

Intent preparation requires:

- valid `StrategyCandidate(status=PROMOTED)` whose referenced ResearchStudy is PROMOTED and ResearchEvaluation is PASS;
- identical strategy ID/version/source SHA across Study, Evaluation and Candidate;
- current source SHA still matching the candidate;
- a fresh Phase 10 `ARCHITECTURE_READY` evaluation;
- Phase 10 invariant `real_capital_blocked=true`;
- canonical symbol and BUY/SELL side;
- emergency stop clear;
- venue rules and `live-v1` gates passing.

`live-v1` enforces both its absolute ceilings and the CANARY rollout fraction. With $100 max deployable capital and 10% rollout fraction, the effective current prepared-intent deployable-capital ceiling is $10. Quantity normalization is downward-only.

Phase 10 still cannot transmit a prepared intent.

Readiness itself checks the real/fail-closed Market Data contract, active Risk, Paper recovery, full Research provenance, active `live-v1`, emergency stop, exact CLEAN reconciliation and disabled adapter capability/permission metadata.

Reconciliation fails closed if it observes any unexplained venue order/position/fill, lookup match for PREPARED intent, trading-enabled adapter, or persisted Live order record suggesting transmission. Every historical `RECOVERY_REQUIRED` remains blocking; a later CLEAN snapshot does not erase it automatically.

Emergency-stop activate/clear transitions are audited. Emergency stop cannot clear while any Live reconciliation remains `RECOVERY_REQUIRED`.

## Startup and recovery

Startup initializes additive tables, bootstraps `live-v1` and emergency-stop baseline, and executes a **read-only** reconciliation through `DisabledLiveAdapter`.

Startup does not:

- transmit an exchange order;
- create real fills;
- load exchange secrets;
- activate Live execution or real capital;
- clear unresolved Live recovery automatically;
- start a Paper session because Live Readiness is present.

## Current scope

- Paper remains virtual-capital execution.
- `live_readiness=readiness_phase_10`.
- `live_adapter=disabled_adapter`.
- `live_execution=disabled`.
- `real_capital_execution=disabled`.
- no actual exchange trading adapter;
- no exchange secret persistence;
- no Live order endpoint;
- no automatic liquidation;
- S1-S4 unchanged.

## Rules

- Never mix Paper and Live records as one source of truth.
- Never auto-replay uncertain financial activity.
- Never fabricate or erase reconciliation provenance.
- Never accept a changed payload under an existing Live idempotency key.
- Never interpret readiness ceilings as funded/authorized capital.
- Never persist exchange secret values in these tables.
