# QWEN.md — AUTOMATON Project Contract

Use `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md` as product truth. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

AUTOMATON targets autonomous Paper Trading on **real market data with virtual capital**, supported by reproducible evidence, explicit Risk/recovery gates and disciplined Strategy Research.

## Current state

- FastAPI + SQLModel + SQLite; React/Vite.
- Phases 1–6 remain Market Data, Accounting, deterministic Paper, Risk, Backtesting and Agent Evolution boundaries.
- Phase 7 persistent autonomous Paper Runtime is session-controlled.
- Phase 8 Strategy Research is an evidence/classification capability.
- Phase 9 physically removed the superseded Mongo/mock/trading architecture, including the old Synthetic AgentEngine and mock-fallback BinanceService.
- Runtime: `paper_trading=autonomous_phase_7`, `paper_runtime=runtime_phase_7`, `automated_trading=paper_enabled_phase_7`, `agent_evolution=evidence_phase_6`, `strategy_research=evidence_phase_8`, `legacy_pruning=pruned_phase_9`, `live_execution=disabled`.

Booting the app does not start/resume Paper sessions. Promoting a Research candidate does not deploy it automatically.

## Evidence/mode separation

Backtest, Paper and any future Live execution are distinct. Never fabricate or merge market data, fills, PnL or evidence across boundaries. Pre-provenance `Trade` rows are retained only as `legacy_unclassified` historical inspection and are not valid evidence.

## Phase 7 Paper Runtime

`backend/app/paper_runtime/` orchestrates:

`new real closed candle -> S1-S4 -> intent -> Risk -> PaperExecution(strategy_runtime) -> Accounting -> runtime evidence`.

Persistent session/cycle state is authoritative. One candle is evaluated once per session/agent. Risk is mandatory. No generated fallback, automatic replication or restart auto-resume.

## Phase 8 Strategy Research

`backend/app/strategy_research/` evaluates evidence without executing trades or modifying strategies.

Research links comparable completed Backtests in chronological repeating `TRAIN -> VALIDATION -> OOS` folds, then requires fingerprinted STOPPED Phase 7 forward Paper evidence. Promotion always creates a fresh evaluation and rechecks source identity.

A promoted candidate is an evidence classification only. It does not imply profitability, mutate S1-S4, auto-deploy to runtime, replicate agents or grant Live eligibility.

## Phase 9 pruning

Do not recreate deleted Mongo services/config/dependencies, old simulation/Paper/trading/risk engines, legacy auth/chat/payments API, mock market fallbacks, old Alpha/Beta/Gamma executables or unreachable frontend pages as shortcuts. Historical ideas may be reintroduced only as explicitly versioned new work through the current evidence architecture.

`backend/app/services/` intentionally contains only the S1-S4 strategy module plus package initializer. `models/enums.py` remains because active SQLModel models use its enums; that is not evidence of the deleted model stack.

## Backtesting / Evolution

Backtest data remains real, immutable and source-fingerprinted with next-candle execution. Evolution fitness/replication remain separate and manual. Do not change strategy thresholds merely to improve evaluated results.

## Live isolation

No Live adapter or real-order route is active. Research/Runtime must never import exchange credentials. Live requires a future separate adapter and explicit authorization.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never claim verification without fresh exact-HEAD execution.
