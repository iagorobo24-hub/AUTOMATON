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

Persistent `runtime-v1` sessions operate unchanged S1-S4 through real Market Data -> Risk -> Paper -> Accounting with one durable cycle per closed candle, deterministic request ids, recovery/ownership controls, no generated fallback and no auto-resume. Per-session/agent strategy version/source-SHA is captured at first start; later resume/recovery fails on drift, and older sessions are never fingerprinted retroactively.

**Status:** source/contract/static gate satisfied. Fresh backend/frontend/build execution and a sustained real-provider Paper run remain required for operational certification.

## Phase 8 — Strategy Research

`research-v1` uses comparable chronological TRAIN/VALIDATION/OOS Backtest evidence plus fingerprinted stopped Phase 7 forward Paper evidence. Promotion is manual, creates a fresh evaluation and never mutates source or auto-deploys.

**Status:** source/contract/static gate satisfied. Fresh executable tests/build plus observed real historical and forward Paper research evidence remain pending; no strategy performance is inferred from source or fixtures.

## Phase 9 — Legacy Pruning

Phase 9 removes the superseded second architecture after reference/dependency audits:

- Mongo service/injection/config/seed/models/dependencies and Mongo dev containers;
- old simulation/Paper/trading/risk/mock/replication/registry engines and routes;
- credentialed/mock-fallback legacy Binance service;
- inactive auth/chat/payments/notifications/dashboard/system/signals/strategy-CRUD code;
- executable Alpha/Beta/Gamma/regime/indicator legacy stack after retaining useful hypotheses as documentation;
- unreachable frontend pages, mock/simulation UI, duplicate components and obsolete tests tied to deleted contracts.

The active `backend/app/services/` package now contains only S1-S4 `strategies.py` plus its initializer. `Agent` remains the active identity/lifecycle anchor; old `Trade` rows remain quarantined as invalid pre-provenance evidence. Runtime exposes `legacy_pruning=pruned_phase_9`. Live remains disabled.

**Status:** source/contract/static gate satisfied. Exact-HEAD backend/frontend/build execution remains pending until fresh observed output exists.

## Phase 10 — Live Readiness

Design a structurally separate exchange adapter, secrets/permissions, exchange constraints, reconciliation, emergency controls and staged rollout. Real-capital activation remains a separate explicit authorization.

**Status:** not started. Phase 9 does not authorize or implement Live.

## Cross-phase certification debt

Fresh exact-HEAD backend tests, frontend tests/build and relevant real-provider smoke evidence are still required. Static closure must never be reported as a green runtime or profitable-strategy gate.
