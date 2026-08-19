# AUTOMATON Roadmap

This roadmap defines dependency order. A later phase must not be treated as complete while a prerequisite remains materially broken.

## Phase 0 — Transition baseline

**Goal:** remove ambiguity and contamination from the old simulator while preserving the SQLModel application.

**Status:** source gate satisfied; fresh repository execution remains pending.

## Phase 1 — Real Market Data

**Goal:** provider-neutral, real-only current quotes and closed OHLCV candles.

Implemented: real Quote/Candle contracts, UTC/provider provenance, public read-only Binance provider, stale/future/gap/order checks, bounded retries and fail-closed behavior with no synthetic fallback.

**Status:** source/contract gate satisfied; executable certification pending.

## Phase 2 — Portfolio & Accounting

**Goal:** one authoritative persistent financial layer.

Implemented: Account, Order, Fill, Position, LedgerEntry, long-only accounting invariants, funding/PnL separation, restart/reconciliation and safe historical-agent bootstrap.

**Status:** source/contract gate satisfied; executable certification pending.

## Phase 3 — Paper Execution

**Goal:** deterministic virtual execution against real current market observations.

Implemented: persistent PaperExecution provenance, operator-only MARKET BUY/SELL, `paper-v1`, request-id idempotency, conservative recovery and Accounting-only financial mutation.

**Status:** source/contract gate satisfied; executable certification and real-provider smoke remain pending.

## Phase 4 — Risk Engine

**Goal:** place an independent, persistent, fail-closed approval layer before normal Paper order creation.

Implemented:

- persistent `RiskProfile` and `RiskDecision`;
- idempotent `risk-v1` bootstrap;
- maximum order notional and order/equity limits;
- projected total-exposure and per-symbol concentration limits;
- maximum open-position limit;
- realized-loss and drawdown gates;
- real/fresh market-data requirement;
- active-agent/account-currency checks;
- complete real marks plus full Accounting reconciliation for BUY;
- valuation-free structural Accounting integrity for risk-reducing SELL;
- unresolved Paper recovery gate;
- risk-reducing SELL exception without allowing oversells;
- persistent global pause/resume circuit breaker;
- mandatory persisted Risk ALLOW for normal Paper execution;
- one-time payload/provider-observation-bound ALLOW consumption;
- ALLOW invalidation if the active profile is paused before consumption;
- exact `paper-v1` compounded BUY cost reserve of 20.01 bps;
- idempotent Risk rejection with no Paper Order/Fill;
- fail-closed/idempotent missing account/agent handling;
- `/api/risk/status`, `/profiles/active`, `/decisions`, `/pause`, `/resume`;
- Settings/Dashboard/runtime visibility for Phase 4 state;
- exact-HEAD static code/documentation audit.

**Exit condition:** unsafe, unreconciled or unapproved normal Paper orders cannot create Paper financial state, and every successful normal Paper execution consumes a matching persisted Risk decision.

**Status:** source/contract/static gate satisfied. Fresh backend/frontend/build execution and a real-provider virtual-capital smoke are still required for execution certification.

## Phase 5 — Backtesting & Evidence

Build reproducible historical runs and evidence metadata. Evaluate S1-S4 as baselines.

**Exit:** strategy claims can be supported or rejected with reproducible reports.

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