# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable Paper Trading platform: **real market data, virtual capital, deterministic accounting, explicit risk and reproducible evidence**.

This file tracks implementation order. Domain requirements live in the linked documents under `docs/`.

## Current baseline

- FastAPI + SQLModel + SQLite are the active backend/persistence baseline.
- React/Vite frontend uses the active agents/trades/crypto APIs.
- Agent strategies S1-S4 exist as baseline strategy code; this does not prove profitability.
- Historical Mongo/Paper/TradingEngine code is not mounted by `app.main`.
- Normal application startup no longer starts the synthetic `AgentEngine`.
- `/health` and `/api/estado` explicitly report transition mode, synthetic engine disabled and Paper not implemented.
- Pre-provenance trade history is quarantined as `legacy_unclassified` and excluded from verified ROI/PnL/Win Rate/trade metrics.
- Manual simulated-PnL mutation is removed from the active API/UI.
- Agent funding increases funded and current capital together, so deposits do not manufacture profit.
- A provider-neutral, real-only market-data boundary is mounted at `/api/market-data`.
- `BinancePublicMarketDataProvider` uses public read-only Binance REST endpoints without credentials or execution capability.
- Quotes/candles carry UTC timestamps and provider provenance; stale/gapped/malformed data fails closed with no synthetic fallback.
- Fresh full test/build execution is still required on an available execution environment for the resulting HEAD.

## Ordered implementation program

### 0. Transition safety
- [x] Stabilize active SQLModel contracts and remove fake UI telemetry.
- [x] Define S4 explicitly and prevent silent strategy fallback.
- [x] Rebuild documentation around real-data Paper Trading.
- [x] Remove synthetic AgentEngine from normal application startup.
- [x] Remove manual PnL fabrication from the active agents API/UI.
- [x] Quarantine pre-provenance trades from verified financial metrics.
- [x] Make runtime/health state explicitly identify transition mode and synthetic isolation.
- [x] Prevent deposits from being counted as profit.
- [ ] Obtain fresh backend/frontend/build execution evidence on the exact resulting HEAD.

**Phase 0 code gate:** statically complete. Execution certification remains pending until the repository commands below run on the same HEAD.

### 1. Market Data
See `docs/MARKET_DATA.md`.
- [x] Define provider-neutral `Quote`, `Candle` and `MarketDataService` contracts.
- [x] Implement a public, read-only Binance real quote/candle provider without trading credentials.
- [x] Normalize BASE/USDT symbols and UTC timestamps at the boundary.
- [x] Reject stale/future quotes, open candles, gaps and out-of-order candle series.
- [x] Add bounded retry handling for transport errors, HTTP 429 and provider 5xx responses.
- [x] Guarantee fail-closed behavior: no generated fallback in the new real-data path.
- [x] Mount diagnostic/consumer endpoints under `/api/market-data`.
- [x] Keep legacy `BinanceService` unmounted; its mock fallback is not part of the new contract.
- [x] Author deterministic parsing, quality and API regression tests.
- [ ] Execute the authored tests and repository gate on the exact Phase 1 HEAD.

**Phase 1 source gate:** complete by static review. Phase 1 is not execution-certified until the validation gate below is observed green on the same HEAD.

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
- [ ] Ensure no random trade-closing behavior is reachable from Paper.

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
- [ ] Define evidence-aware fitness/automatic-replication criteria.
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

A checker, static review or historical report is not a substitute for fresh execution evidence.
