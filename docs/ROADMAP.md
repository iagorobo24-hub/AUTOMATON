# AUTOMATON Roadmap

This roadmap defines dependency order. Source/static closure and executable certification are intentionally separate.

## Phases 0–4

Transition safety, Real Market Data, Accounting, deterministic Paper and Risk source contracts are implemented. Fresh exact-HEAD executable certification remains cross-phase debt.

## Phase 5 — Backtesting & Evidence

Immutable real historical snapshots, canonical dataset/source SHA-256, next-candle deterministic execution, isolated financial evidence and metrics are implemented.

**Status:** source/contract/static gate satisfied. Exact-HEAD execution and observed real-provider S1-S4 baseline remain pending; no performance numbers are inferred.

## Phase 6 — Agent Evolution

`evolution-v1` implements evidence-aware fitness, lineage/lifecycle and manual child replication with conserving Accounting transfer. Current-source Backtest provenance, agent-specific PaperExecution evidence and recovery/integrity gates are mandatory.

**Status:** source/contract/static gate satisfied. Execution certification remains pending.

## Phase 7 — 24/7 Paper Operation

**Goal:** operate S1-S4 autonomously against real current market data with virtual capital while preserving Risk, Accounting, idempotency and restart safety.

Implemented in source:

- additive persistent `PaperRuntimeSession`, `PaperRuntimeAgent`, `PaperRuntimeCycle`, `PaperRuntimeEvent`;
- `runtime-v1` lifecycle: CREATED/RUNNING/PAUSED/DEGRADED/RECOVERY_REQUIRED/STOPPED;
- explicit operator start/pause/resume/recover/stop controls;
- Market Data contract validation for session symbol/timeframe before persistence;
- persistent ownership preventing overlapping agent/symbol/interval sessions, including recovery states;
- one evaluation per real closed candle per session/agent;
- unchanged S1-S4 strategies;
- HOLD/already-long/already-flat no-action evidence;
- BUY sizing from 25% available cash with exact Paper cost reserve; full-position SELL;
- deterministic `runtime:` request IDs;
- autonomous path `Market Data -> Strategy -> Risk -> PaperExecution(strategy_runtime) -> Accounting`;
- Risk remains mandatory and unsupported Paper origins fail closed;
- in-process asyncio scheduler with SQLite as authority;
- scheduler controls execute on an active event loop, not a FastAPI sync worker thread;
- heartbeat, cycle outcome, failure counters and persistent events;
- no synthetic fallback; repeated operational failures can mark DEGRADED;
- financial ambiguity marks RECOVERY_REQUIRED;
- startup reconciles interrupted runtime intents without submitting new orders;
- prior RUNNING/DEGRADED sessions become RECOVERY_REQUIRED after restart and never auto-resume;
- start/recovery is blocked while attached Paper requests/executions remain ambiguous;
- `/api/runtime` controls and Ops Monitor/Settings/Dashboard observability;
- no automatic replication, optimizer or Live adapter.

Current runtime identifiers:

- `paper_trading=autonomous_phase_7`
- `paper_runtime=runtime_phase_7`
- `automated_trading=paper_enabled_phase_7`
- `live_execution=disabled`

**Exit condition:** an explicitly started Paper session can evaluate each new real closed candle once, route every actionable signal through Risk/Paper/Accounting, survive polling/retry ambiguity without double execution, and fail closed across restart/recovery.

**Status:** source/contract/static gate satisfied. Fresh backend/frontend/build execution and a sustained real-provider Paper run remain required for operational certification; the current tool environment still fails before test execution because it cannot resolve `github.com`.

## Phase 8 — Strategy Research

Use Phase 5 historical evidence plus Phase 7 forward Paper evidence to evaluate and revise strategies. Establish out-of-sample/walk-forward discipline, fixed cost assumptions and configuration/source versioning before promotion.

## Phase 9 — Legacy Pruning

Remove obsolete Mongo/trading/synthetic services, dead pages/config/dependencies and historical shortcuts only after reference/dependency audits prove no active recovery/evidence path depends on them.

## Phase 10 — Live Readiness

Design a structurally separate exchange adapter, secrets/permissions, exchange constraints, reconciliation, emergency controls and staged rollout. Real-capital activation remains a separate explicit authorization.

## Cross-phase certification debt

Fresh exact-HEAD backend tests, frontend tests/build and relevant real-provider smoke evidence are still required. Static closure must never be reported as a green runtime gate.
