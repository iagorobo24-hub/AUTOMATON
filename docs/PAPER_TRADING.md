# Paper Trading

## Definition

Paper Trading means **real market data + virtual capital + simulated execution**. It is forward validation, not a visual simulation and never Live execution.

## Current boundary

The active execution domain is `backend/app/paper_execution/`; Phase 7 adds persistent orchestration in `backend/app/paper_runtime/`.

Paper now supports two explicit origins:

- `operator`: manual `POST /api/paper/orders/market`;
- `strategy_runtime`: autonomous actions generated only by a started Phase 7 runtime session.

Both paths require:

- real provider-provenanced current Market Data;
- virtual capital;
- MARKET BUY/SELL only;
- persisted current-profile Risk ALLOW;
- deterministic `paper-v1` fill policy;
- Accounting as the only financial mutation path;
- request-id idempotency and fail-closed recovery.

Unknown execution origins are rejected. There are no exchange trading credentials or Live adapter.

## `paper-v1`

- full fill or rejection;
- maximum quote age 30 seconds;
- maximum future clock skew 5 seconds;
- BUY/SELL adverse slippage 10 bps;
- fee 10 bps of fill notional;
- long-only Accounting;
- account quote currency must match the market;
- agent must be active.

For BUY, the current compounded cost factor is `1.001 × 1.001 = 1.002001`.

## Risk gate

`PaperExecutionService` requires a persisted unconsumed Risk ALLOW matching account, symbol, side, quantity, provider, price and quote timestamp. The active Risk profile must still be enabled/not paused when the decision is consumed.

There is no low-level normal execution bypass without Risk. Recovery methods reconcile existing state; they do not submit new orders.

## Idempotency and recovery

Manual Paper commands require a caller-provided `request_id`. Phase 7 derives a deterministic runtime request id from session/agent/market/candle/signal.

Same logical request cannot produce a second fill. Ambiguous `PROCESSING`, missing linkage or partial financial state becomes `RECOVERY_REQUIRED` rather than automatic re-execution.

Startup recovery order relevant to Paper/runtime:

1. recover pending `PaperExecution`;
2. recover pending `PaperRequest`;
3. reconcile interrupted Phase 7 runtime cycles without submitting a new order;
4. mark previously RUNNING/DEGRADED runtime sessions `RECOVERY_REQUIRED`.

## Autonomous Phase 7 path

A started `runtime-v1` session evaluates each agent once per new real closed candle:

```text
closed candle -> S1-S4 -> intent -> current real quote -> Risk -> Paper -> Accounting
```

HOLD and position-guard no-actions create runtime cycle evidence without Paper orders. Autonomous BUY targets 25% of available cash while accounting for the compounded Paper cost. Autonomous SELL requests the full current long.

Provider failure never falls back to generated market data. Repeated operational failures may degrade a session; financial ambiguity blocks it in `RECOVERY_REQUIRED`.

## API/UI

Manual Paper:

- `GET /api/paper/status`
- `POST /api/paper/orders/market`
- `GET /api/paper/executions`

Persistent autonomous runtime:

- `/api/runtime/status`
- `/api/runtime/sessions*`
- `/api/runtime/sessions/{id}/start|pause|resume|recover|stop`

Ops Monitor exposes session heartbeat/failure state. Settings reports autonomous Paper as session-controlled.

## Isolation from Live

Phase 7 automates **Paper only**. No active route can send a real exchange order. Live requires the separate future adapter and gate in `LIVE_TRADING_GATE.md` plus explicit authorization.

## Certification

Source/static coherence is distinct from executable certification. Fresh exact-HEAD backend/frontend tests/build and a sustained real-provider Paper session are required before operational validation is claimed.
