# Phase 6 — Agent Evolution Design

## Goal

Introduce evidence-aware agent lifecycle and financially conservative replication without enabling autonomous 24/7 trading, strategy mutation, shorts, leverage or Live execution.

## Boundaries

- SQLModel + SQLite remain active persistence.
- `Agent` remains the compatibility identity row; new evolution metadata is additive so existing SQLite databases do not require destructive column migrations.
- Accounting remains the only financial authority.
- Backtest and Paper evidence stay distinct.
- Legacy `Trade` rows never count toward fitness.
- Replication never duplicates money.
- S1-S4 are inherited unchanged; Phase 6 does not mutate strategy parameters.
- Automated strategy-to-Paper execution remains disabled after Phase 6.

## Additive records

### EvolutionPolicy

Persist a versioned `evolution-v1` policy with conservative defaults:

- minimum completed Backtest round trips: 5;
- Backtest net return must be positive;
- Backtest expectancy must be positive;
- maximum Backtest drawdown: 15%;
- minimum agent-specific Paper closing fills: 3;
- Paper realized PnL must be positive;
- child capital allocation fraction: 25% of eligible parent capital.

The policy is infrastructure, not a profitability claim. It can reject all current agents until real evidence exists.

### AgentFitnessEvaluation

Persist every explicit fitness evaluation with:

- agent;
- policy/version;
- chosen Backtest run;
- strategy/source fingerprint;
- observed Backtest round trips, return, expectancy and drawdown;
- observed Paper closed-trade count and realized PnL;
- PASS/REJECT;
- machine-readable reason codes;
- timestamp.

A PASS is single-purpose evidence for one replication attempt; it does not label the strategy globally profitable or validated.

### AgentLineage

Persist parent/child lineage with:

- parent and child IDs;
- generation;
- inherited strategy ID/version/source fingerprint;
- policy version;
- fitness evaluation ID;
- allocated capital;
- timestamp.

`Agent.padre_id` remains populated for compatibility, but `AgentLineage` is the richer authority.

### AgentLifecycleEvent

Persist CREATED, LEGACY_BASELINE, REPLICATED_FROM, REPLICATED_TO, KILLED and future lifecycle events with explicit reasons and optional lineage/fitness references.

## Fitness evidence

Fitness requires both configuration-level historical evidence and agent-specific forward Paper evidence.

Backtest evidence:

- `BacktestRun.status == COMPLETED`;
- strategy ID matches the agent;
- source fingerprint exists;
- run meets `evolution-v1` round-trip, return, expectancy and drawdown limits.

Paper evidence:

- authoritative Account exists;
- at least the policy minimum number of Paper SELL fills exists for that account;
- account `realized_pnl` is positive;
- no legacy `Trade` rows are counted.

The evaluator chooses the most recent completed matching Backtest run that has source fingerprint evidence. Missing/insufficient evidence yields REJECT, never an inferred PASS.

## Capital transfer

Replication transfers a fixed fraction of eligible parent capital under one accounting transaction.

Eligible transfer base is `min(parent.cash - reserved_cash, parent.funded_capital)`.

Allocation = `eligible_base * child_allocation_fraction`.

Requirements:

- parent agent ACTIVE;
- parent account exists;
- allocation > 0;
- parent remains non-negative in cash, reserve and funded capital;
- child account does not already exist;
- parent cash and funded capital both decrease by allocation;
- child initial/funded capital and cash equal allocation;
- paired ledger entries `CAPITAL_TRANSFER_OUT` / `CAPITAL_TRANSFER_IN` record the same amount and transfer reason;
- one commit establishes parent/child financial state together.

No open position is copied. The child starts flat.

## Replication flow

`POST /api/agents/{id}/replicate`:

1. resolve active parent;
2. evaluate and persist fitness;
3. reject with 409 if fitness is not PASS;
4. create child Agent with same strategy and `padre_id`;
5. atomically transfer capital into the child Account;
6. persist lineage and lifecycle events;
7. mark parent state `REPLICADO` only if that state is used as a historical event? No: parent remains ACTIVE so future Paper operation is not silently disabled. `REPLICADO` is not used as an execution state in Phase 6;
8. return child + lineage + allocation + fitness evidence.

The endpoint does not mutate strategy parameters and does not start trading.

## Lifecycle kill

`DELETE /api/agents/{id}` records an explicit lifecycle reason. Killing an agent changes identity state only; it does not zero cash or delete Accounting/evidence.

## API

Add `/api/evolution`:

- `GET /status`
- `GET /policies/active`
- `POST /agents/{agent_id}/fitness`
- `GET /agents/{agent_id}/fitness`
- `GET /agents/{agent_id}/lineage`

The existing agent replication endpoint delegates to the evolution domain.

## Restart/bootstrap

Startup bootstraps `evolution-v1` idempotently and creates `LEGACY_BASELINE` lifecycle events for pre-Phase-6 agents that do not yet have any lifecycle event. It never fabricates historical fitness or lineage.

## Tests / exit gate

Source/contract gate requires regression contracts for:

- policy bootstrap idempotency;
- missing Backtest/Paper evidence => REJECT;
- valid Backtest + agent-specific Paper evidence => PASS;
- legacy Trade rows ignored;
- strategy mismatch/source fingerprint absence rejected;
- parent/child capital conservation;
- reserved cash excluded;
- insufficient eligible capital rejected;
- child starts flat;
- lineage/generation persisted;
- lifecycle reasons persisted;
- repeated replication creates distinct children only after a fresh fitness evaluation and never reuses a prior PASS as an authorization token;
- killed/inactive parent cannot replicate;
- no strategy mutation;
- no automatic trading or Live capability introduced.

Execution certification remains separate and requires fresh exact-HEAD backend/frontend/build output.