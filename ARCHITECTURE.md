# AUTOMATON Architecture

## Objective

AUTOMATON researches autonomous crypto-trading agents using **real market data and virtual capital** until explicit evidence/safety gates justify any future Live mode.

## Non-negotiable boundaries

1. Synthetic data is test-only and explicitly labelled.
2. Backtest and Paper use real market data and virtual capital.
3. Live is a separate future execution adapter.
4. Evidence preserves mode/provenance.
5. SQLModel/SQLite is the active persistence baseline.
6. Accounting is the only active Paper financial authority.
7. Every normal Paper execution requires a persisted current-profile Risk ALLOW.
8. Backtest state is isolated from Paper and uses next-candle execution.
9. Replication transfers rather than duplicates funded liquid capital.
10. Phase 7 autonomous trading exists only inside explicitly started Paper runtime sessions.
11. Runtime restart never silently resumes an interrupted session or uncertain order.
12. Phase 7 does not enable Live, auto-replication, strategy mutation or optimization.

## Active domains

### Market Data — Phase 1

`backend/app/market_data/` owns real current Quote/Candle contracts, provenance and quality controls. Historical Backtest access remains a separate read-only provider.

### Strategy — baseline S1-S4

`backend/app/services/strategies.py` remains unchanged baseline logic. Phase 7 consumes close-price history from real closed candles; the runtime does not tune strategy thresholds.

### Risk — Phase 4

`backend/app/risk/` remains the authorization layer for both manual and autonomous Paper orders. Risk does not execute orders.

### Paper Execution — Phases 3, 4 and 7

`backend/app/paper_execution/` accepts two controlled origins:

- `operator`: explicit manual API command;
- `strategy_runtime`: Phase 7 session orchestration.

Both require the same real Quote, persisted one-time Risk ALLOW, deterministic `paper-v1` execution and Accounting mutation. Unknown origins are rejected. There is no Live exchange adapter.

### Portfolio & Accounting — Phase 2

`backend/app/accounting/` owns Account, Order, Fill, Position and LedgerEntry. Funding is separate from PnL. Phase 6 capital transfer also uses this authority.

### Backtesting — Phase 5

`backend/app/backtesting/` owns immutable historical datasets and deterministic isolated evidence. It never mutates active Paper state.

### Agent Evolution — Phase 6

`backend/app/agent_evolution/` owns evidence-aware fitness, lineage and manual replication. Replication remains manual in Phase 7; runtime cycles cannot auto-replicate agents.

### Paper Runtime — Phase 7

`backend/app/paper_runtime/` owns durable autonomous Paper session orchestration.

Persistent records:

- `PaperRuntimeSession`: session identity, market/timeframe, status, heartbeat and operational failure state;
- `PaperRuntimeAgent`: agent attachment plus last processed candle/signal/outcome;
- `PaperRuntimeCycle`: unique `(session, agent, candle close)` evaluation evidence and links to Risk/Paper;
- `PaperRuntimeEvent`: lifecycle/recovery/operational events.

The live worker is an in-process asyncio scheduler. It is **not** authoritative: SQLite state is. The local/single-process baseline prevents two tasks in the current process for one session, while persistent ownership rules reject conflicting sessions for the same agent/symbol/interval.

#### `runtime-v1` loop

```text
new real closed candle
        ↓
S1-S4 close-price history
        ↓
BUY / SELL / HOLD
        ↓
position-aware intent
        ↓
real current quote + marks
        ↓
RiskDecision
        ↓
PaperExecution(origin=strategy_runtime)
        ↓
Accounting
        ↓
PaperRuntimeCycle evidence
```

Rules:

- a candle is evaluated once per session/agent;
- HOLD creates no order;
- BUY while long creates no order;
- BUY while flat targets 25% of available cash, reserving exact `paper-v1` compounded cost;
- SELL while long requests the full current position;
- SELL while flat creates no order;
- request id derives deterministically from runtime/session/agent/symbol/candle/signal;
- replay cannot duplicate an execution.

#### Resilience and recovery

Operational provider/data failures do not fabricate observations. Repeated failures increment a persistent counter and can move a session to `DEGRADED`.

Financial ambiguity moves the session to `RECOVERY_REQUIRED`. Start/recover also fail closed while any attached account has unresolved `PaperRequest` or `PaperExecution` recovery state.

Startup ordering includes Paper recovery, then reconciliation of interrupted runtime cycles **without submitting a new order**, then converts persisted RUNNING/DEGRADED sessions to `RECOVERY_REQUIRED`. No task is auto-spawned after restart.

## Active API/UI boundary

Phase 7 adds `/api/runtime/*` create/read/start/pause/resume/recover/stop/cycles surfaces. Ops Monitor displays runtime session heartbeat/failure state. Settings displays the current runtime contract.

No Live execution, auto-replication or optimizer endpoint exists.

## Current runtime

`backend/app/main.py` reports:

- `runtime_mode=transition`;
- `market_data=real_contract_available`;
- `accounting=authoritative_phase_2`;
- `risk=authoritative_phase_4`;
- `paper_trading=autonomous_phase_7`;
- `backtesting=evidence_phase_5`;
- `agent_evolution=evidence_phase_6`;
- `paper_runtime=runtime_phase_7`;
- `automated_trading=paper_enabled_phase_7`;
- `live_execution=disabled`.

`paper_enabled_phase_7` means autonomous Paper is available **inside an explicitly started session**; the application does not start trading merely because it boots.

## Verification

Static review establishes source/contract coherence only. Runtime correctness requires fresh exact-HEAD backend/frontend execution, and Phase 7 operational certification additionally requires a sustained real-provider Paper smoke with restart/recovery observation.
