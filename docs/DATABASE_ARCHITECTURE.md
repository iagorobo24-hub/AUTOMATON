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
- `live_readiness_evaluations` — immutable READY/BLOCKED technical snapshots; every record stores `real_capital_blocked=true` in Phase 10.
- `live_order_intents` — deterministic future-command preparation records. Each stores both a stable `client_order_id` and an SHA-256 `intent_fingerprint` of the canonical payload/policy assumptions. `PREPARED` does not mean transmitted.
- `live_order_records` — reserved/audit representation for future venue order identity; Phase 10 defaults to `NOT_TRANSMITTED`.
- `live_fill_records` — schema boundary for future reconciled venue fills; Phase 10 creates no real fills.
- `live_reconciliations` — CLEAN / RECOVERY_REQUIRED / RESOLVED reconciliation snapshots.
- `live_circuit_breaker_events` — persistent reasons for fail-closed Live blocks.
- `live_emergency_stop` — singleton persistent emergency-stop state.

No existing Paper/Accounting table is repurposed for Live Readiness.

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
- No Phase 10 record can change `real_capital_execution=disabled`.

## Phase 10 invariants

A future intent identity uses a deterministic client id derived from candidate, symbol, side and source-event id. The stored payload fingerprint additionally includes candidate, active policy version, source event, normalized symbol/side, quantity, reference price, projected symbol/portfolio exposure and deployable-capital context.

An identical retry returns the existing intent. Reusing the same deterministic client id with a different fingerprint is an idempotency conflict and fails closed rather than silently accepting changed financial intent.

Intent preparation requires:

- promoted StrategyCandidate;
- current source SHA still matching the candidate;
- a previous `ARCHITECTURE_READY` evaluation for that candidate;
- Phase 10 invariant `real_capital_blocked=true`;
- non-empty source event and symbol plus BUY/SELL side;
- emergency stop clear;
- venue rules and `live-v1` ceilings passing.

Phase 10 still cannot transmit the prepared intent.

Readiness itself checks the real/fail-closed Market Data contract, active Risk, Paper recovery, complete `live-v1` policy validity, reconciliation, emergency stop and disabled adapter capability.

A Live reconciliation ambiguity is never cleared merely because a later startup produces a CLEAN snapshot. Every historical `RECOVERY_REQUIRED` stays blocking until the operator explicitly changes that exact record to `RESOLVED` with a reason.

Emergency stop cannot be cleared while any Live reconciliation remains `RECOVERY_REQUIRED`.

## Startup and recovery

Startup initializes additive tables, bootstraps `live-v1` and emergency-stop baseline, and executes a **read-only** reconciliation through `DisabledLiveAdapter`.

Startup does not:

- transmit an exchange order;
- create real fills;
- load exchange secrets;
- activate real capital;
- clear unresolved Live recovery automatically;
- start a Paper session because Live Readiness is present.

## Current scope

- Paper remains virtual-capital execution.
- Live Readiness is architecture/evidence only.
- `live_execution=readiness_phase_10`.
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
