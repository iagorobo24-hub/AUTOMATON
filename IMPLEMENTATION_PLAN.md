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
- A provider-neutral, real-only market-data boundary is mounted at `/api/market-data`.
- `BinancePublicMarketDataProvider` uses public read-only Binance REST endpoints without credentials or execution capability.
- Quotes/candles carry UTC timestamps and provider provenance; stale/gapped/malformed data fails closed with no synthetic fallback.
- Phase 2 introduces authoritative SQLModel accounting records: Account, Order, Fill, Position and LedgerEntry.
- New agents receive an accounting account at creation; deposits are explicit ledger events and do not create PnL.
- Existing agents are bootstrapped from funded/initial capital only; legacy `presupuesto_actual` is not promoted because it may contain synthetic PnL.
- Manual replication is blocked until Agent Evolution defines a capital-transfer policy; the old behavior duplicated money.
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
- [x] Add SQLModel Account, Order, Fill, Position and LedgerEntry records.
- [x] Establish long-only accounting and reject implicit short/margin semantics.
- [x] Implement funded capital, cash, average cost, realized/unrealized PnL, fees, equity and exposure invariants.
- [x] Treat buy fees as acquisition cost and sell fees as net realized-PnL costs.
- [x] Support additive buys, partial closes and full closes without double-counting cash or PnL.
- [x] Reject insufficient cash, oversells, overfills and invalid timestamps before financial mutation.
- [x] Persist funding events separately from trading PnL.
- [x] Add reload/restart reconstruction tests using persisted SQLModel records.
- [x] Add reconciliation checks for equity identity, negative balances/positions, order/fill mismatches and orphan fills.
- [x] Bootstrap pre-Phase-2 agents from funded capital while discarding unverified legacy current-balance PnL.
- [x] Make new-agent creation/deposits use the accounting layer as financial authority while keeping legacy Agent budget fields only as compatibility mirrors.
- [x] Preserve financial balances when an agent lifecycle state changes to dead.
- [x] Block replication until a non-duplicating capital-allocation policy is implemented in Agent Evolution.
- [x] Mount a read-only `/api/accounting/agents/{agent_id}` inspection endpoint; no order/fill execution mutation is exposed in Phase 2.
- [ ] Execute the authored accounting/backend/frontend/build gates on the exact Phase 2 HEAD.

**Phase 2 source gate:** complete by static review. Accounting is not execution-certified until the validation gate below is observed green on the same HEAD.

### 3. Paper Execution
See `docs/PAPER_TRADING.md`.
- [ ] Implement virtual order lifecycle against real observations.
- [ ] Define deterministic fill, fee, slippage and timeout rules.
- [ ] Persist open state and restore/reconcile after restart.
- [ ] Ensure no random trade-closing behavior is reachable from Paper.
- [ ] Feed every accepted fill through the Phase 2 accounting service instead of mutating balances directly.

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
- [ ] Define explicit child capital transfer/allocation without money duplication.
- [ ] Re-enable manual/automatic replication only after that accounting policy is implemented and tested.
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
