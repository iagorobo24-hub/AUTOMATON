# GEMINI.md — AUTOMATON Project Contract

## Read first

Canonical direction: `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md`, `docs/ROADMAP.md`. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

Build autonomous Paper Trading on **real market data + virtual capital**, supported by reproducible Backtest/Paper evidence. Never present synthetic/mock results as financial evidence.

## Current runtime

- FastAPI + SQLModel + SQLite; React/Vite.
- Synthetic AgentEngine disabled.
- Phase 1 real-only Market Data.
- Phase 2 authoritative Accounting.
- Phase 3 operator-only deterministic Paper.
- Phase 4 mandatory persistent Risk.
- Phase 5 isolated reproducible Backtesting.
- Phase 6 evidence-aware Agent Evolution.
- Runtime: `backtesting=evidence_phase_5`, `agent_evolution=evidence_phase_6`, `automated_trading=blocked_until_phase_7_runtime`, `live_execution=disabled`.

## Boundaries

Paper path: `Market Data -> Risk -> Paper Execution -> Accounting`.
Future Phase 7 automation inserts Strategy Intent before Risk; it may never bypass Risk/Paper/Accounting.
Backtest is a parallel historical path and never mutates Paper state.

## Accounting / replication

- Accounting owns all active financial state; Agent budget fields are mirrors.
- Funding is not profit.
- Long-only; do not invent shorts/margin/leverage.
- Phase 6 replication transfers funded liquid capital; it never copies/mints balances.
- Eligible transfer base is `min(cash-reserved_cash, funded_capital)`; `evolution-v1` currently allocates 25%.
- Parent cash/funded decrease exactly by child initial/funded cash; paired transfer ledger entries are required.
- Child starts flat and inherits the same strategy.

## Agent Evolution

`backend/app/agent_evolution/` owns `evolution-v1`, fitness, lineage and lifecycle evidence.

A replication attempt must create a fresh evaluation and PASS only when:

- agent is ACTIVE;
- completed same-strategy Backtest exists;
- Backtest source fingerprint exists and still matches current strategy source;
- >=5 Backtest round trips;
- Backtest return/expectancy > 0 and drawdown <=15%;
- >=3 agent-specific FILLED Paper SELL executions with PaperExecution provenance;
- authoritative Paper realized PnL >0;
- Accounting structural integrity holds;
- no PaperRequest is `RECOVERY_REQUIRED`.

Legacy Trade rows or standalone Paper-labelled fills do not count. A PASS is permission for one replication attempt, not a profitability/safety claim. No strategy mutation, auto-replication or auto-trading in Phase 6.

## Backtesting

Historical datasets are real/immutable/SHA-256 identified; mixed/gapped/duplicate/out-of-order data is rejected. Signal on candle `t` executes no earlier than `t+1`. New runs persist strategy source SHA-256. Never modify S1-S4 to make evaluated results look better.

## Paper / Risk

Paper prices come from real Market Data. Normal execution requires persisted one-time current-profile Risk ALLOW. Ambiguous recovery fails closed. No Live credentials/adapter.

## Legacy

Mongo/old Trading/Paper engines/mock fallbacks and unmounted product areas are not active contracts. Migrate useful concepts only; never reactivate them as shortcuts.

## Evidence

Never merge Synthetic/Backtest/Paper/Live silently. Fixture tests prove software behavior, not trading performance. No profitable/optimized/validated/safe claim without reproducible observed evidence.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report green status without fresh exact-HEAD output.
