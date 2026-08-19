# AUTOMATON Roadmap

This roadmap defines dependency order. A later phase must not be treated as complete while a prerequisite remains materially broken.

## Phase 0 — Transition baseline
**Status:** source gate satisfied; fresh repository execution remains pending.

## Phase 1 — Real Market Data
**Status:** source/contract gate satisfied; executable certification pending.

## Phase 2 — Portfolio & Accounting
**Status:** source/contract gate satisfied; executable certification pending.

## Phase 3 — Paper Execution
**Status:** source/contract gate satisfied; executable certification and real-provider smoke remain pending.

## Phase 4 — Risk Engine
**Status:** source/contract/static gate satisfied; executable certification and real-provider Paper smoke remain pending.

## Phase 5 — Backtesting & Evidence

Implemented: immutable real historical snapshots, canonical dataset SHA-256, strategy-source fingerprinting, deterministic next-candle `backtest-v1`, isolated financial state, persisted trades/equity/metrics and no optimizer/Live/automatic Paper path.

**Status:** source/contract/static gate satisfied. Exact-HEAD tests/build and a real historical-provider S1-S4 baseline remain pending; no performance numbers are inferred.

## Phase 6 — Agent Evolution

**Goal:** make lifecycle and replication evidence-aware without duplicating capital or silently enabling autonomous trading.

Implemented in source:

- additive `EvolutionPolicy`, `AgentFitnessEvaluation`, `AgentLineage` and `AgentLifecycleEvent` records;
- idempotent `evolution-v1` bootstrap and legacy-agent lifecycle baselines;
- explicit CREATED/KILLED/REPLICATED lifecycle reasons;
- fresh fitness evaluation for every replication attempt;
- fitness requires an active agent, matching completed Backtest, current strategy-source SHA-256, >=5 Backtest round trips, positive Backtest return/expectancy and <=15% drawdown;
- fitness also requires >=3 agent-specific FILLED Paper SELL executions, positive authoritative Paper realized PnL, Accounting structural integrity and no `RECOVERY_REQUIRED` Paper request;
- legacy `Trade` rows and Paper-labelled fills without `PaperExecution` provenance are excluded;
- `POST /api/agents/{id}/replicate` is manual and evidence-gated;
- child allocation defaults to 25% of `min(cash - reserved_cash, funded_capital)`;
- parent `cash` and `funded_capital` decrease by exactly the child's initial/funded cash;
- paired `CAPITAL_TRANSFER_OUT/IN` ledger entries preserve money conservation;
- the child starts flat, inherits the same strategy and records parent/generation/configuration lineage;
- parent stays ACTIVE; replication is an event, not an execution state;
- `/api/evolution` exposes status, active policy, fitness history/evaluation and lineage;
- strategy mutation, automatic replication, automatic trading and Live remain disabled;
- runtime reports `agent_evolution=evidence_phase_6` and `automated_trading=blocked_until_phase_7_runtime`.

**Exit condition:** no child can be created from legacy/unreconciled/stale evidence, and successful replication transfers rather than duplicates funded liquid capital with persistent lineage.

**Status:** source implementation present. Final exact-HEAD static audit and executable certification gate remain to be completed before formal source/static closure.

## Phase 7 — 24/7 Paper Operation

Add run/session identity, the controlled Strategy -> Risk -> Paper loop, restart/reconciliation procedures, provider resilience, observability and long-running forward Paper operation. Capital remains virtual.

## Phase 8 — Strategy Research

Evaluate richer or revised strategies using Phase 5 reproducible Backtests plus Phase 7 forward Paper evidence. Use out-of-sample/walk-forward discipline and version every promoted configuration.

## Phase 9 — Legacy Pruning

Delete obsolete Mongo/trading/synthetic services, pages, dependencies and configuration only after reference audits prove active concepts have migrated and no required evidence/recovery path depends on them.

## Phase 10 — Live Readiness

Satisfy `LIVE_TRADING_GATE.md`: design a separate exchange execution adapter, secrets/permissions, exchange constraints, reconciliation, emergency stop and staged rollout. Real-capital activation remains a separate explicit authorization, not an automatic consequence of completing this phase.

## Cross-phase certification debt

Phases 0-6 still require fresh exact-HEAD backend tests, frontend tests/build and relevant real-provider smoke evidence when an executable environment/CI is available. Static source closure must never be reported as a green runtime gate.

## Deferred product areas

Auth, payments, LLM chat, public APIs, multi-user features and UI customization remain deferred unless needed to operate or validate the trading product.
