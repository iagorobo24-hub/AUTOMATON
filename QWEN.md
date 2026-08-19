# QWEN.md — AUTOMATON Project Contract

Use `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md` as product truth. Inspect `backend/app/main.py` before claiming runtime status.

## Objective

AUTOMATON targets autonomous Paper Trading on **real market data with virtual capital**, supported by reproducible evidence and explicit Risk/evolution/recovery gates.

## Current state

- FastAPI + SQLModel + SQLite; React/Vite.
- Synthetic AgentEngine disabled.
- Phases 1–6 active as real Market Data, Accounting, deterministic Paper, Risk, Backtesting and Agent Evolution boundaries.
- Phase 7 persistent autonomous Paper Runtime is active as a capability.
- Runtime: `paper_trading=autonomous_phase_7`, `paper_runtime=runtime_phase_7`, `automated_trading=paper_enabled_phase_7`, `agent_evolution=evidence_phase_6`, `live_execution=disabled`.

Autonomous capability is session-controlled: booting the app does not start or resume a session.

## Mode separation

Synthetic/Test, Backtest, Paper and Live are distinct. Never fabricate or merge market data, fills, PnL or evidence across modes.

## Phase 7 Paper Runtime

`backend/app/paper_runtime/` orchestrates:

`new real closed candle -> S1-S4 -> intent -> Risk -> PaperExecution(strategy_runtime) -> Accounting -> runtime evidence`.

Rules:

- persistent session/cycle/event state is authoritative; asyncio task state is not;
- one evaluation per session/agent/candle;
- S1-S4 remain unchanged;
- HOLD and position guards create no Paper order;
- BUY targets 25% available cash with exact Paper cost reserve; SELL closes the current long;
- deterministic runtime request IDs prevent duplicate execution;
- every action requires real market data and persisted Risk ALLOW;
- no synthetic fallback;
- repeated operational failures may mark DEGRADED;
- financial ambiguity marks RECOVERY_REQUIRED;
- restart reconciliation never resubmits an uncertain order and never auto-resumes an interrupted session;
- start/recover is blocked by unresolved PaperRequest/PaperExecution recovery;
- automatic replication remains disabled.

## Backtesting / Evolution

Backtest data remains real, immutable and source-fingerprinted. Evolution fitness remains evidence-gated and replication remains manual with conserving Accounting transfer. Phase 7 does not change fitness thresholds or strategy code.

## Live / legacy

No Live adapter or real-order route is active. Phase 7 must never import exchange credentials. Mongo/old engines/mock fallbacks remain legacy and must not be reactivated as shortcuts.

## Evidence discipline

Fixture tests prove software behavior, not trading performance. Running autonomously does not prove a strategy is useful. No profitability/safety claim without observed reproducible evidence.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never claim verification without fresh exact-HEAD execution. Phase 7 operational certification additionally requires a sustained real-provider Paper runtime smoke including restart/recovery behavior.
