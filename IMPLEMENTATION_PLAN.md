# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable Paper Trading platform: **real market data, virtual capital, deterministic accounting, explicit risk and reproducible evidence**.

This file tracks implementation order. Domain requirements live in the linked documents under `docs/`.

## Current baseline

- FastAPI + SQLModel + SQLite are the active backend/persistence baseline.
- React/Vite is the active frontend.
- Agent strategies S1-S4 exist as baseline code; this does not prove profitability.
- Historical Mongo/Paper/TradingEngine code is not mounted by `app.main`.
- Normal startup does not start the synthetic `AgentEngine`.
- Pre-provenance `Trade` history remains `legacy_unclassified` and excluded from verified Paper metrics.
- Phase 1 real-only Market Data is mounted at `/api/market-data` and fails closed without synthetic fallback.
- Phase 2 Accounting is authoritative for new financial state: Account, Order, Fill, Position and LedgerEntry.
- Phase 3 Paper Execution is mounted at `/api/paper` and is operator-only.
- `paper-v1` uses real Quote input, MARKET full-fill-or-reject semantics, 10 bps adverse slippage and 10 bps fees.
- Paper mutations require persistent `request_id` idempotency and have conservative restart recovery.
- Ops Monitor reads PaperExecution provenance instead of treating legacy Trade rows as Paper.
- Automated strategy/agent execution is blocked until Phase 4 Risk exists.
- Live execution is disabled and no active Paper path can place a real exchange order.
- Replication remains blocked until Agent Evolution defines non-duplicating capital transfer.
- Fresh full test/build execution is still required on an available execution environment for the resulting HEAD.

## Ordered implementation program

### 0. Transition safety
- [x] Stabilize active SQLModel contracts and remove fake UI telemetry.
- [x] Define S4 explicitly and prevent silent strategy fallback.
- [x] Rebuild documentation around real-data Paper Trading.
- [x] Remove synthetic AgentEngine from normal application startup.
- [x] Remove manual PnL fabrication from active API/UI.
- [x] Quarantine pre-provenance trades from verified financial metrics.
- [x] Prevent deposits from being counted as profit.
- [ ] Obtain fresh backend/frontend/build execution evidence on the exact resulting HEAD.

**Phase 0 source gate:** complete. Execution certification remains pending.

### 1. Market Data
See `docs/MARKET_DATA.md`.
- [x] Provider-neutral `Quote`, `Candle` and `MarketDataService` contracts.
- [x] Public read-only Binance provider without trading credentials.
- [x] Symbol/UTC/provenance normalization.
- [x] Stale/future/gap/out-of-order validation.
- [x] Bounded retry/rate-limit handling.
- [x] Fail closed with no generated fallback.
- [x] Active `/api/market-data` boundary and deterministic tests authored.
- [ ] Execute authored tests and repository gate on exact HEAD.

**Phase 1 source gate:** complete. Execution certification remains pending.

### 2. Portfolio & Accounting
See `docs/PORTFOLIO_ACCOUNTING.md`.
- [x] SQLModel Account, Order, Fill, Position and LedgerEntry records.
- [x] Long-only cash/cost/PnL/fee/equity/exposure invariants.
- [x] Funding separate from PnL.
- [x] Additive buys, partial/full closes and fail-closed invalid mutations.
- [x] Restart/reload and reconciliation contracts/tests authored.
- [x] Safe bootstrap of historical agents excluding unverified current-balance PnL.
- [x] Agent creation/deposits use Accounting as authority.
- [x] Replication blocked until non-duplicating allocation exists.
- [x] Read-only accounting inspection API.
- [ ] Execute accounting/backend/frontend/build gates on exact HEAD.

**Phase 2 source gate:** complete. Execution certification remains pending.

### 3. Paper Execution
See `docs/PAPER_TRADING.md`.
- [x] Add persistent `PaperExecution` provenance linked to authoritative Order/Fill records.
- [x] Implement operator-only virtual MARKET BUY/SELL execution against Phase 1 real Quote data.
- [x] Define deterministic `paper-v1`: full fill or rejection, 10 bps adverse slippage, 10 bps fee.
- [x] Reject stale/future/mismatched quotes, inactive agents and account-currency mismatches.
- [x] Feed every accepted fill through Phase 2 `AccountingService`; no direct balance mutation.
- [x] Persist rejections and keep random open/close behavior unreachable.
- [x] Add persistent `PaperRequest` idempotency keyed by required `request_id`.
- [x] Make identical request replays return the same execution; conflicting payload reuse fails.
- [x] Treat provider failures as retryable only when no financial state exists.
- [x] Recover pending execution/request state on restart without blind re-execution.
- [x] Cancel definitely unfilled interrupted orders; mark ambiguous state `RECOVERY_REQUIRED` and block the account.
- [x] Mount `/api/paper/status`, `/api/paper/orders/market` and `/api/paper/executions`.
- [x] Update Ops Monitor/Settings to show truthful Paper provenance and automation/Live boundaries.
- [x] Keep strategy/agent automation blocked until Risk.
- [ ] Execute targeted Phase 3 tests plus repository backend/frontend/build gate on exact HEAD.
- [ ] Run an end-to-end smoke against the real provider with virtual capital and inspect persisted reconciliation.

**Phase 3 source/contract gate:** complete by static review. It is not execution-certified until both executable gates above are observed on the exact HEAD.

### 4. Risk
See `docs/RISK_MANAGEMENT.md`.
- [ ] Define independent risk request/decision contract before Paper Execution.
- [ ] Add position sizing, per-order/notional and total-exposure limits.
- [ ] Add loss/drawdown and stale-data/accounting-error circuit breakers.
- [ ] Persist risk profile/version and allow/reject reasons with evidence.
- [ ] Only after this gate, allow strategy/agent-originated orders to reach Paper Execution.

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
- [ ] Re-enable replication only after that accounting policy is implemented and tested.
- [ ] Persist lineage/configuration versions and retirement/death reasons.

### 7. 24/7 Paper
- [ ] Add run/session identity and operational health.
- [ ] Add sustained recovery/reconciliation procedures and monitoring.
- [ ] Run long-lived forward Paper experiments.

### 8. Strategy research
See `docs/STRATEGIES.md`.
- [ ] Audit Alpha/Beta/Gamma legacy ideas against new contracts.
- [ ] Re-implement only useful deterministic concepts.
- [ ] Validate richer strategies through backtest then Paper.

### 9. Legacy pruning
See `docs/LEGACY_AUDIT.md`.
- [ ] Delete legacy services after useful concepts have been migrated.
- [ ] Remove obsolete Mongo/config/dependencies/pages and re-audit references.

### 10. Live readiness
See `docs/LIVE_TRADING_GATE.md`.
- [ ] Design a separate Live execution adapter only after prior gates.
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
