# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable Paper Trading platform: **real market data, virtual capital, deterministic accounting, explicit risk and reproducible evidence**.

## Current baseline

- FastAPI + SQLModel + SQLite are the active backend/persistence baseline.
- React/Vite is the active frontend.
- Historical Mongo/Paper/TradingEngine code is not mounted by `app.main`.
- Synthetic `AgentEngine` is not started by normal runtime.
- Phase 1 Market Data is real-only and fail-closed.
- Phase 2 Accounting is authoritative for active Paper financial state.
- Phase 3 Paper Execution is operator-only, deterministic and idempotent.
- Phase 4 Risk is mandatory for normal Paper execution.
- Phase 5 Backtesting uses immutable real historical datasets, next-candle execution and isolated evidence records.
- Automated strategy/agent execution remains disabled.
- Live execution remains disabled.
- Fresh full test/build execution is still required for exact resulting HEADs.

## Ordered implementation program

### 0. Transition safety
- [x] Stabilize SQLModel contracts and remove fake telemetry.
- [x] Define S4 and prevent silent strategy fallback.
- [x] Remove synthetic runtime contamination and simulated-PnL mutation.
- [x] Quarantine legacy trade evidence and preserve funding/PnL separation.
- [ ] Obtain fresh backend/frontend/build execution evidence on exact HEAD.

**Phase 0 source gate:** complete. Execution certification remains pending.

### 1. Market Data
See `docs/MARKET_DATA.md`.
- [x] Provider-neutral Quote/Candle contracts.
- [x] Public read-only real Binance provider.
- [x] UTC/provenance/symbol normalization.
- [x] Stale/future/gap/order validation and bounded retries.
- [x] Fail closed with no generated fallback.
- [ ] Execute exact-HEAD validation gate.

**Phase 1 source gate:** complete. Execution certification remains pending.

### 2. Portfolio & Accounting
See `docs/PORTFOLIO_ACCOUNTING.md`.
- [x] Account, Order, Fill, Position and LedgerEntry persistence.
- [x] Long-only cash/cost/PnL/fee/equity/exposure invariants.
- [x] Funding separate from PnL and safe legacy bootstrap.
- [x] Reconciliation/restart contracts.
- [x] Replication blocked until non-duplicating allocation exists.
- [ ] Execute exact-HEAD validation gate.

**Phase 2 source gate:** complete. Execution certification remains pending.

### 3. Paper Execution
See `docs/PAPER_TRADING.md`.
- [x] Persistent PaperExecution provenance.
- [x] Operator-only MARKET BUY/SELL against real Quote data.
- [x] `paper-v1`: full fill/reject, 10 bps adverse slippage, 10 bps fee.
- [x] Persistent request-id idempotency.
- [x] Conservative restart/recovery and RECOVERY_REQUIRED handling.
- [x] Every accepted fill flows through Accounting.
- [x] Active `/api/paper` surface with no Live/automation endpoint.
- [ ] Execute exact-HEAD validation and real-provider smoke.

**Phase 3 source gate:** complete. Execution certification remains pending.

### 4. Risk Engine
See `docs/RISK_MANAGEMENT.md`.
- [x] Persist versioned RiskProfile/RiskDecision.
- [x] Implement order/equity/exposure/concentration/open-position/loss/drawdown gates.
- [x] Enforce market-data, agent, currency, Accounting and recovery integrity.
- [x] Preserve safe risk-reducing SELL semantics.
- [x] Add pause/resume circuit breaker.
- [x] Require one-time current-profile ALLOW before normal Paper execution.
- [x] Match BUY cash reserve to `paper-v1` compounded cost.
- [x] Complete exact-HEAD static audit.
- [ ] Execute Risk/Paper tests and real-provider virtual-capital smoke.

**Phase 4 source/contract/static gate:** complete. Execution certification remains pending.

### 5. Backtesting & Evidence
See `docs/BACKTESTING.md` and `docs/METRICS_AND_EVIDENCE.md`.
- [x] Add immutable `BacktestDataset` + `BacktestCandle` snapshots with canonical SHA-256.
- [x] Add read-only paginated historical Binance provider with no synthetic fallback.
- [x] Reject empty/gapped/duplicate/out-of-order/out-of-window historical data.
- [x] Preserve UTC semantics across SQLite persistence.
- [x] Add isolated long-only `BacktestLedger`; do not mutate Paper accounts/evidence.
- [x] Add deterministic `backtest-v1`: next-candle execution, no pyramiding, 10 bps adverse slippage, 10 bps fee, 25% default allocation.
- [x] Explicitly force-close final open positions with `DATASET_END_EXIT`.
- [x] Persist `BacktestRun`, `BacktestTrade` and `BacktestEquityPoint` evidence.
- [x] Compute return/PnL, round trips, win/loss, expectancy, profit factor where defined, drawdown, fees and exposure.
- [x] Keep undefined metrics null; no Sharpe convention invented.
- [x] Invalidate interrupted RUNNING backtests on restart.
- [x] Mount `/api/backtests` dataset/run/status/read surfaces with no optimizer/Live capability.
- [x] Keep S1-S4 algorithms unchanged and version them as `baseline-v1` evidence inputs.
- [x] Update Settings/client/docs for `backtesting=evidence_phase_5` without profitability claims.
- [ ] Execute targeted backtest tests plus full backend/frontend/build gate on exact Phase 5 HEAD.
- [ ] Run one real historical dataset through S1-S4 under identical `backtest-v1` assumptions and persist/report observed baseline results.

**Phase 5 source/contract implementation:** complete pending final exact-HEAD static audit. Execution certification and observed S1-S4 baseline evidence remain pending until executable/provider gates are available.

### 6. Agent Lifecycle
See `docs/AGENT_LIFECYCLE.md`.
- [ ] Define evidence-aware fitness/replication criteria.
- [ ] Define non-duplicating child capital transfer/allocation.
- [ ] Persist lineage/config versions and lifecycle reasons.

### 7. 24/7 Paper
- [ ] Add run/session identity and operational health.
- [ ] Add sustained recovery/reconciliation procedures and monitoring.
- [ ] Run long-lived forward Paper experiments.

### 8. Strategy research
See `docs/STRATEGIES.md`.
- [ ] Re-evaluate legacy strategy ideas under new contracts.
- [ ] Promote only deterministic, reproducibly useful logic.

### 9. Legacy pruning
See `docs/LEGACY_AUDIT.md`.
- [ ] Delete obsolete legacy services after useful concepts migrate.
- [ ] Remove obsolete Mongo/config/dependencies/pages and re-audit references.

### 10. Live readiness
See `docs/LIVE_TRADING_GATE.md`.
- [ ] Design separate Live adapter only after prior gates.
- [ ] Verify secrets, limits, emergency stop, reconciliation and staged rollout.
- [ ] Require explicit authorization before real-capital activation.

## Validation gate

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Static review is not a substitute for fresh execution evidence. Backtest performance numbers are not evidence unless they come from persisted reproducible runs over a documented immutable dataset.
