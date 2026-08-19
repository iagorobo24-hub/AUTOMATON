# Database Architecture

## Active baseline

The runtime uses SQLModel + SQLite. MongoDB remains legacy and is not a source of truth for new product work.

## Active records

### Legacy/transition
- `Agent`: identity/strategy/status plus compatibility budget/parent fields.
- `Trade`: historical pre-provenance record outside valid financial evidence.

### Phase 2 Accounting
- `portfolio_accounts`
- `portfolio_orders`
- `portfolio_fills`
- `portfolio_positions`
- `portfolio_ledger`

Accounting is the active Paper financial authority.

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

Evolution never owns competing balances; replication moves capital through Accounting.

### Phase 7 Paper Runtime

Additive SQLite-compatible runtime tables:

- `paper_runtime_sessions` (`PaperRuntimeSession`): persistent session identity/state, polling policy, heartbeat, failure counter and recovery state.
- `paper_runtime_agents` (`PaperRuntimeAgent`): session/agent attachment and last processed candle/signal/outcome.
- `paper_runtime_cycles` (`PaperRuntimeCycle`): one durable result per `(session_id, agent_id, candle_close)`, with request/Risk/Paper links.
- `paper_runtime_events` (`PaperRuntimeEvent`): session lifecycle, degradation and recovery evidence.

The unique cycle constraint is a persistent idempotency boundary: polling the same candle again cannot create another runtime cycle for the same session/agent.

## Source-of-truth rules

- Accounting owns active Paper money, positions, PnL and fees.
- PaperExecution owns execution provenance.
- PaperRequest owns Paper command idempotency/recovery.
- RiskProfile/RiskDecision own authorization policy/evidence.
- Backtest records own historical research evidence only.
- Evolution records own lifecycle/fitness/lineage evidence only.
- Paper Runtime owns orchestration/session/cycle evidence only; it never owns a second balance or direct fill path.
- The asyncio scheduler is process-local worker state, not persistent authority.

## Phase 7 recovery invariants

On startup:

1. initialize additive SQLModel tables;
2. bootstrap Accounting/evolution/risk state;
3. invalidate interrupted Backtests;
4. reconcile pending PaperExecution records;
5. reconcile PaperRequest records;
6. reconcile interrupted runtime INTENT cycles against existing Paper state **without submitting another order**;
7. mark previously RUNNING/DEGRADED runtime sessions `RECOVERY_REQUIRED`;
8. spawn no autonomous session automatically.

A runtime session may start/recover only when all attached agents are ACTIVE, their Accounting accounts exist and neither `PaperRequest` nor `PaperExecution` has unresolved recovery state.

`RECOVERY_REQUIRED` sessions retain ownership of the same agent/symbol/interval so another session cannot start on top of uncertain state.

## Runtime cycle identity

Runtime request id is derived deterministically from:

`runtime-v1 | session | agent | symbol | candle_close | signal`

The PaperRequest and unique runtime-cycle records together prevent duplicate trading after repeated polling/retries/restarts.

## Current scope

- long-only Paper/Backtest;
- manual and Phase 7 session-controlled autonomous Paper;
- S1-S4 unchanged;
- manual evidence-gated replication only;
- no automatic replication/mutation;
- no optimizer;
- no Live execution.

## Rules

- Never mix evidence modes silently.
- Never auto-resume interrupted financial activity.
- Ambiguous/incomplete evidence fails closed.
- Runtime orchestration must go through Risk -> Paper -> Accounting.
- No new active Mongo collection is introduced.
