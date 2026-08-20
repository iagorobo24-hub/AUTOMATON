# GEMINI.md — AUTOMATON Project Contract

## Read first

Canonical direction: `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md`, `docs/ROADMAP.md`. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

Build autonomous Paper Trading on **real market data + virtual capital**, supported by reproducible historical/forward evidence and disciplined Strategy Research. Never present generated/mock results as financial evidence.

## Current runtime

- FastAPI + SQLModel + SQLite; React/Vite.
- Phase 1 real-only Market Data.
- Phase 2 authoritative Accounting.
- Phase 3 deterministic Paper Execution.
- Phase 4 mandatory persistent Risk.
- Phase 5 isolated reproducible Backtesting.
- Phase 6 evidence-aware Agent Evolution.
- Phase 7 persistent autonomous Paper runtime.
- Phase 8 persistent Strategy Research.
- Phase 9 physically pruned the superseded Mongo/mock/trading architecture; the old Synthetic AgentEngine and mock-fallback BinanceService no longer exist in source.
- Runtime: `paper_trading=autonomous_phase_7`, `paper_runtime=runtime_phase_7`, `automated_trading=paper_enabled_phase_7`, `agent_evolution=evidence_phase_6`, `strategy_research=evidence_phase_8`, `legacy_pruning=pruned_phase_9`, `live_execution=disabled`.

Autonomous Paper remains session-controlled. A Research candidate never starts or modifies a session automatically.

## Active Paper architecture

Manual path:
`operator -> real Market Data -> Risk -> PaperExecution(origin=operator) -> Accounting`.

Autonomous path:
`new real closed candle -> S1-S4 -> intent -> real Market Data -> Risk -> PaperExecution(origin=strategy_runtime) -> Accounting -> runtime cycle evidence`.

PaperExecution accepts only `operator` and `strategy_runtime`; both require persisted Risk ALLOW.

## Strategy Research — Phase 8

`backend/app/strategy_research/` owns methodology/evaluation/promotion evidence only.

`research-v1` requires repeating chronological non-overlapping `TRAIN -> VALIDATION -> OOS` folds based on completed Phase 5 Backtests. Historical and forward evidence must preserve matching strategy/source identity and comparable execution assumptions. Forward Paper also requires clean recovery and unambiguous execution attribution.

Every promotion attempt creates a fresh evaluation and rechecks current strategy source SHA. `StrategyCandidate` means only that this exact source/config passed `research-v1` against referenced evidence at that time.

Research must never modify S1-S4 automatically, optimize-and-score the same evidence, auto-deploy candidates, auto-replicate agents or enable Live.

## Phase 9 pruning rules

Do not recreate deleted Mongo services, legacy API aggregators, old trading/Paper/risk engines, mock market fallbacks, Alpha/Beta/Gamma executables or unreachable frontend surfaces as shortcuts. Useful historical strategy ideas belong in research documentation until explicitly reimplemented and versioned through the current evidence pipeline.

`Agent` remains an active identity/lifecycle model. Pre-provenance `Trade` remains quarantined historical data with invalid evidence status; do not reinterpret it as Paper/Backtest/Research evidence.

## Paper Runtime rules

SQLite session/cycle state is authoritative; asyncio tasks are process-local workers only. Restart reconciliation never resubmits uncertain orders or auto-resumes sessions. Financial ambiguity => RECOVERY_REQUIRED. No generated fallback or automatic replication.

## Backtesting / Evolution

Historical datasets are real/immutable/SHA-256 identified and source-fingerprinted. Signal on candle `t` executes no earlier than `t+1`. Evolution remains evidence-gated and manual. Never tune S1-S4 merely to improve observed scores.

## Live isolation

No active route/service may place a real exchange order. Do not introduce exchange credentials into Paper Runtime or Research. Live requires a future separate adapter and explicit authorization.

## Evidence discipline

Never merge historical/Backtest/Paper/Live evidence silently. Fixture tests prove software behavior, not trading performance. A Research PASS/PROMOTED label is not a profitability, safety or Live-readiness claim.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report green status without fresh exact-HEAD output. Real Research evidence additionally requires observed historical Backtests and completed forward Paper sessions.
