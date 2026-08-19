# GEMINI.md — AUTOMATON Project Contract

## Read first

Canonical direction: `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md`, `docs/ROADMAP.md`. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

Build autonomous Paper Trading on **real market data + virtual capital**, supported by reproducible historical/forward evidence and disciplined Strategy Research. Never present synthetic/mock results as financial evidence.

## Current runtime

- FastAPI + SQLModel + SQLite; React/Vite.
- Synthetic AgentEngine disabled.
- Phase 1 real-only Market Data.
- Phase 2 authoritative Accounting.
- Phase 3 deterministic Paper Execution.
- Phase 4 mandatory persistent Risk.
- Phase 5 isolated reproducible Backtesting.
- Phase 6 evidence-aware Agent Evolution.
- Phase 7 persistent autonomous Paper runtime.
- Phase 8 persistent Strategy Research.
- Runtime: `paper_trading=autonomous_phase_7`, `paper_runtime=runtime_phase_7`, `automated_trading=paper_enabled_phase_7`, `agent_evolution=evidence_phase_6`, `strategy_research=evidence_phase_8`, `live_execution=disabled`.

Autonomous Paper remains session-controlled. A Research candidate never starts or modifies a session automatically.

## Active Paper architecture

Manual path:
`operator -> real Market Data -> Risk -> PaperExecution(origin=operator) -> Accounting`.

Autonomous path:
`new real closed candle -> S1-S4 -> intent -> real Market Data -> Risk -> PaperExecution(origin=strategy_runtime) -> Accounting -> runtime cycle evidence`.

PaperExecution accepts only `operator` and `strategy_runtime`; both require persisted Risk ALLOW.

## Strategy Research — Phase 8

`backend/app/strategy_research/` owns methodology/evaluation/promotion evidence only.

`research-v1` requires repeating chronological non-overlapping `TRAIN -> VALIDATION -> OOS` folds based on completed Phase 5 Backtests. The first window freezes strategy version/source SHA and execution/cost assumptions; later windows must also match market/timeframe, initial capital and historical risk profile.

VALIDATION/OOS require sufficient round trips, positive return/expectancy, and OOS must respect drawdown/profit-factor/degradation limits.

Forward evidence requires STOPPED Phase 7 sessions on the same market/timeframe, matching-strategy agents, runtime cycles, >=3 unique FILLED closing SELL `PaperExecution(origin=strategy_runtime)` records, positive authoritative account-level realized-PnL context and clean Paper recovery. If qualifying account PnL is contaminated by FILLED manual/non-runtime Paper execution, Research fails closed.

Every promotion attempt creates a fresh evaluation and rechecks current strategy source SHA. `StrategyCandidate` means only that this exact source/config passed `research-v1` against referenced evidence at that time.

Research must never:

- modify S1-S4 automatically;
- optimize parameters and score on the same evidence window;
- auto-deploy a candidate to Paper Runtime;
- auto-replicate an agent;
- enable Live.

## Paper Runtime rules

SQLite session/cycle state is authoritative; asyncio tasks are process-local workers only. Restart reconciliation never resubmits uncertain orders or auto-resumes sessions. Financial ambiguity => RECOVERY_REQUIRED. No synthetic fallback or automatic replication.

## Backtesting / Evolution

Historical datasets are real/immutable/SHA-256 identified and source-fingerprinted. Signal on candle `t` executes no earlier than `t+1`. Evolution remains evidence-gated and manual. Never tune S1-S4 merely to improve observed scores.

## Live isolation

No active route/service may place a real exchange order. Do not introduce exchange credentials into Paper Runtime or Research. Live requires the future separate adapter and explicit authorization.

## Evidence discipline

Never merge Synthetic/Backtest/Paper/Live silently. Fixture tests prove software behavior, not trading performance. A Research PASS/PROMOTED label is not a profitability, safety or Live-readiness claim.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report green status without fresh exact-HEAD output. Real Research evidence additionally requires observed historical Backtests and completed forward Paper sessions.
