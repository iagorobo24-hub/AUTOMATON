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
- `paper_runtime_sessions`
- `paper_runtime_agents`
- `paper_runtime_cycles`
- `paper_runtime_events`

The unique runtime-cycle constraint is a persistent idempotency boundary: the same session/agent/candle cannot create a second cycle.

### Phase 8 Strategy Research

All Research tables are additive so existing SQLite installations require no destructive column migration:

- `research_policies` (`ResearchPolicy`): versioned methodology thresholds (`research-v1`).
- `research_studies` (`ResearchStudy`): strategy research identity and frozen source/config assumptions.
- `research_windows` (`ResearchWindow`): explicit Backtest-run references with TRAIN/VALIDATION/OOS role and ordinal.
- `research_evaluations` (`ResearchEvaluation`): immutable PASS/REJECT evidence snapshots and referenced historical/forward ids/metrics.
- `strategy_candidates` (`StrategyCandidate`): one manual promotion record per exact strategy/version/source-SHA identity.

Research does not copy Backtest trades, Paper fills, PnL or balances. It stores references/snapshots needed to explain a decision.

## Source-of-truth rules

- Accounting owns active Paper money, positions, PnL and fees.
- PaperExecution owns execution provenance.
- PaperRequest owns Paper command idempotency/recovery.
- RiskProfile/RiskDecision own authorization policy/evidence.
- Backtest records own historical execution/input evidence.
- Evolution records own lifecycle/fitness/lineage evidence.
- Paper Runtime owns orchestration/session/cycle evidence only.
- Research records own methodology/evaluation/promotion evidence only.
- StrategyCandidate never changes source code or runtime configuration by itself.
- The asyncio scheduler is process-local worker state, not persistent authority.

## Phase 8 evidence invariants

A ResearchStudy's first attached Backtest freezes strategy version/source SHA, execution policy, fee/slippage and position fraction. Subsequent windows must match those and the first window's symbol/timeframe, initial capital and historical risk-profile version.

ResearchWindow sequence repeats:

`TRAIN -> VALIDATION -> OOS`

Windows are chronological and non-overlapping. A complete evaluation requires full folds rather than arbitrary subsets.

ResearchEvaluation snapshots do not become financial truth. They reference Backtest runs and qualifying STOPPED PaperRuntime sessions and record the metrics/reasons used by `research-v1`.

Forward account PnL context is accepted only when qualifying accounts have no FILLED non-`strategy_runtime` Paper execution and no unresolved Paper recovery. This prevents current Account.realized_pnl from being silently attributed to a Research session when manual Paper activity is mixed in.

Promotion creates a fresh evaluation and then, on PASS, one StrategyCandidate for the exact strategy/version/source SHA. Candidate uniqueness prevents multiple competing promotion records for the same exact identity.

## Startup and recovery

Normal startup initializes additive SQLModel tables and bootstraps Accounting, Evolution, Risk and `research-v1`, then performs Backtest/Paper/Runtime recovery. Research has no long-running evaluation worker to resume: evaluations are synchronous over already persisted evidence.

No startup step fabricates Research evaluations/candidates or starts a Paper session because a candidate exists.

## Current scope

- long-only Paper/Backtest;
- manual and Phase 7 session-controlled autonomous Paper;
- S1-S4 unchanged by Research;
- manual evidence-gated replication only;
- manual evidence-gated Research promotion only;
- no automatic replication/mutation/deployment;
- no optimizer;
- no Live execution.

## Rules

- Never mix evidence modes silently.
- Never auto-resume interrupted financial activity.
- Ambiguous/incomplete evidence fails closed.
- Runtime orchestration must go through Risk -> Paper -> Accounting.
- Research may reference financial evidence but never mutate it.
- No new active Mongo collection is introduced.
