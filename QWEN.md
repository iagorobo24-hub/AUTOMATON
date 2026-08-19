# QWEN.md — AUTOMATON Project Contract

Use `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md` as product truth. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

AUTOMATON targets autonomous Paper Trading on **real market data with virtual capital**, supported by reproducible Backtest/Paper evidence and explicit risk/evolution gates.

## Current state

- FastAPI + SQLModel + SQLite; React/Vite.
- Synthetic AgentEngine disabled.
- Phase 1 real-only Market Data.
- Phase 2 authoritative Accounting.
- Phase 3 deterministic operator-only Paper.
- Phase 4 mandatory persistent Risk.
- Phase 5 immutable historical Backtesting with strategy source fingerprinting.
- Phase 6 evidence-aware Agent Evolution.
- Runtime: `agent_evolution=evidence_phase_6`, `automated_trading=blocked_until_phase_7_runtime`, `live_execution=disabled`.

## Mode separation

Synthetic/Test, Backtest, Paper and Live are distinct. Never fabricate or merge market data, fills, PnL or evidence across modes.

## Paper architecture

Future autonomous path is `Market Data -> Strategy Intent -> Risk -> Paper Execution -> Accounting -> Evidence`.
Phase 6 does not activate Strategy Intent automatically. Risk and Paper cannot be bypassed.

## Backtesting

Historical data is real, immutable and SHA-256 identified. Signal on candle `t` executes no earlier than `t+1`. New runs persist the active strategy source SHA. Backtest state never mutates Paper state. S1-S4 remain baseline code, not profitability evidence.

## Agent Evolution

`backend/app/agent_evolution/` owns `evolution-v1`, fitness, lineage and lifecycle evidence.

Replication is manual and requires a fresh PASS with:

- ACTIVE agent;
- same-strategy completed Backtest;
- Backtest source SHA still equal to current strategy source;
- >=5 round trips, positive return/expectancy, drawdown <=15%;
- >=3 FILLED agent-specific Paper SELL executions with PaperExecution provenance;
- positive authoritative Paper realized PnL;
- Accounting integrity;
- no PaperRequest `RECOVERY_REQUIRED`.

Legacy Trade rows or standalone Paper-labelled fills do not count.

Successful replication transfers, never duplicates, capital:

`eligible = min(cash-reserved_cash, funded_capital)`

`evolution-v1` currently allocates 25%. Parent cash/funded capital decrease exactly by child initial/funded cash, paired ledger entries are required, child starts flat, strategy is inherited unchanged, lineage/generation/source fingerprint are persisted, parent stays ACTIVE.

A fitness PASS is permission for one replication attempt, not a profitability or safety claim. No strategy mutation, auto-replication or automatic trading in Phase 6.

## Live / legacy

No Live adapter or real-order route is active. Mongo/old engines/mock fallbacks remain legacy and must not be reactivated as shortcuts.

## Evidence discipline

Fixture tests prove software behavior, not trading performance. No profitable/optimized/validated/safe claim without observed reproducible evidence.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never claim verification without fresh execution on the exact HEAD.
