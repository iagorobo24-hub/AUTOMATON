# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable Paper Trading platform: **real market data, virtual capital, deterministic accounting, explicit risk and reproducible evidence**.

## Current baseline

- FastAPI + SQLModel + SQLite are the active backend/persistence baseline.
- React/Vite is the active frontend.
- Historical Mongo/Paper/TradingEngine code is not mounted by `app.main`.
- Synthetic `AgentEngine` is not started by normal runtime.
- Phase 1 Market Data is real-only and fail-closed.
- Phase 2 Accounting is authoritative for financial state.
- Phase 3 Paper Execution is operator-only, deterministic and idempotent.
- Phase 4 Risk is mounted at `/api/risk`, persists `risk-v1` profiles/decisions and is mandatory for normal Paper execution.
- Risk rejection creates no Paper Order/Fill; ALLOW is one-time consumable and linked to Paper execution.
- Automated strategy/agent execution remains disabled until a later explicit integration step.
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
- [x] Add persistent `RiskProfile` and `RiskDecision` records.
- [x] Bootstrap versioned `risk-v1` profile idempotently.
- [x] Add absolute order-notional and order/equity limits.
- [x] Add projected total exposure and symbol-concentration limits.
- [x] Add maximum open-position limit.
- [x] Add realized-loss and drawdown limits.
- [x] Reject stale/non-real data, inactive agents, currency mismatch, incomplete real marks for BUY, accounting mismatch and unresolved Paper recovery.
- [x] Preserve SELL risk-reduction path with valuation-free structural accounting integrity while still rejecting oversells.
- [x] Add persistent global pause/resume circuit breaker.
- [x] Require persisted current-profile Risk ALLOW before normal Paper execution.
- [x] Make Risk ALLOW decisions one-time consumable and payload/provider-observation bound.
- [x] Invalidate unconsumed ALLOW when the profile is paused before Paper consumption.
- [x] Match BUY cash reserve exactly to `paper-v1` compounded execution cost (20.01 bps).
- [x] Ensure Risk rejection completes the Paper request idempotently without Order/Fill creation.
- [x] Make missing account/agent failures idempotent and fail-closed instead of leaving ambiguous PROCESSING state.
- [x] Expose `/api/risk/status`, `/profiles/active`, `/decisions`, `/pause`, `/resume`.
- [x] Update runtime/UI/docs to report `authoritative_phase_4` while autonomous trading remains disabled.
- [x] Complete exact-HEAD static audit and reconcile code/documentation drift.
- [ ] Execute targeted Risk/Paper tests plus full backend/frontend/build gate on exact Phase 4 HEAD.
- [ ] Run a real-provider virtual-capital smoke and inspect RiskDecision -> PaperExecution -> Accounting reconciliation.

**Phase 4 source/contract/static gate:** complete. Execution certification remains pending until the executable gates above are observed on the exact HEAD.

### 5. Backtesting & Evidence
See `docs/BACKTESTING.md` and `docs/METRICS_AND_EVIDENCE.md`.
- [ ] Build reproducible historical runner using real datasets.
- [ ] Add fee/slippage and bias controls.
- [ ] Evaluate S1-S4 baselines.
- [ ] Produce machine-readable run metadata/comparable reports.

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

Static review is not a substitute for fresh execution evidence.