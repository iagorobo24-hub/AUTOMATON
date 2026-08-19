# AUTOMATON Roadmap

This roadmap defines dependency order. Source/static closure and executable certification are intentionally separate.

## Phases 0–4

Transition safety, Real Market Data, Accounting, deterministic Paper and Risk source contracts are implemented. Fresh exact-HEAD executable certification remains cross-phase debt.

## Phase 5 — Backtesting & Evidence

Immutable real historical snapshots, canonical dataset/source SHA-256, next-candle deterministic execution, isolated financial evidence and metrics are implemented.

**Status:** source/contract/static gate satisfied. Exact-HEAD execution and observed real-provider S1-S4 baseline remain pending; no performance numbers are inferred.

## Phase 6 — Agent Evolution

`evolution-v1` implements evidence-aware fitness, lineage/lifecycle and manual child replication with conserving Accounting transfer.

**Status:** source/contract/static gate satisfied. Execution certification remains pending.

## Phase 7 — 24/7 Paper Operation

Persistent `runtime-v1` sessions operate unchanged S1-S4 through real Market Data -> Risk -> Paper -> Accounting with one durable cycle per closed candle, deterministic request ids, recovery/ownership controls, no synthetic fallback and no auto-resume. Phase 8 hardening adds per-session/agent strategy version/source-SHA capture at first start; later resume/recovery fails on drift, and sessions started before that provenance contract are never fingerprinted retroactively.

**Status:** source/contract/static gate satisfied. Fresh backend/frontend/build execution and a sustained real-provider Paper run remain required for operational certification.

## Phase 8 — Strategy Research

**Goal:** decide which exact strategy configurations deserve continued research using reproducible historical holdout evidence plus forward Paper evidence, without optimizing and scoring on the same window or auto-deploying results.

Implemented in source:

- additive `ResearchPolicy`, `ResearchStudy`, `ResearchWindow`, `ResearchEvaluation`, `StrategyCandidate` records;
- idempotent `research-v1` policy bootstrap;
- explicit repeating chronological TRAIN/VALIDATION/OOS folds;
- first-window freeze of strategy version/source SHA, execution policy, fees, slippage and position fraction;
- identical symbol/timeframe, initial capital and historical risk-profile requirements across study windows;
- completed Backtest + source-fingerprint requirements;
- minimum VALIDATION/OOS round-trip sample;
- positive VALIDATION/OOS return and expectancy gates;
- OOS drawdown/profit-factor/relative-degradation limits;
- forward evidence from STOPPED Phase 7 sessions on the same market/timeframe;
- matching strategy ID/version/source SHA captured by Phase 7 at first session start;
- legacy Phase 7 sessions without captured provenance are ineligible for promotion evidence;
- matching-strategy runtime cycles and unique FILLED `strategy_runtime` closing SELL provenance;
- unresolved Paper recovery rejection;
- rejection when a qualifying account contains any FILLED execution outside the exact Research-selected sessions;
- positive authoritative account-level realized-PnL context;
- immutable PASS/REJECT evaluation snapshots with referenced historical and forward evidence;
- current-source SHA check on promotion, giving historical SHA == forward captured SHA == current SHA;
- a fresh evaluation for every manual promotion attempt;
- one candidate identity per exact strategy/version/source SHA;
- `/api/research` status/policy/studies/windows/evaluate/promote/candidates surfaces;
- `strategy_research=evidence_phase_8` runtime/UI status;
- no optimizer, automatic strategy mutation, auto-deployment or Live capability.

Promotion means only that the exact source/config satisfied `research-v1` against the evidence referenced by that evaluation. It is not a future-profitability guarantee or Live eligibility.

**Status:** source/contract/static gate satisfied. Fresh executable tests/build plus observed real historical and forward Paper research evidence remain pending; no strategy performance is inferred from source or fixtures.

## Phase 9 — Legacy Pruning

Remove obsolete Mongo/trading/synthetic services, dead pages/config/dependencies and historical shortcuts only after reference/dependency audits prove no active recovery/evidence path depends on them.

## Phase 10 — Live Readiness

Design a structurally separate exchange adapter, secrets/permissions, exchange constraints, reconciliation, emergency controls and staged rollout. Real-capital activation remains a separate explicit authorization.

## Cross-phase certification debt

Fresh exact-HEAD backend tests, frontend tests/build and relevant real-provider smoke evidence are still required. Static closure must never be reported as a green runtime or profitable-strategy gate.
