# AUTOMATON Roadmap

This roadmap defines dependency order. A later phase must not be treated as complete while a prerequisite remains materially broken.

## Phase 0 — Transition baseline

**Status:** source gate satisfied; fresh repository execution remains pending.

## Phase 1 — Real Market Data

**Status:** source/contract gate satisfied; executable certification pending.

## Phase 2 — Portfolio & Accounting

**Status:** source/contract gate satisfied; executable certification pending.

## Phase 3 — Paper Execution

**Status:** source/contract gate satisfied; executable certification and real-provider smoke remain pending.

## Phase 4 — Risk Engine

**Status:** source/contract/static gate satisfied. Fresh backend/frontend/build execution and a real-provider virtual-capital smoke remain required for execution certification.

## Phase 5 — Backtesting & Evidence

**Goal:** produce reproducible strategy evidence from immutable real historical data without contaminating Paper state or modifying strategy rules.

Implemented in source:

- immutable `BacktestDataset`/`BacktestCandle` snapshots;
- canonical SHA-256 over normalized candle content;
- provider/symbol/interval/requested+actual UTC window/count provenance;
- paginated public read-only Binance historical provider with no synthetic fallback;
- rejection of empty, duplicate, out-of-order, gapped, mixed-provider and out-of-window data;
- UTC-preserving SQLite evidence timestamps;
- isolated long-only `BacktestLedger`, with regression coverage preventing Paper Account/PaperExecution/RiskDecision contamination;
- deterministic `backtest-v1`;
- signal on candle `t`, execution no earlier than candle `t+1` open;
- no pyramiding, default 25% allocation, 10 bps adverse slippage and 10 bps fee;
- explicit `DATASET_END_EXIT` without diluting the time-in-market denominator;
- persistent `BacktestRun`, `BacktestRunEvidence`, `BacktestTrade`, `BacktestEquityPoint`;
- SHA-256 fingerprint of active strategy source for every new run;
- older pre-fingerprint runs remain readable but missing provenance is never invented;
- return/PnL, round trips, wins/losses, averages, expectancy, profit factor where defined, max drawdown, fees and exposure metrics;
- undefined ratios remain null;
- interrupted RUNNING runs are invalidated after restart;
- `/api/backtests` dataset/run/status/read API exposing source fingerprints;
- no optimizer, Live adapter or automatic strategy-to-Paper integration;
- Settings/client identify `backtesting=evidence_phase_5` without profitability claims;
- S1-S4 are consumed unchanged as `baseline-v1` strategy inputs.

**Exit condition:** the source path `real historical snapshot -> strategy using history through t -> next-candle deterministic execution -> isolated financial state -> persisted source fingerprint/equity/trades/metrics` is reproducible and carries enough provenance to compare runs without mixing evidence modes.

**Status:** source/contract/static gate satisfied. Exact-HEAD tests/build and a real historical provider smoke remain required for execution certification. S1-S4 real-provider baseline performance remains **unobserved** until actual reproducible runs execute; no numbers may be invented.

## Phase 6 — Agent Evolution

Define evidence-aware lifecycle/replication rules, lineage and explicit capital transfer/allocation. Replication remains blocked until it cannot duplicate money.

## Phase 7 — 24/7 Paper Operation

Add run/session identity, recovery, reconciliation, provider resilience, observability and long-running Paper operation.

## Phase 8 — Strategy Research

Evaluate richer historical/new strategy ideas and promote only reproducibly useful logic.

## Phase 9 — Legacy Pruning

Delete obsolete legacy implementations only after selected concepts have migrated and dependency/reference audits are clean.

## Phase 10 — Live Readiness

Satisfy `LIVE_TRADING_GATE.md`, design a separate exchange execution adapter, secret handling, emergency controls and staged rollout. Live activation remains a separate explicit decision.

## Deferred product areas

Auth, payments, LLM chat, public APIs, multi-user features and UI customization remain deferred unless needed to operate or validate the trading product.
