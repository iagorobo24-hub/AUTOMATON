# AUTOMATON Implementation Plan

## Current program objective

Replace the transition simulator with a verifiable Paper Trading platform: **real market data, virtual capital, deterministic accounting, explicit risk and reproducible evidence**.

This file tracks implementation order. Domain requirements live in the linked documents under `docs/`.

## Current verified baseline

- FastAPI + SQLModel + SQLite are the active backend/persistence baseline.
- React/Vite frontend uses the active agents/trades/crypto APIs.
- Agent strategies S1-S4 exist as baseline strategy code; this does not prove profitability.
- Historical Mongo/Paper/TradingEngine code is not mounted by `app.main`.
- The current `AgentEngine` still uses synthetic market movement and therefore is not valid Paper Trading.
- Fresh full test/build execution is still required on an available execution environment for the current HEAD.

## Ordered implementation program

### 0. Transition safety
- [x] Stabilize active SQLModel contracts and remove fake UI telemetry.
- [x] Define S4 explicitly and prevent silent strategy fallback.
- [x] Rebuild documentation around real-data Paper Trading.
- [ ] Obtain fresh backend/frontend/build execution evidence on the exact current HEAD.
- [ ] Mark synthetic engine paths explicitly test-only before Paper replacement work lands.

### 1. Market Data
See `docs/MARKET_DATA.md`.
- [ ] Define provider-neutral market observation types.
- [ ] Implement real candle/current-price provider adapter.
- [ ] Add UTC, stale, gap, retry and parsing tests.
- [ ] Remove synthetic fallback from every Paper-capable path.

### 2. Portfolio & Accounting
See `docs/PORTFOLIO_ACCOUNTING.md`.
- [ ] Specify SQLModel order/fill/position/account records.
- [ ] Implement cash/equity/PnL/fees invariants.
- [ ] Add reconciliation and restart tests.
- [ ] Make financial metrics consume this single source of truth.

### 3. Paper Execution
See `docs/PAPER_TRADING.md`.
- [ ] Implement virtual order lifecycle against real observations.
- [ ] Define deterministic fill, fee, slippage and timeout rules.
- [ ] Persist open state and restore/reconcile after restart.
- [ ] Remove random trade-closing behavior from Paper.

### 4. Risk
See `docs/RISK_MANAGEMENT.md`.
- [ ] Add independent risk approval before execution.
- [ ] Add position/exposure/loss/drawdown controls.
- [ ] Add stale-data/accounting-error circuit breakers.
- [ ] Persist risk profile/version with evidence.

### 5. Backtesting & Evidence
See `docs/BACKTESTING.md` and `docs/METRICS_AND_EVIDENCE.md`.
- [ ] Build reproducible historical runner using real datasets.
- [ ] Add fees/slippage and bias controls.
- [ ] Evaluate S1-S4 baselines.
- [ ] Produce machine-readable run metadata and comparable reports.

### 6. Agent Lifecycle
See `docs/AGENT_LIFECYCLE.md`.
- [ ] Define evidence-aware fitness/replication criteria.
- [ ] Define child capital allocation without money duplication.
- [ ] Persist lineage/configuration versions.
- [ ] Add retirement/death reasons and lifecycle tests.

### 7. 24/7 Paper
- [ ] Add session/run identity and operational health.
- [ ] Add recovery and reconciliation procedures.
- [ ] Add monitoring for stale provider, engine errors and open financial state.
- [ ] Run sustained forward Paper experiments.

### 8. Strategy research
See `docs/STRATEGIES.md`.
- [ ] Audit legacy Alpha/Beta/Gamma code against the new contracts.
- [ ] Re-implement only useful deterministic concepts.
- [ ] Validate richer strategies by backtest then Paper.
- [ ] Reject unsupported historical performance claims.

### 9. Legacy pruning
See `docs/LEGACY_AUDIT.md`.
- [ ] Delete legacy services only after selected concepts have been migrated.
- [ ] Remove obsolete Mongo/config/dependencies/pages.
- [ ] Re-audit references, docs and dependencies.

### 10. Live readiness
See `docs/LIVE_TRADING_GATE.md`.
- [ ] Design separate Live execution adapter only after prior gates.
- [ ] Verify secrets, limits, emergency stop, reconciliation and staged rollout.
- [ ] Require explicit authorization before any real-capital activation.

## Validation gate

For code phases, closure requires relevant targeted tests plus the repository gate on the same HEAD:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

A checker or historical report is not a substitute for fresh evidence.
