# QWEN.md — AUTOMATON Project Contract

Use `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md` as product truth. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

AUTOMATON targets autonomous Paper Trading on **real market data with virtual capital**, supported by reproducible evidence, explicit Risk/recovery gates and disciplined Strategy Research.

## Current state

- FastAPI + SQLModel + SQLite; React/Vite.
- Synthetic AgentEngine disabled.
- Phases 1–6 remain Market Data, Accounting, deterministic Paper, Risk, Backtesting and Agent Evolution boundaries.
- Phase 7 persistent autonomous Paper Runtime is active as a session-controlled capability.
- Phase 8 Strategy Research is active as an evidence/classification capability.
- Runtime: `paper_trading=autonomous_phase_7`, `paper_runtime=runtime_phase_7`, `automated_trading=paper_enabled_phase_7`, `agent_evolution=evidence_phase_6`, `strategy_research=evidence_phase_8`, `live_execution=disabled`.

Booting the app does not start/resume Paper sessions. Promoting a Research candidate does not deploy it automatically.

## Mode separation

Synthetic/Test, Backtest, Paper and Live are distinct. Never fabricate or merge market data, fills, PnL or evidence across modes.

## Phase 7 Paper Runtime

`backend/app/paper_runtime/` orchestrates:

`new real closed candle -> S1-S4 -> intent -> Risk -> PaperExecution(strategy_runtime) -> Accounting -> runtime evidence`.

Persistent session/cycle state is authoritative. One candle is evaluated once per session/agent. Risk is mandatory. No synthetic fallback, automatic replication or restart auto-resume.

## Phase 8 Strategy Research

`backend/app/strategy_research/` evaluates evidence without executing trades or modifying strategies.

Research studies link completed Phase 5 Backtests in chronological repeating `TRAIN -> VALIDATION -> OOS` folds. The first window freezes strategy version/source SHA and execution/cost assumptions. Later windows must remain compatible on strategy source/config, market/timeframe, capital and historical risk profile.

`research-v1` gates VALIDATION/OOS sample size, return, expectancy, OOS drawdown, profit factor and relative degradation. Historical PASS alone is insufficient.

Forward evidence requires STOPPED Phase 7 sessions on the same market/timeframe, matching-strategy agents, runtime cycles, unique FILLED closing SELL executions with `origin=strategy_runtime`, positive account-level realized-PnL context and clean Paper recovery. Accounts contaminated by FILLED manual/non-runtime Paper execution are rejected because PnL attribution is ambiguous.

Promotion always creates a fresh evaluation and requires current source SHA to still equal the historical source SHA. At most one `StrategyCandidate` represents one exact strategy/version/source identity.

A promoted candidate is an evidence classification only. It does not imply profitability, mutate S1-S4, auto-deploy to runtime, replicate agents or grant Live eligibility.

## Backtesting / Evolution

Backtest data remains real, immutable and source-fingerprinted with next-candle execution. Evolution fitness/replication remain separate and manual. Do not change strategy thresholds merely to improve evaluated results.

## Live / legacy

No Live adapter or real-order route is active. Research/Runtime must never import exchange credentials. Mongo/old engines/mock fallbacks remain legacy and must not be reactivated as shortcuts.

## Evidence discipline

Fixture tests prove software behavior, not trading performance. Research PASS/PROMOTED cannot be reported as real strategy success without observed reproducible historical and forward evidence.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never claim verification without fresh exact-HEAD execution.
