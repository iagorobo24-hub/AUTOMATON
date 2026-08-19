# Database Architecture

## Active baseline

The runtime uses SQLModel + SQLite through `backend/app/database.py`. MongoDB remains legacy and is not a source of truth for new product work.

## Active records

### Legacy/transition
- `Agent`: identity/strategy/status plus compatibility budget/parent fields.
- `Trade`: historical pre-provenance record outside valid Paper/Backtest/fitness evidence.

### Phase 2 Accounting
- `portfolio_accounts` (`Account`)
- `portfolio_orders` (`Order`)
- `portfolio_fills` (`Fill`)
- `portfolio_positions` (`Position`)
- `portfolio_ledger` (`LedgerEntry`)

Accounting is the active Paper financial authority. Phase 6 capital transfer uses the same Account/Ledger tables rather than introducing another balance system.

### Phase 3 Paper
- `paper_executions` (`PaperExecution`)
- `paper_requests` (`PaperRequest`)

### Phase 4 Risk
- `risk_profiles` (`RiskProfile`)
- `risk_decisions` (`RiskDecision`)

### Phase 5 Backtesting
- `backtest_datasets` (`BacktestDataset`)
- `backtest_candles` (`BacktestCandle`)
- `backtest_runs` (`BacktestRun`)
- `backtest_run_evidence` (`BacktestRunEvidence`)
- `backtest_trades` (`BacktestTrade`)
- `backtest_equity_points` (`BacktestEquityPoint`)

`backtest_run_evidence` is additive because SQLite `create_all()` creates tables but does not add columns to existing tables. Older runs may legitimately lack a fingerprint; new runs must create one.

### Phase 6 Agent Evolution

Evolution also uses additive tables so existing SQLite databases do not require destructive column migrations:

- `evolution_policies` (`EvolutionPolicy`): versioned fitness/allocation contract (`evolution-v1`).
- `agent_fitness_evaluations` (`AgentFitnessEvaluation`): immutable PASS/REJECT evidence snapshot, Backtest/source inputs, Paper counts/PnL and reason codes.
- `agent_lineage` (`AgentLineage`): one parent link per child, generation, inherited strategy version/source SHA, policy, fitness evaluation and allocated capital.
- `agent_lifecycle_events` (`AgentLifecycleEvent`): CREATED/LEGACY_BASELINE/REPLICATED_TO/REPLICATED_FROM/KILLED with explicit reasons.

`Agent.padre_id` remains a compatibility mirror; `AgentLineage` is the richer genealogy authority.

## Source-of-truth rules

- Accounting owns active Paper money/positions/PnL/fees/equity.
- PaperExecution owns forward execution provenance.
- PaperRequest owns Paper idempotency/recovery state.
- RiskProfile/RiskDecision own Paper authorization policy/evidence.
- Backtest tables own historical input/run evidence only.
- EvolutionPolicy/FitnessEvaluation/Lineage/LifecycleEvent own lifecycle/evolution evidence only.
- Evolution never owns a competing balance field; capital movement is persisted through Accounting.
- `Agent.presupuesto_*` remain compatibility mirrors.

## Phase 6 transfer invariants

For successful replication:

`eligible = min(parent.cash - parent.reserved_cash, parent.funded_capital)`

`allocation = eligible * evolution-v1.child_allocation_fraction`

Current default allocation fraction is 25%.

The transaction requires:

- parent available cash >= allocation;
- parent funded capital >= allocation;
- no pre-existing child Account;
- parent cash/funded decrease exactly by allocation;
- child initial/funded/cash equal exactly allocation;
- paired `CAPITAL_TRANSFER_OUT` / `CAPITAL_TRANSFER_IN` ledger entries;
- child has no copied positions;
- child + transfer + lineage/lifecycle evidence commit together.

This conserves funded virtual capital rather than treating replication as external funding.

## Fitness evidence integrity

A Phase 6 fitness PASS requires a completed same-strategy Backtest with `BacktestRunEvidence.strategy_code_sha256`, and that SHA must still match the active strategy module. It also requires agent/account-specific FILLED PaperExecution SELL provenance, positive Account.realized_pnl, structural Accounting integrity and no PaperRequest in `RECOVERY_REQUIRED`.

Legacy Trade rows and standalone Paper-labelled Fill records are not fitness evidence.

## Startup and recovery

Normal startup:

1. initializes SQLModel tables, including additive Backtest/Evolution tables;
2. bootstraps missing Accounting accounts from funded capital only;
3. bootstraps `evolution-v1`;
4. creates one `LEGACY_BASELINE` event for existing agents lacking lifecycle evidence;
5. bootstraps `risk-v1`;
6. invalidates interrupted Backtest runs;
7. reconciles Paper executions and Paper requests.

No startup step fabricates historical fitness, lineage or missing strategy fingerprints.

## Current scope limits

- long-only Paper and Backtest;
- operator-only Paper execution;
- manual evidence-gated replication only;
- no strategy mutation;
- no automatic replication;
- no autonomous Strategy→Paper loop until Phase 7;
- no optimizer;
- no Live execution.

## Rules

- Never mix evidence modes silently.
- Every successful normal Paper order has real-market and Risk provenance.
- Every new Backtest run has immutable historical/source provenance.
- Every successful replication has fresh fitness evidence and a conserving Accounting transfer.
- Ambiguous/incomplete evidence fails closed.
- Existing data is migrated, baselined or quarantined explicitly; never silently promoted.
- No new active Mongo collection is introduced.
