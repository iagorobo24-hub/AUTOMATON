# AUTOMATON Implementation Plan

## Current program objective

Build a verifiable autonomous Paper Trading research platform: **real market data, virtual capital, deterministic accounting/execution, explicit risk, reproducible historical/forward evidence and disciplined strategy promotion**.

## Current baseline

- FastAPI + SQLModel + SQLite and React/Vite are active.
- Phase 9 physically removed the superseded Mongo/mock/trading architecture; no Synthetic AgentEngine, legacy Binance execution service or Mongo runtime remains in active source.
- Phases 1–9 source/static contracts are present.
- Phase 7 provides explicit persistent autonomous Paper sessions; no session starts or resumes merely because the process boots.
- Phase 8 Strategy Research is an evidence/orchestration layer; it does not mutate strategies or auto-deploy candidates.
- Phase 7 captures strategy/version/source-SHA evidence at first session start so Phase 8 can prove forward-source identity; sessions started before that contract cannot receive provenance retroactively.
- Phase 9 reports `legacy_pruning=pruned_phase_9` and retains only explicitly justified transition records such as quarantined pre-provenance `Trade` rows.
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
- [x] Capture per-session/agent strategy ID/version/source SHA at first start; block resume/recovery on strategy/source drift.
- [x] Never fabricate source evidence for sessions that had already started before the fingerprint contract.
- [x] Ops Monitor/Settings/Dashboard observability.
- [x] No auto-replication, optimizer or Live.
- [x] Exact-HEAD static audit/documentation reconciliation.
- [ ] Execute exact-HEAD backend/frontend/build and sustained real-provider runtime smoke.

**Phase 7 source/contract/static gate:** complete. Execution/operational certification remains pending.

### 8. Strategy Research
See `docs/superpowers/specs/2026-08-19-phase-8-strategy-research-design.md` and `docs/STRATEGIES.md`.
- [x] Add additive `ResearchPolicy`, `ResearchStudy`, `ResearchWindow`, `ResearchEvaluation`, `StrategyCandidate` persistence.
- [x] Bootstrap versioned `research-v1` idempotently.
- [x] Freeze strategy version/source SHA and comparable execution assumptions from first Backtest evidence.
- [x] Require chronological non-overlapping repeating TRAIN -> VALIDATION -> OOS folds.
- [x] Apply holdout sample/return/expectancy/drawdown/profit-factor/degradation gates.
- [x] Require fingerprinted STOPPED Phase 7 forward sessions and unambiguous Paper execution/PnL attribution.
- [x] Persist immutable PASS/REJECT ResearchEvaluation snapshots.
- [x] Re-check current active strategy source SHA on every promotion attempt.
- [x] Create a fresh evaluation for every promotion attempt and at most one candidate per exact strategy/version/source SHA.
- [x] Keep optimizer, source mutation, auto-deployment and Live absent.
- [x] Complete final exact-HEAD static audit and documentation reconciliation.
- [ ] Execute exact-HEAD backend/frontend/build gate plus observed historical/forward research smoke.

**Phase 8 source/contract/static gate:** complete. Execution certification and observed real historical/forward research evidence remain pending. Promotion remains an evidence classification, not a profitability or deployment guarantee.

### 9. Legacy Pruning
See `docs/LEGACY_AUDIT.md`, `docs/superpowers/specs/2026-08-20-phase-9-legacy-pruning-design.md` and `docs/superpowers/plans/2026-08-20-phase-9-legacy-pruning.md`.
- [x] Audit imports/routes/pages/config/dependencies against the Phase 8 active runtime.
- [x] Preserve useful historical strategy concepts as research documentation rather than active legacy executables.
- [x] Remove Mongo DatabaseService/injection/config/seed/models/dependencies and Mongo dev containers.
- [x] Remove superseded simulation/Paper/trading/risk/mock/replication/registry engines and routers.
- [x] Remove credentialed/mock-fallback legacy BinanceService and python-binance dependency.
- [x] Remove inactive auth/chat/payments/notifications/dashboard/system/signals/strategy-CRUD implementation and dedicated dependencies.
- [x] Remove legacy Alpha/Beta/Gamma/regime/indicator executables without modifying S1-S4.
- [x] Remove unreachable frontend pages, mock data, simulation hooks and duplicate/neural-fiber UI.
- [x] Remove obsolete tests that targeted deleted modules/external preview endpoints rather than current contracts.
- [x] Add source guards preventing deleted backend/frontend/dependency/Mongo infrastructure from silently returning.
- [x] Expose `legacy_pruning=pruned_phase_9` and backend version `2.12.0` without changing active financial semantics.
- [x] Reconcile architecture/database/legacy audit/project contracts.
- [x] Complete exact-HEAD reference/drift audit; S1-S4 remain unchanged and Live remains disabled.
- [ ] Execute exact-HEAD backend/frontend/build gate.

**Phase 9 source/contract/static gate:** complete. Executable certification remains pending until fresh exact-HEAD test/build output is observed.

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

Static review is not fresh execution evidence. Operational evidence also requires real historical Backtests and completed forward Paper sessions under the relevant contracts.
