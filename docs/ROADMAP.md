# AUTOMATON Roadmap

This roadmap defines dependency order. A later phase must not be treated as complete while a prerequisite remains materially broken.

## Phase 0 — Transition baseline

**Goal:** preserve the SQLModel application while removing ambiguity and contamination from the old simulator.

Completed in source/documentation:

- normal startup does not start the synthetic `AgentEngine`;
- synthetic prices/random closes/manual fake PnL are isolated from active financial evidence;
- pre-provenance Trade records stay `legacy_unclassified`;
- funding does not manufacture profit;
- legacy Mongo/trading code stays unmounted.

**Status:** source gate satisfied; fresh repository execution remains pending.

## Phase 1 — Real Market Data

**Goal:** provider-neutral, real-only current quotes and closed OHLCV candles.

Implemented:

- immutable real Quote/Candle contracts;
- UTC/provider provenance;
- public read-only Binance market provider;
- stale/future/gap/order checks;
- bounded retries/rate-limit handling;
- no mock/generated fallback;
- `/api/market-data` boundary.

**Status:** source/contract gate satisfied; executable certification pending.

## Phase 2 — Portfolio & Accounting

**Goal:** one authoritative persistent financial layer before Paper execution.

Implemented:

- Account, Order, Fill, Position and LedgerEntry;
- long-only funded capital/cash/cost basis/PnL/fees/equity/exposure;
- deterministic buy/sell and partial/full close semantics;
- funding separated from PnL;
- restart/reload and reconciliation;
- safe historical-agent bootstrap excluding unverified legacy current balance;
- replication blocked until capital transfer is defined.

**Status:** source/contract gate satisfied; executable certification pending.

## Phase 3 — Paper Execution

**Goal:** execute virtual orders against current real-market observations while preserving deterministic, auditable financial state.

Implemented:

- persistent `PaperExecution` provenance linked to Phase 2 Order/Fill;
- operator-only MARKET BUY/SELL path;
- `paper-v1`: 10 bps adverse slippage, 10 bps fee, full fill or rejection;
- real Quote required, with stale/future/provenance validation;
- active-agent and account-currency gates;
- every accepted fill delegated to Accounting;
- persistent `PaperRequest` idempotency with required `request_id`;
- identical replay returns the same execution; payload conflicts fail;
- financial rejections remain idempotent;
- provider failures remain retryable only when no financial state exists;
- conservative restart recovery: never blindly resubmit uncertain orders;
- ambiguous recovery state blocks the affected account;
- `/api/paper/status`, `/api/paper/orders/market`, `/api/paper/executions`;
- Ops Monitor displays Paper/real provider, quote, fill, fee and state;
- Settings reports operator-only Paper, automation blocked and Live disabled.

**Exit condition:** the source path `real Quote -> PaperExecution -> Accounting Fill/Position/Equity` is deterministic, persistent, idempotent and recoverable without random or Live behavior.

**Status:** source/contract gate satisfied by static review. Fresh backend/frontend/build execution and a real-provider/virtual-capital smoke run are still required for execution certification.

## Phase 4 — Risk Engine

**Goal:** put an independent fail-closed approval layer in front of automated Paper execution.

Required next:

- risk request/decision contract;
- order/notional sizing limits;
- per-agent and portfolio exposure limits;
- loss/drawdown constraints;
- stale-market/accounting-reconciliation circuit breakers;
- persisted profile/version and allow/reject reason;
- only after Risk is active may strategy/agent-originated orders reach Paper Execution.

**Exit:** unsafe or unreconciled orders cannot reach Paper Execution, and every automated order carries a persisted risk decision.

## Phase 5 — Backtesting & Evidence

Build reproducible historical runs and evidence metadata. Evaluate S1-S4 as baselines.

**Exit:** strategy claims can be supported or rejected with reproducible reports.

## Phase 6 — Agent Evolution

Replace simplistic fitness/replication assumptions with evidence-aware lifecycle rules, lineage and explicit capital transfer/allocation. Replication stays blocked until it cannot duplicate money.

**Exit:** replication cannot create capital or be triggered by misleading short-term/synthetic performance.

## Phase 7 — 24/7 Paper Operation

Add run/session identity, recovery, reconciliation, provider resilience, observability and long-running Paper operation.

**Exit:** agents can operate unattended with real data and virtual capital while preserving traceable state.

## Phase 8 — Strategy Research

Evaluate richer ideas from historical Alpha/Beta/Gamma material and new research. Promote only reproducibly useful logic.

## Phase 9 — Legacy Pruning

Delete obsolete legacy implementations only after selected concepts have been migrated and dependency/reference audits are clean.

## Phase 10 — Live Readiness

Satisfy `LIVE_TRADING_GATE.md`, design the separate exchange execution adapter, secret handling, emergency controls and staged deployment plan.

Live activation remains a separate explicit decision after all prior gates.

## Deferred product areas

Auth, payments, LLM chat, public APIs, multi-user features and UI customization remain deferred unless needed to operate or validate the core trading product.
