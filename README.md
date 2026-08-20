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
- Live Readiness: `readiness_phase_10`; separate `live-v1` policy, disabled adapter, hard limits, reconciliation, emergency stop and readiness evidence.
- Live execution: **disabled**.
- Real-capital execution: **disabled**.

A Phase 10 `ARCHITECTURE_READY` result is only a technical readiness classification. It does not authorize money, credentials, an exchange adapter or a real order.

## Phase 10 — Live Readiness

`backend/app/live_execution/` creates a future Live safety boundary without implementing Live trading.

Persistent records:

- `LivePolicy`
- `LiveReadinessEvaluation`
- `LiveOrderIntent`
- `LiveOrderRecord`
- `LiveFillRecord`
- `LiveReconciliation`
- `LiveCircuitBreakerEvent`
- `LiveEmergencyStop`

`live-v1` uses conservative absolute ceilings of $100 deployable capital, $25 order notional, $50 symbol exposure, $100 portfolio exposure, $5 session loss and 5% drawdown, plus three consecutive execution errors and a 30-second stale-data threshold. The current `CANARY` rollout fraction is 10%, so the effective prepared-intent deployable-capital ceiling is $10. These are design gates, not authorized capital.

The Phase 10 adapter is `DisabledLiveAdapter`. It has read/reconciliation methods only and **no order-transmission method**. `/api/live/orders`, buy/sell, activation and credential-write routes do not exist.

Future intent preparation is persistent and idempotent through deterministic `live:<sha256>` client ids. Market symbols are canonicalized before that identity is derived, so aliases such as `btc-usdt` and `BTC/USDT` cannot create two commands for the same source event. Phase 10 can persist `PREPARED`/`BLOCKED` intent evidence but cannot transmit it.

Readiness verifies the full Research chain (`Study PROMOTED -> Evaluation PASS -> Candidate PROMOTED`) plus matching strategy/version/source SHA, current source integrity, active Risk, clean Paper recovery, fail-closed Market Data, valid Live policy, emergency-stop state and clean Live reconciliation.

Reconciliation is fail-closed: any unexplained venue order, position, fill, trading-enabled adapter or impossible transmitted Live record creates `RECOVERY_REQUIRED` plus circuit-breaker evidence. Phase 10 provides no shortcut for converting ambiguous financial state to trusted state merely from an operator note.

Emergency-stop activation/clear is persistent and audited. It cannot be cleared while any Live reconciliation remains unresolved, and it never auto-liquidates positions.

## Active Live Readiness API

- `GET /api/live/status`
- `GET /api/live/policy`
- `GET /api/live/readiness`
- `POST /api/live/readiness/evaluate`
- `POST /api/live/emergency-stop`
- `POST /api/live/emergency-stop/clear`
- `GET /api/live/reconciliations`
- `POST /api/live/reconcile`

There is no executable Live-order route, credential-write route, manual recovery-resolution shortcut or real-capital activation endpoint.

## Runtime identifiers

Current backend reports:

- `paper_trading=autonomous_phase_7`
- `paper_runtime=runtime_phase_7`
- `automated_trading=paper_enabled_phase_7`
- `agent_evolution=evidence_phase_6`
- `strategy_research=evidence_phase_8`
- `legacy_pruning=pruned_phase_9`
- `live_readiness=readiness_phase_10`
- `live_adapter=disabled_adapter`
- `live_execution=disabled`
- `real_capital_execution=disabled`

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Source/static gates are not runtime certification. Research promotion is not a profitability guarantee, and Live Readiness is not authorization for real capital.
