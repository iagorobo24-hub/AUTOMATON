# Agent Lifecycle

## Goal

Agents are experimental trading actors with identity, configuration, capital allocation, lineage and evidence. Lifecycle transitions must be observable and financially consistent.

## Phase 6 active contract

`backend/app/agent_evolution/` owns evidence-aware fitness and replication. The active policy is `evolution-v1`.

Phase 6 does **not** enable automatic trading, automatic replication, strategy mutation or Live execution.

## Identity states

The compatibility `Agent` row still exposes `ACTIVO`, `MUERTO` and historical `REPLICADO`. New Phase 6 replication leaves the parent and child `ACTIVO`; replication is an event/lineage fact, not a reason to disable the parent.

## Lifecycle evidence

Additive tables preserve:

- `AgentLifecycleEvent`: CREATED, LEGACY_BASELINE, REPLICATED_TO, REPLICATED_FROM, KILLED and explicit reasons;
- `AgentLineage`: parent, child, generation, inherited strategy version/source fingerprint, policy, fitness evaluation and allocated capital;
- `AgentFitnessEvaluation`: every explicit PASS/REJECT evaluation and its evidence inputs;
- `EvolutionPolicy`: versioned fitness/allocation contract.

Existing pre-Phase-6 agents receive one `LEGACY_BASELINE` event at startup. No historical fitness or lineage is fabricated.

## Fitness `evolution-v1`

A replication attempt always creates a fresh fitness evaluation. A previous PASS is not a reusable authorization token.

A candidate requires both reproducible historical evidence and its own forward Paper evidence:

- active agent;
- latest matching completed Backtest with strategy source SHA-256;
- Backtest source SHA must still match the currently active strategy source;
- at least 5 completed Backtest round trips;
- Backtest net return > 0;
- Backtest expectancy > 0;
- Backtest maximum drawdown <= 15%;
- at least 3 FILLED Paper SELL executions linked to the agent/account;
- Paper realized PnL > 0;
- structurally consistent Accounting;
- no Paper request in `RECOVERY_REQUIRED`.

Legacy `Trade` rows and standalone fills without `PaperExecution` provenance never count.

These are conservative infrastructure gates, not claims that a strategy is profitable, optimal, safe or ready for Live.

## Replication and capital conservation

Manual replication is available through `POST /api/agents/{id}/replicate`.

If fitness rejects, no child or financial transfer is created.

If fitness passes:

1. eligible capital is `min(cash - reserved_cash, funded_capital)`;
2. `evolution-v1` allocates 25% of that eligible amount;
3. the parent loses exactly that amount from `cash` and `funded_capital`;
4. the child receives exactly that amount as initial/funded cash;
5. paired `CAPITAL_TRANSFER_OUT` / `CAPITAL_TRANSFER_IN` ledger entries are persisted;
6. the child starts flat and inherits S1-S4 identity unchanged;
7. lineage and lifecycle events are committed with the transfer.

Replication therefore transfers virtual capital; it never copies or mints the parent's balance.

## Death / retirement

Killing an agent changes identity state to `MUERTO` and persists a `KILLED` event with an explicit reason. It does not zero cash, delete positions or erase evidence.

## Strategy mutation

Phase 6 does not mutate strategy parameters. Future mutations require a new configuration/version and reproducible evidence so descendants can be compared without hidden drift.

## Next boundary

Phase 7 may connect active strategy execution into long-running Paper sessions. That runtime must still route every order through Market Data -> Risk -> Paper -> Accounting and must not use Agent Evolution as a shortcut around those gates.
