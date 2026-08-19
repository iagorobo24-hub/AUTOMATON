# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable autonomous Paper Trading platform: **real market data, virtual capital, deterministic accounting/execution, explicit risk, reproducible evidence, evidence-aware lifecycle and recoverable long-running operation**.

## Current baseline

- FastAPI + SQLModel + SQLite and React/Vite are active.
- Synthetic `AgentEngine` and legacy Mongo/trading engines are outside normal runtime.
- Phases 1–7 source/static contracts are present.
- Phase 7 provides explicit persistent autonomous Paper sessions; no session starts or resumes merely because the process boots.
- Live remains disabled.
- Fresh exact-HEAD execution evidence remains required.

## Ordered implementation program

### 0–5 — Foundation and evidence

Market Data, Accounting, Paper Execution, Risk, Backtesting/Evidence and their source/static gates are complete. Fresh execution certification remains pending; Phase 5 real-provider S1-S4 baseline is still unobserved.

### 6. Agent Evolution
See `docs/AGENT_LIFECYCLE.md`.
- [x] Versioned fitness, lineage and lifecycle records.
- [x] Current-source Backtest provenance + agent-specific Paper evidence gates.
- [x] Accounting/recovery integrity requirements.
- [x] Funded-liquid child allocation with conserved parent+child capital.
- [x] Manual evidence-gated replication; no mutation/auto-replication.
- [x] Exact-HEAD static audit/documentation reconciliation.
- [ ] Execute exact-HEAD backend/frontend/build gate.

**Phase 6 source/contract/static gate:** complete. Execution certification remains pending.

### 7. 24/7 Paper Operation
See `docs/superpowers/specs/2026-08-19-phase-7-paper-runtime-design.md`.
- [x] Add additive `PaperRuntimeSession`, `PaperRuntimeAgent`, `PaperRuntimeCycle`, `PaperRuntimeEvent` persistence.
- [x] Define `runtime-v1` session lifecycle: CREATED/RUNNING/PAUSED/DEGRADED/RECOVERY_REQUIRED/STOPPED.
- [x] Enforce persistent session ownership for agent/symbol/interval, including recovery states.
- [x] Validate session symbol/timeframe through the active Market Data normalization/interval contract before persistence.
- [x] Evaluate each attached active agent at most once per new real closed candle.
- [x] Consume unchanged S1-S4 close-price logic; no strategy mutation/tuning.
- [x] Persist HOLD/position-guard no-actions without creating orders.
- [x] Size flat BUY from 25% available cash with exact `paper-v1` compounded-cost reserve; close full long on SELL.
- [x] Derive deterministic runtime Paper request ids from session/agent/symbol/candle/signal.
- [x] Route autonomous actions through current real Market Data -> Risk -> `PaperExecution(origin=strategy_runtime)` -> Accounting.
- [x] Keep Risk mandatory and reject unsupported Paper origins.
- [x] Add in-process asyncio task ownership while SQLite remains authoritative.
- [x] Run scheduler start/resume/pause/stop controls on an active asyncio event loop rather than FastAPI's sync threadpool.
- [x] Track heartbeat, last cycle, outcomes, failures and structured runtime events.
- [x] Degrade after configured consecutive operational failures without synthetic fallback.
- [x] Block financial ambiguity in RECOVERY_REQUIRED.
- [x] Reconcile interrupted runtime cycles without replaying uncertain orders.
- [x] Convert persisted RUNNING/DEGRADED sessions to RECOVERY_REQUIRED after restart and never auto-resume them.
- [x] Block start/recover on unresolved PaperRequest/PaperExecution recovery state.
- [x] Mount `/api/runtime` create/read/cycles/start/pause/resume/recover/stop controls.
- [x] Update Paper status, health/estado, client, Settings, Dashboard and Ops Monitor for session-controlled autonomous Paper.
- [x] Keep automatic replication, optimizer and Live execution absent.
- [x] Complete final exact-HEAD static audit/documentation drift search.
- [ ] Execute exact-HEAD backend tests, frontend tests/build and sustained real-provider Paper runtime smoke.

**Phase 7 source/contract/static gate:** complete. Execution certification remains pending because the current environment cannot resolve `github.com`; operational certification additionally requires a sustained real-provider Paper session including restart/recovery observation.

### 8. Strategy Research
See `docs/STRATEGIES.md`.
- [ ] Establish train/validation/out-of-sample/walk-forward methodology.
- [ ] Run observed S1-S4 historical baseline and forward Paper experiments under fixed costs/contracts.
- [ ] Version every strategy/config change and source fingerprint.
- [ ] Compare expectancy/drawdown/cost robustness across identical evidence windows.
- [ ] Promote only reproducibly useful configurations; do not optimize and score on the same window.

### 9. Legacy Pruning
See `docs/LEGACY_AUDIT.md`.
- [ ] Audit imports/routes/pages/config/dependencies against the Phase 7 active runtime.
- [ ] Migrate any still-useful concepts.
- [ ] Remove obsolete Mongo, old trading/Paper engines, mock fallbacks and dead UI only after evidence/recovery dependencies are clean.
- [ ] Re-run repository/API/import/documentation audits.

### 10. Live Readiness
See `docs/LIVE_TRADING_GATE.md`.
- [ ] Design a separate Live adapter; never toggle Paper into Live.
- [ ] Implement secret permissions, exchange filters/precision, idempotency and reconciliation.
- [ ] Add hard capital/position limits, emergency stop and staged rollout controls.
- [ ] Require explicit authorization before any real-capital activation.

## Validation gate

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Static review is not fresh execution evidence. Phase 7 operational certification additionally requires a sustained real-provider Paper session including restart/recovery observation.
