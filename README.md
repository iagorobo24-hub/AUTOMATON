# AUTOMATON

AUTOMATON is a local platform for developing, testing and evaluating autonomous crypto-trading agents.

## Product contract

The current product target is **autonomous Paper Trading with real market data and virtual capital**, supported by reproducible historical evidence, explicit Risk and evidence-aware agent lifecycle. Synthetic/Test, Backtest, Paper and Live remain separate evidence modes.

## Current runtime

Active stack: FastAPI + SQLModel + SQLite with React/Vite.

- Synthetic `AgentEngine`: disabled from normal startup.
- Market Data: real-only, provider-neutral and fail-closed.
- Accounting: authoritative long-only financial source for active Paper state.
- Paper Execution: deterministic MARKET execution with manual `operator` and controlled `strategy_runtime` origins.
- Risk: persistent mandatory `risk-v1` authorization before every normal Paper execution.
- Backtesting: immutable real historical datasets, deterministic `backtest-v1` and strategy-source SHA-256 evidence.
- Agent Evolution: `evolution-v1` fitness, lineage/lifecycle evidence and manual non-duplicating replication.
- Paper Runtime: persistent `runtime-v1` sessions that can execute S1-S4 autonomously on new real closed candles.
- Automated trading: enabled **only inside explicitly started Phase 7 Paper sessions**.
- Live execution: disabled and structurally separate.

Legacy pre-provenance `Trade` rows remain excluded from valid Paper/Backtest/fitness evidence.

## Implemented core

### Phases 1–6

Market Data, Accounting, deterministic Paper Execution, Risk, reproducible Backtesting and evidence-aware Agent Evolution are implemented as separate domains. S1-S4 remain unchanged baseline algorithms; no performance claim is implied by infrastructure completion.

### Phase 7 — 24/7 Paper Operation

`backend/app/paper_runtime/` adds a durable orchestration boundary:

```text
real closed candle -> S1-S4 -> intent -> Risk -> Paper Execution -> Accounting
```

`runtime-v1` contracts:

- session states: `CREATED`, `RUNNING`, `PAUSED`, `DEGRADED`, `RECOVERY_REQUIRED`, `STOPPED`;
- one durable cycle per `(session, agent, candle close)`;
- same candle cannot create a second action;
- HOLD persists evidence without an order;
- BUY while flat targets 25% of available cash and accounts for `paper-v1` compounded cost;
- BUY while already long is a no-op;
- SELL closes the current long; SELL while flat is a no-op;
- each autonomous action gets a deterministic `runtime:` request id;
- every execution still requires current real Market Data and a persisted Risk ALLOW;
- Paper origin is `strategy_runtime` and financial mutation still goes only through Accounting;
- provider failures never fall back to synthetic data;
- repeated operational failures can mark a session `DEGRADED`;
- financial ambiguity produces `RECOVERY_REQUIRED`;
- process restart never silently resumes a previous RUNNING session;
- startup reconciles interrupted Paper/runtime evidence without re-submitting an uncertain order;
- a session in recovery keeps ownership of its agent until explicitly recovered or stopped;
- automatic replication remains disabled.

The in-process asyncio scheduler is only the live worker. SQLite session/cycle/request/execution state is authoritative.

## Active APIs

In addition to Market Data, Accounting, Risk, Paper, Backtest and Evolution APIs, Phase 7 adds:

- `GET /api/runtime/status`
- `POST /api/runtime/sessions`
- `GET /api/runtime/sessions`
- `GET /api/runtime/sessions/{id}`
- `GET /api/runtime/sessions/{id}/cycles`
- `POST /api/runtime/sessions/{id}/start`
- `POST /api/runtime/sessions/{id}/pause`
- `POST /api/runtime/sessions/{id}/resume`
- `POST /api/runtime/sessions/{id}/recover`
- `POST /api/runtime/sessions/{id}/stop`

There is no Live execution endpoint, auto-replication endpoint or Backtest optimizer.

## Runtime identifiers

Current backend reports:

- `paper_trading=autonomous_phase_7`
- `paper_runtime=runtime_phase_7`
- `automated_trading=paper_enabled_phase_7`
- `agent_evolution=evidence_phase_6`
- `live_execution=disabled`

This means autonomous **Paper capability exists when an operator explicitly starts a session**. Startup itself does not begin trading or resume interrupted sessions.

## Development order

real market data → accounting → paper execution → risk → backtesting/evidence → agent evolution → 24/7 Paper → **strategy research** → legacy pruning → live-readiness.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Source/static gates are not runtime certification. Phase 7 operational certification additionally requires a sustained real-provider Paper session. Never claim strategy profitability, fitness quality or a green repository without fresh exact-HEAD evidence.
