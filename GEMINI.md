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
- Phase 3 deterministic Paper Execution.
- Phase 4 mandatory persistent Risk.
- Phase 5 isolated reproducible Backtesting.
- Phase 6 evidence-aware Agent Evolution.
- Phase 7 persistent autonomous Paper runtime.
- Runtime: `paper_trading=autonomous_phase_7`, `paper_runtime=runtime_phase_7`, `automated_trading=paper_enabled_phase_7`, `agent_evolution=evidence_phase_6`, `live_execution=disabled`.

`paper_enabled_phase_7` means only explicitly started Paper sessions may run strategy loops. Process startup never starts or resumes trading automatically.

## Active Paper architecture

Manual path:
`operator -> real Market Data -> Risk -> PaperExecution(origin=operator) -> Accounting`.

Autonomous Phase 7 path:
`new real closed candle -> S1-S4 -> intent -> current real Market Data -> Risk -> PaperExecution(origin=strategy_runtime) -> Accounting -> runtime cycle evidence`.

PaperExecution accepts only `operator` and `strategy_runtime`; both require persisted Risk ALLOW. No direct Accounting trading mutation is allowed from runtime orchestration.

## Paper Runtime rules

`backend/app/paper_runtime/` owns persistent session/cycle orchestration.

- SQLite session/cycle state is authoritative; asyncio tasks are process-local workers only.
- States: CREATED/RUNNING/PAUSED/DEGRADED/RECOVERY_REQUIRED/STOPPED.
- Evaluate one cycle per `(session, agent, closed candle)`.
- S1-S4 remain unchanged.
- HOLD/already-long/already-flat produce no order.
- Flat BUY targets 25% available cash with exact Paper cost reserve; SELL closes the current long.
- Runtime request id is deterministic from session/agent/symbol/candle/signal.
- No synthetic fallback.
- Repeated operational failures may DEGRADED the session.
- Financial ambiguity => RECOVERY_REQUIRED.
- Startup reconciles existing Paper/runtime state without re-submitting uncertain orders, then blocks interrupted sessions pending explicit recovery.
- Start/recover fail while PaperRequest/PaperExecution recovery is unresolved.
- A recovery-required session retains agent/symbol/interval ownership.
- No automatic agent replication or mutation.

## Accounting / Evolution

Accounting owns all active financial state. Funding is not profit; long-only remains defined scope. Phase 6 replication transfers funded liquid capital and never copies/mints balances. Fitness/lineage remain separate from Phase 7 scheduling.

## Backtesting

Historical datasets are real/immutable/SHA-256 identified and source-fingerprinted. Signal on candle `t` executes no earlier than `t+1`. Never tune S1-S4 to make evaluated results look better.

## Live isolation

No Phase 7 route or service may place a real exchange order. Do not introduce exchange credentials into Paper Runtime. Live requires the future separate adapter and explicit authorization.

## Evidence

Never merge Synthetic/Backtest/Paper/Live silently. Fixture tests prove software behavior, not trading performance. Autonomous operation does not prove strategy quality.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report green status without fresh exact-HEAD output. Phase 7 operational certification also requires a sustained real-provider Paper session including recovery observation.
