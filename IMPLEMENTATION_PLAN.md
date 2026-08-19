# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable autonomous Paper Trading research platform: **real market data, virtual capital, deterministic accounting/execution, explicit risk, reproducible historical/forward evidence and disciplined strategy promotion**.

## Current baseline

- FastAPI + SQLModel + SQLite and React/Vite are active.
- Synthetic `AgentEngine` and legacy Mongo/trading engines are outside normal runtime.
- Phases 1–7 source/static contracts are present.
- Phase 7 provides explicit persistent autonomous Paper sessions; no session starts or resumes merely because the process boots.
- Phase 8 Strategy Research is implemented in source as an evidence/orchestration layer; it does not mutate strategies or auto-deploy candidates.
- Live remains disabled.
- Fresh exact-HEAD execution evidence remains required.

## Ordered implementation program

### 0–5 — Foundation and evidence

Market Data, Accounting, Paper Execution, Risk, Backtesting/Evidence and their source/static gates are complete. Fresh execution certification remains pending; Phase 5 real-provider S1-S4 baseline is still unobserved.

### 6. Agent Evolution
- [x] Versioned fitness, lineage and lifecycle records.
- [x] Current-source Backtest provenance + agent-specific Paper evidence gates.
- [x] Accounting/recovery integrity requirements.
- [x] Funded-liquid child allocation with conserved parent+child capital.
- [x] Manual evidence-gated replication; no mutation/auto-replication.
- [x] Exact-HEAD static audit/documentation reconciliation.
- [ ] Execute exact-HEAD backend/frontend/build gate.

**Phase 6 source/contract/static gate:** complete. Execution certification remains pending.

### 7. 24/7 Paper Operation
- [x] Persistent session/agent/cycle/event state and explicit lifecycle.
- [x] Market Data contract validation before session persistence.
- [x] One evaluation per new real closed candle.
- [x] Unchanged S1-S4 -> Risk -> PaperExecution(strategy_runtime) -> Accounting.
- [x] Deterministic request ids, recovery, ownership and no auto-resume.
- [x] Async scheduler controls execute on an active event loop.
- [x] Ops Monitor/Settings/Dashboard observability.
- [x] No auto-replication, optimizer or Live.
- [x] Exact-HEAD static audit/documentation reconciliation.
- [ ] Execute exact-HEAD backend/frontend/build and sustained real-provider runtime smoke.

**Phase 7 source/contract/static gate:** complete. Execution/operational certification remains pending.

### 8. Strategy Research
See `docs/superpowers/specs/2026-08-19-phase-8-strategy-research-design.md` and `docs/STRATEGIES.md`.
- [x] Add additive `ResearchPolicy`, `ResearchStudy`, `ResearchWindow`, `ResearchEvaluation`, `StrategyCandidate` persistence.
- [x] Bootstrap versioned `research-v1` idempotently.
- [x] Freeze strategy version/source SHA, execution policy, fees, slippage and position fraction from first Backtest evidence.
- [x] Require identical market/timeframe, initial capital and historical risk-profile version across study windows.
- [x] Require chronological non-overlapping repeating TRAIN -> VALIDATION -> OOS folds.
- [x] Reject non-COMPLETED Backtests or missing source fingerprint evidence.
- [x] Require >=5 round trips in VALIDATION and OOS.
- [x] Require positive VALIDATION/OOS net return and expectancy.
- [x] Enforce OOS max drawdown <=15%, profit factor >=1.05 when defined and <=50% relative return degradation.
- [x] Require STOPPED Phase 7 forward sessions on the same symbol/timeframe with matching-strategy agents and persisted runtime cycles.
- [x] Require >=3 unique FILLED closing SELL Paper executions with `origin=strategy_runtime`.
- [x] Reject unresolved Paper recovery and forward accounts contaminated by FILLED non-runtime Paper execution.
- [x] Require positive authoritative account-level realized PnL context.
- [x] Persist immutable PASS/REJECT ResearchEvaluation snapshots with historical/forward evidence ids and metrics.
- [x] Re-check current active strategy source SHA on every promotion attempt.
- [x] Create a fresh evaluation for every promotion attempt; old PASS cannot be reused silently.
- [x] Persist at most one StrategyCandidate per exact strategy/version/source SHA and preserve manual promotion semantics.
- [x] Mount `/api/research` studies/windows/evaluate/promote/candidates surfaces.
- [x] Keep `/optimize`, source mutation, auto-deployment and Live absent.
- [x] Update backend runtime/client/Settings for `strategy_research=evidence_phase_8`.
- [ ] Complete final exact-HEAD static audit and documentation drift search.
- [ ] Execute exact-HEAD backend/frontend/build gate plus observed historical/forward research smoke.

**Phase 8 implementation/source contracts:** present. Formal source/static closure depends on the final exact-HEAD audit. Promotion remains an evidence classification, not a profitability or deployment guarantee.

### 9. Legacy Pruning
See `docs/LEGACY_AUDIT.md`.
- [ ] Audit imports/routes/pages/config/dependencies against the Phase 8 active runtime.
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

Static review is not fresh execution evidence. Phase 8 operational evidence also requires real historical Backtests and completed forward Paper sessions under the research contract.
