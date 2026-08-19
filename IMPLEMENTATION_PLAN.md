# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable autonomous Paper Trading platform: **real market data, virtual capital, deterministic accounting/execution, explicit risk, reproducible evidence and evidence-aware agent lifecycle**.

## Current baseline

- FastAPI + SQLModel + SQLite are active.
- React/Vite is active.
- Legacy Mongo/Paper/TradingEngine code is unmounted.
- Synthetic `AgentEngine` is disabled in normal runtime.
- Phase 1 Market Data is real-only and fail-closed.
- Phase 2 Accounting is authoritative for Paper financial state.
- Phase 3 Paper Execution is deterministic/idempotent and operator-only.
- Phase 4 Risk is mandatory before normal Paper financial mutation.
- Phase 5 Backtesting provides immutable historical evidence and strategy-source fingerprints.
- Phase 6 Agent Evolution provides versioned fitness, lineage/lifecycle evidence and non-duplicating manual replication.
- Automated strategy/agent execution remains disabled until Phase 7.
- Live execution remains disabled.
- Fresh exact-HEAD execution evidence remains required.

## Ordered implementation program

### 0. Transition safety
- [x] Stabilize SQLModel contracts and remove fake telemetry.
- [x] Define S4 and prevent silent strategy fallback.
- [x] Remove synthetic runtime contamination and simulated-PnL mutation.
- [x] Quarantine legacy trade evidence and preserve funding/PnL separation.
- [ ] Obtain fresh backend/frontend/build execution evidence on exact HEAD.

**Phase 0 source gate:** complete. Execution certification pending.

### 1. Market Data
See `docs/MARKET_DATA.md`.
- [x] Provider-neutral Quote/Candle contracts.
- [x] Public read-only real Binance provider.
- [x] UTC/provenance/symbol normalization.
- [x] Stale/future/gap/order validation and bounded retries.
- [x] Fail closed with no generated fallback.
- [ ] Execute exact-HEAD validation gate.

**Phase 1 source gate:** complete. Execution certification pending.

### 2. Portfolio & Accounting
See `docs/PORTFOLIO_ACCOUNTING.md`.
- [x] Account, Order, Fill, Position and LedgerEntry persistence.
- [x] Long-only cash/cost/PnL/fee/equity/exposure invariants.
- [x] Funding separate from PnL and safe legacy bootstrap.
- [x] Reconciliation/restart contracts.
- [x] Add funded-liquid parent→child transfer without money duplication.
- [ ] Execute exact-HEAD validation gate.

**Phase 2 source gate:** complete; Phase 6 extends it with capital transfer. Execution certification pending.

### 3. Paper Execution
See `docs/PAPER_TRADING.md`.
- [x] Persistent execution provenance.
- [x] Operator-only MARKET BUY/SELL against real Quote data.
- [x] `paper-v1`: full fill/reject, adverse slippage and fee.
- [x] Request-id idempotency and conservative recovery.
- [x] Every accepted fill flows through Accounting.
- [ ] Execute exact-HEAD validation and real-provider smoke.

**Phase 3 source gate:** complete. Execution certification pending.

### 4. Risk Engine
See `docs/RISK_MANAGEMENT.md`.
- [x] Versioned RiskProfile/RiskDecision.
- [x] Size/exposure/concentration/open-position/loss/drawdown gates.
- [x] Market-data, agent, currency, Accounting and recovery integrity.
- [x] Safe risk-reducing SELL semantics and circuit breaker.
- [x] One-time current-profile ALLOW before normal Paper execution.
- [x] Complete exact-HEAD static audit.
- [ ] Execute Risk/Paper tests and real-provider virtual-capital smoke.

**Phase 4 source/contract/static gate:** complete. Execution certification pending.

