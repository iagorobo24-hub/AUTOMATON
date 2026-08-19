# Phase 7 — 24/7 Paper Operation Design

## Goal

Introduce a durable autonomous Paper runtime that evaluates active S1-S4 agents on real closed market candles and routes every actionable intent through Risk, Paper Execution and Accounting using virtual capital only.

## Non-goals

- No Live adapter, credentials or real-capital execution.
- No Redis/Celery or distributed worker infrastructure.
- No automatic agent replication or strategy mutation.
- No changes to S1-S4 algorithms.
- No synthetic market-data fallback.
- No strategy optimization or profitability claims.

## Architecture

Create `backend/app/paper_runtime/` as an orchestration domain above existing Market Data, Strategy, Risk, Paper and Accounting boundaries.

Persist:

- `PaperRuntimeSession`: experiment/run identity and lifecycle.
- `PaperRuntimeAgent`: agents attached to a session and last processed candle.
- `PaperRuntimeCycle`: one durable evaluation result for `(session, agent, candle close)`.
- `PaperRuntimeEvent`: structured operational events and recovery reasons.

The in-process scheduler owns asyncio tasks only while the FastAPI process is alive. Persisted records remain the authority. Any session found RUNNING after restart becomes `RECOVERY_REQUIRED`; no old loop resumes silently.

## Session states

`CREATED`, `RUNNING`, `PAUSED`, `DEGRADED`, `RECOVERY_REQUIRED`, `STOPPED`.

Only `RUNNING` may evaluate new candles. `RECOVERY_REQUIRED` is fail-closed and requires explicit operator recovery before resume.

## Single ownership

At most one session may be RUNNING for the same `(agent_id, symbol, interval)` tuple. Starting a conflicting session fails closed.

The in-memory scheduler keeps one task per running session. Persistent state prevents duplicate execution after restart.

## Market cadence

For each configured agent:

1. request enough real closed candles from `MarketDataService.get_candles()`;
2. identify the newest closed candle;
3. compare its `close_time` with `PaperRuntimeAgent.last_candle_close`;
4. if unchanged, do nothing;
5. if new, persist one `PaperRuntimeCycle` keyed uniquely by `(session_id, agent_id, candle_close)`;
6. compute S1-S4 signal from candle closes through that candle.

A candle is evaluated at most once per session/agent, even if polling repeats or the process retries.

## Strategy and sizing

S1-S4 remain unchanged.

`runtime-v1`:

- HOLD → persist cycle as `NO_ACTION_HOLD`.
- BUY while already long → `NO_ACTION_ALREADY_LONG`.
- BUY while flat → target 25% of current available cash at the real quote; quantity is derived deterministically.
- SELL while long → request full current long quantity.
- SELL while flat → `NO_ACTION_ALREADY_FLAT`.

Risk remains authoritative and may reject any generated quantity.

## Paper execution

Autonomous actions use `origin="strategy_runtime"`.

Each actionable cycle derives a stable request id from:

`runtime-v1 | session_id | agent_id | symbol | candle_close | signal`

The same logical candle/signal can therefore never produce two Paper orders.

Normal execution remains:

`real Market Data -> RiskDecision -> PaperExecution -> Accounting`.

The runtime must not bypass Risk or call Accounting directly for trades.

## Provider resilience

Provider/quality failures never trigger synthetic fallback.

Cycle outcomes:

- transient unavailable → `SKIPPED_PROVIDER_UNAVAILABLE`;
- invalid/stale data → `SKIPPED_MARKET_DATA_INVALID`;
- Risk reject → `REJECTED_RISK`;
- Paper rejection → `REJECTED_PAPER`;
- successful fill → `FILLED`.

A session tracks consecutive failures. Default `runtime-v1` threshold is 5. Reaching the threshold marks session `DEGRADED`. Financial/recovery ambiguity marks `RECOVERY_REQUIRED` immediately.

## Recovery

Startup recovery:

1. find sessions persisted as RUNNING or DEGRADED;
2. inspect attached agents and Paper `RECOVERY_REQUIRED` requests;
3. mark those sessions `RECOVERY_REQUIRED` with a lifecycle event;
4. do not spawn tasks automatically.

Operator may explicitly recover a session only after no account has unresolved Paper recovery state. Recovery returns it to PAUSED, from which resume is explicit.

## Controls/API

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

No Live or auto-replication endpoint is introduced.

## Observability

Persist and expose:

- heartbeat;
- last cycle time;
- last candle close;
- last signal;
- cycle outcome;
- risk decision id;
- Paper execution id;
- consecutive failures;
- last error;
- session events.

Ops Monitor and Settings may display this state but must not claim profitability.

## Runtime contract

After Phase 7 source closure:

- `paper_trading=autonomous_phase_7`
- `paper_runtime=runtime_phase_7`
- `automated_trading=paper_enabled_phase_7`
- `agent_evolution=evidence_phase_6`
- `live_execution=disabled`

## Exit gate

Source/static closure requires regression contracts for session lifecycle, one-cycle-per-candle idempotency, BUY/SELL/HOLD behavior, Risk/Paper enforcement, restart recovery, provider failures, circuit breakers, inactive agents, no auto-replication and no Live capability.

Execution certification additionally requires fresh exact-HEAD backend tests, frontend tests/build and a sustained real-provider Paper smoke. Static closure is not a runtime green result.
