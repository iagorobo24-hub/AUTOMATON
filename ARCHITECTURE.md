# AUTOMATON Architecture

## Objective

AUTOMATON researches autonomous crypto-trading agents using **real market data and virtual capital** until explicit evidence/safety gates justify any future Live mode.

## Non-negotiable boundaries

1. Synthetic data is test-only and explicitly labelled.
2. Backtest and Paper use real market data and virtual capital.
3. Live is a separate future execution adapter.
4. Evidence always preserves mode/provenance.
5. SQLModel/SQLite is the active persistence baseline.
6. Legacy Mongo/trading services are not reactivated as shortcuts.
7. Accounting is the only active Paper financial authority.
8. Normal Paper execution requires persisted current-profile Risk ALLOW.
9. Backtest state is isolated from Paper and cannot execute before the candle after the signal observation.
10. Agent replication may transfer capital but cannot mint/copy it.
11. Fitness cannot promote legacy/unreconciled/stale strategy evidence.
12. Phase 6 does not enable automatic trading, automatic replication, mutation or Live.

## Active domains

### Market Data — Phase 1

`backend/app/market_data/` owns current real Quote/Candle contracts and quality controls. `backend/app/backtesting/providers/binance_history.py` is the separate public read-only historical provider.

### Strategy / Signals

S1-S4 remain deterministic baseline implementations in `backend/app/services/strategies.py`. Their source is SHA-256 fingerprinted for Backtest evidence. Phase 6 compares fitness Backtest fingerprints against the current source so stale algorithm evidence fails closed.

### Risk — Phase 4

`backend/app/risk/` owns versioned Paper authorization and circuit breaker state. Normal Paper financial state cannot be created without a persisted matching ALLOW.

### Paper Execution — Phase 3 + Risk gate

`backend/app/paper_execution/` owns operator-originated deterministic virtual MARKET execution:

```text
request_id -> Real Market Data -> Risk -> Paper Execution -> Accounting
```

Paper persists provenance/idempotency/recovery state and has no Live exchange adapter.

### Portfolio & Accounting — Phase 2 + Phase 6 transfer primitive

`backend/app/accounting/` owns Account, Order, Fill, Position and LedgerEntry. Funding is not PnL; long-only is the defined scope.

Phase 6 adds `AccountingService.transfer_to_child()`:

- transfer only from funded liquid capital;
- exclude reserved cash;
- decrease parent cash/funded capital by the exact allocation;
- create a flat child account with the exact same amount;
- paired `CAPITAL_TRANSFER_OUT/IN` entries;
- can participate in one larger transaction with child/lineage creation.

### Backtesting & Evidence — Phase 5

`backend/app/backtesting/` freezes immutable real historical datasets, persists canonical SHA-256, executes deterministic `backtest-v1` using signal-close `t` -> execution-open `t+1`, and stores run/source/trade/equity/metric evidence separately from Paper.

`BacktestRunEvidence.strategy_code_sha256` identifies the exact active strategy source used by new runs. Missing fingerprints on older runs remain missing rather than being fabricated.

### Agent Evolution — Phase 6

`backend/app/agent_evolution/` owns evidence-aware lifecycle and replication.

#### Policy

`EvolutionPolicy` persists `evolution-v1`:

- min 5 Backtest round trips;
- Backtest net return > 0;
- Backtest expectancy > 0;
- max Backtest drawdown 15%;
- min 3 agent-specific FILLED Paper SELL executions;
- Paper realized PnL > 0;
- child allocation fraction 25% of eligible funded liquid capital.

These limits are research infrastructure, not profitability claims.

#### Fitness

Every replication attempt creates a fresh `AgentFitnessEvaluation`.

Fitness requires:

- ACTIVE agent;
- completed Backtest for the same strategy;
- Backtest source fingerprint present and equal to current strategy source;
- Backtest metrics within `evolution-v1` gates;
- Paper closes represented by actual `PaperExecution` FILLED SELL records for that agent/account;
- positive authoritative Account.realized_pnl;
- structural Accounting integrity;
- no `PaperRequest.status=RECOVERY_REQUIRED`.

Legacy `Trade` and unprovenanced Paper-labelled Fill rows do not count.

#### Replication / lineage

`AgentEvolutionService.replicate()`:

1. obtains a fresh fitness evaluation;
2. rejects without creating child state if fitness != PASS;
3. computes `eligible=min(cash-reserved_cash, funded_capital)`;
4. allocates 25% under `evolution-v1`;
5. creates a child with the same strategy;
6. transfers rather than duplicates capital;
7. persists `AgentLineage`, strategy version/source SHA, generation and allocation;
8. persists `REPLICATED_TO` / `REPLICATED_FROM` events;
9. commits child + financial transfer + lineage/events together.

The parent remains ACTIVE. Replication is history/evidence, not a terminal execution state.

#### Lifecycle

`AgentLifecycleEvent` records CREATED, LEGACY_BASELINE, REPLICATED_TO, REPLICATED_FROM and KILLED with explicit reasons. Killing an agent never zeroes or deletes Accounting state.

## Runtime/API boundary

Active research/trading APIs include:

- `/api/market-data/*`
- `/api/accounting/*`
- `/api/risk/*`
- `/api/paper/*`
- `/api/backtests/*`
- `/api/evolution/status`
- `/api/evolution/policies/active`
- `/api/evolution/agents/{agent_id}/fitness`
- `/api/evolution/agents/{agent_id}/lineage`
- `/api/agents/{agent_id}/replicate`

No autonomous-trading-start, auto-replication, optimizer or Live endpoint exists.

## Current runtime

`backend/app/main.py` reports:

- `runtime_mode=transition`;
- `market_data=real_contract_available`;
- `accounting=authoritative_phase_2`;
- `risk=authoritative_phase_4`;
- `paper_trading=operator_only_phase_4`;
- `backtesting=evidence_phase_5`;
- `agent_evolution=evidence_phase_6`;
- `automated_trading=blocked_until_phase_7_runtime`;
- `live_execution=disabled`.

Startup initializes tables, Accounting baseline, `evolution-v1`/lifecycle baselines, `risk-v1`, invalidates interrupted Backtests and reconciles Paper recovery.

## Next automated Paper boundary — Phase 7

```text
Long-running Session
        |
        v
Market Data -> Strategy Intent -> Risk -> Paper Execution -> Accounting
                                      |               |
                                      +----------> Evidence
```

Phase 7 may activate that controlled loop with virtual capital. Agent Evolution never bypasses Risk/Paper/Accounting.

## Verification

Static review establishes source/contract coherence only. Runtime correctness, S1-S4 performance and fitness quality require fresh exact-HEAD backend/frontend execution and real-provider evidence.