### 5. Backtesting & Evidence
See `docs/BACKTESTING.md` and `docs/METRICS_AND_EVIDENCE.md`.
- [x] Immutable real historical datasets with canonical SHA-256.
- [x] Historical public provider with no synthetic fallback.
- [x] UTC/data-quality controls.
- [x] Isolated deterministic `backtest-v1` with next-candle execution and explicit costs.
- [x] Persist run/trade/equity/evidence records and strategy source SHA-256.
- [x] Metrics with undefined values preserved as null.
- [x] Interrupted-run invalidation and Paper-state isolation.
- [x] `/api/backtests` surfaces, no optimizer/Live capability.
- [x] S1-S4 unchanged.
- [x] Exact-HEAD static audit.
- [ ] Execute exact-HEAD tests/build.
- [ ] Observe one real historical S1-S4 baseline under identical assumptions.

**Phase 5 source/contract/static gate:** complete. Execution certification and real S1-S4 baseline pending.

### 6. Agent Evolution
See `docs/AGENT_LIFECYCLE.md`.
- [x] Add `EvolutionPolicy`, `AgentFitnessEvaluation`, `AgentLineage`, `AgentLifecycleEvent` as additive SQLite-compatible records.
- [x] Bootstrap versioned `evolution-v1` and pre-Phase-6 lifecycle baselines idempotently.
- [x] Require fresh fitness evaluation on every replication attempt.
- [x] Require active agent and matching completed Backtest evidence.
- [x] Require the Backtest strategy source SHA-256 to match current active strategy source.
- [x] Require minimum Backtest round trips, positive return/expectancy and bounded drawdown.
- [x] Require agent-specific `PaperExecution` closing evidence and positive authoritative Paper realized PnL.
- [x] Reject Accounting integrity drift and `RECOVERY_REQUIRED` Paper state.
- [x] Exclude legacy Trade rows and unprovenanced Paper-labelled fills.
- [x] Implement child allocation from funded liquid parent capital, excluding reserved cash.
- [x] Conserve parent+child cash/funded capital with paired transfer ledger entries.
- [x] Keep child flat and inherit strategy without mutation.
- [x] Persist parent/child/generation/configuration lineage and explicit lifecycle reasons.
- [x] Keep parent ACTIVE; treat replication as evidence/event rather than execution state.
- [x] Expose `/api/evolution` policy/fitness/lineage surfaces and evidence-gated manual `/api/agents/{id}/replicate`.
- [x] Update runtime/client/Agents/Settings for `agent_evolution=evidence_phase_6` while auto trading remains blocked until Phase 7.
- [ ] Complete final exact-HEAD static audit and reconcile documentation drift.
- [ ] Execute targeted/full backend/frontend/build gate on exact Phase 6 HEAD.

**Phase 6 source implementation:** present; final static closure and execution certification are separate gates.

### 7. 24/7 Paper Operation
- [ ] Define durable run/session identity and single active-loop ownership.
- [ ] Connect Strategy Intent -> Risk -> Paper -> Accounting under a controlled autonomous scheduler.
- [ ] Add restart/recovery/reconciliation, provider resilience, rate-limit/backoff and operational health.
- [ ] Add structured observability and long-running Paper session controls.
- [ ] Run sustained forward Paper experiments; capital remains virtual.

### 8. Strategy Research
See `docs/STRATEGIES.md`.
- [ ] Establish research/validation and walk-forward/out-of-sample methodology.
- [ ] Evaluate S1-S4 observed baseline plus revised/legacy hypotheses.
- [ ] Version every parameter/config change and compare identical datasets/costs.
- [ ] Promote only reproducibly useful strategies after forward Paper evidence.

### 9. Legacy Pruning
See `docs/LEGACY_AUDIT.md`.
- [ ] Re-audit references/dependencies and identify concepts still needed.
- [ ] Remove obsolete Mongo, old engines, mock fallbacks, pages/config/dependencies only after migration.
- [ ] Re-run repository/API/import/documentation audits after deletion.

### 10. Live Readiness
See `docs/LIVE_TRADING_GATE.md`.
- [ ] Design a separate Live execution adapter; never toggle Paper into Live.
- [ ] Implement secrets/permissions, exchange constraints, idempotency and reconciliation.
- [ ] Implement emergency stop, capital/position limits and staged rollout controls.
- [ ] Require explicit authorization before any real-capital activation.

## Validation gate

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Static review is not a substitute for fresh execution evidence. Backtest or fitness labels are not profitability evidence by themselves.
