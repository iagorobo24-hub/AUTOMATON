# AUTOMATON

AUTOMATON is a local platform for developing, testing and evaluating autonomous crypto-trading agents.

## Product contract

The current product target is **autonomous Paper Trading with real market data and virtual capital**, supported by reproducible historical evidence, explicit Risk, evidence-aware agent lifecycle and disciplined Strategy Research. Backtest, Paper and any future Live mode remain separate evidence/execution boundaries.

## Current runtime

Active stack: FastAPI + SQLModel + SQLite with React/Vite.

- Market Data: real-only, provider-neutral and fail-closed.
- Accounting: authoritative long-only financial source for active Paper state.
- Paper Execution: deterministic MARKET execution with manual `operator` and controlled `strategy_runtime` origins.
- Risk: persistent mandatory `risk-v1` authorization before every normal Paper execution.
- Backtesting: immutable real historical datasets, deterministic `backtest-v1` and strategy-source SHA-256 evidence.
- Agent Evolution: `evolution-v1` fitness, lineage/lifecycle evidence and manual non-duplicating replication.
- Paper Runtime: persistent `runtime-v1` autonomous Paper sessions with recovery/idempotency and source provenance.
- Strategy Research: `research-v1` TRAIN/VALIDATION/OOS + forward Paper evidence and manual candidate promotion.
- Legacy pruning: `pruned_phase_9`; Mongo/mock/legacy trading engines are physically removed.
- Live Readiness: `readiness_phase_10`; separate `live-v1` policy, read-only disabled adapter, hard limits, reconciliation, emergency stop and readiness evidence.
- Real-capital execution: **disabled**.

A Phase 10 `ARCHITECTURE_READY` result is only a technical readiness classification. It does not authorize money, credentials, an exchange adapter or a real order.

## Phase 10 — Live Readiness

`backend/app/live_execution/` creates the future Live safety boundary without implementing Live trading.

Persistent records:

- `LivePolicy`
- `LiveReadinessEvaluation`
- `LiveOrderIntent`
- `LiveOrderRecord`
- `LiveFillRecord`
- `LiveReconciliation`
- `LiveCircuitBreakerEvent`
- `LiveEmergencyStop`

`live-v1` uses conservative readiness ceilings: $100 deployable capital, $25 maximum order notional, $50 symbol exposure, $100 portfolio exposure, $5 session-loss ceiling, 5% drawdown, three consecutive execution errors, 30-second stale-data limit and CANARY rollout at 10% with manual approval required. These are design ceilings, not authorized capital.

The Phase 10 adapter is `DisabledLiveAdapter`. It exposes only read/reconciliation capability metadata and **has no order-transmission method**. `/api/live/orders` does not exist and there is no API for writing exchange credentials.

Intent preparation is persistent and idempotent through deterministic `live:<sha256>` client ids. A prepared intent can be `PREPARED` or `BLOCKED`; Phase 10 cannot transmit it.

Reconciliation is fail-closed. Unexpected venue state produces `RECOVERY_REQUIRED` plus a circuit-breaker event. Resolution requires an explicit operator reason; later clean snapshots do not erase ambiguity automatically.

Emergency stop is persistent, blocks new Live intents and cannot be cleared while a reconciliation remains unresolved. It never auto-liquidates positions.

Readiness requires a promoted Research candidate with current matching source SHA, active unpaused Risk, clean Paper recovery, valid `live-v1` limits, no emergency stop, explicit CANARY/manual-approval policy and clean/resolved Live reconciliation. Every readiness evaluation keeps `real_capital_blocked=true`.

## Active Live Readiness API

- `GET /api/live/status`
- `GET /api/live/policy`
- `GET /api/live/readiness`
- `POST /api/live/readiness/evaluate`
- `POST /api/live/emergency-stop`
- `POST /api/live/emergency-stop/clear`
- `GET /api/live/reconciliations`
- `POST /api/live/reconciliations/{id}/resolve`

There is no executable Live-order route, credential-write route or real-capital activation endpoint.

## Runtime identifiers

Current backend reports:

- `paper_trading=autonomous_phase_7`
- `paper_runtime=runtime_phase_7`
- `automated_trading=paper_enabled_phase_7`
- `agent_evolution=evidence_phase_6`
- `strategy_research=evidence_phase_8`
- `legacy_pruning=pruned_phase_9`
- `live_execution=readiness_phase_10`
- `real_capital_execution=disabled`

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Source/static gates are not runtime certification. Research promotion is not a profitability guarantee, and Live Readiness is not authorization for real capital.