# Database Architecture

## Active baseline

The runtime uses SQLModel + SQLite. Phase 9 physically removed the former MongoDB service, injection/configuration, models, dependencies and development containers. Mongo is not an alternate or preserved runtime.

## Active records

### Legacy/transition
- `Agent`: identity/strategy/status plus compatibility budget/parent fields. It remains an active anchor for Accounting, Evolution, Runtime and Research relationships.
- `Trade`: historical pre-provenance record outside valid financial evidence. It is retained only for quarantined inspection and is exposed with `evidence_mode=legacy_unclassified` and `evidence_valid=false`.

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
- `paper_runtime_strategy_evidence`

`paper_runtime_strategy_evidence` is additive one-to-one evidence per session/agent. It captures strategy ID/version/source SHA at the first start so later Research can prove which code produced forward evidence. Resume/recovery verifies that identity and fails on drift. A session that already had `started_at` before this evidence existed cannot be assigned a fingerprint retroactively.

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
- Paper Runtime owns orchestration/session/cycle evidence and the source fingerprint captured for each started strategy session.
- Research records own methodology/evaluation/promotion evidence only.
- StrategyCandidate never changes source code or runtime configuration by itself.
- The asyncio scheduler is process-local worker state, not persistent authority.
- No Mongo collection or deleted legacy model is a source of truth after Phase 9.

## Phase 8 evidence invariants

A ResearchStudy's first attached Backtest freezes strategy version/source SHA, execution policy, fee/slippage and position fraction. Subsequent windows must match those and the first window's symbol/timeframe, initial capital and historical risk-profile version.

ResearchWindow sequence repeats:

`TRAIN -> VALIDATION -> OOS`

Windows are chronological and non-overlapping. A complete evaluation requires full folds rather than arbitrary subsets.

ResearchEvaluation snapshots do not become financial truth. They reference Backtest runs and qualifying STOPPED PaperRuntime sessions and record the metrics/reasons used by `research-v1`.

Forward evidence is eligible only when the Phase 7 captured strategy ID/version/source SHA matches the frozen historical Research identity. Sessions without captured start-time provenance remain readable but are not eligible for promotion evidence.

Forward account PnL context is accepted only when every FILLED execution in a qualifying account belongs to the exact Research-selected sessions and no Paper recovery remains unresolved. This prevents current `Account.realized_pnl` from being silently attributed to Research when other manual or autonomous activity is mixed in.

Promotion creates a fresh evaluation and then, on PASS, one StrategyCandidate for the exact strategy/version/source SHA. Promotion also rechecks the current source SHA, so accepted evidence requires historical SHA == forward captured SHA == current SHA.

## Phase 9 persistence boundary

Phase 9 is intentionally schema-conservative for active records: it removes the competing historical Mongo architecture and unused Pydantic model stack rather than migrating or rewriting active SQLModel evidence. Existing SQLite `Agent`/`Trade` transition rows are not silently converted into newer financial evidence.

Development Docker Compose now runs the backend with a SQLite volume and contains no MongoDB or mongo-express service.

## Startup and recovery

Normal startup initializes additive SQLModel tables and bootstraps Accounting, Evolution, Risk and `research-v1`, then performs Backtest/Paper/Runtime recovery. Research has no long-running evaluation worker to resume: evaluations are synchronous over already persisted evidence.

No startup step fabricates Research evaluations/candidates, retroactively fingerprints old sessions, starts a Paper session because a candidate exists, or initializes Mongo.

## Current scope

- long-only Paper/Backtest;
- manual and Phase 7 session-controlled autonomous Paper;
- S1-S4 unchanged by Research/Phase 9;
- manual evidence-gated replication only;
- manual evidence-gated Research promotion only;
- no automatic replication/mutation/deployment;
- no optimizer;
- no Mongo runtime;
- no Live execution.

## Rules

- Never mix evidence modes silently.
- Never auto-resume interrupted financial activity.
- Never fabricate source provenance retroactively.
- Ambiguous/incomplete evidence fails closed.
- Runtime orchestration must go through Risk -> Paper -> Accounting.
- Research may reference financial evidence but never mutate it.
- Do not reintroduce a competing Mongo or legacy financial store.
