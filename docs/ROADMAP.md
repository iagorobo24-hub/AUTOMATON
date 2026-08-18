# AUTOMATON Roadmap

This roadmap defines dependency order. A later phase must not be treated as complete while a prerequisite remains materially broken.

## Phase 0 — Transition baseline

**Goal:** Preserve the working SQLModel application while removing ambiguity about the old simulator.

- keep active agents/trades/UI coherent;
- isolate synthetic behavior as test/transition infrastructure;
- maintain regression tests and fresh validation when execution is available;
- keep legacy code unmounted until migrated or deleted.

**Exit:** current runtime is understandable, documented and safe to evolve without reactivating Mongo by accident.

## Phase 1 — Real Market Data

Build a provider-neutral real-data layer for candles/current prices with UTC timestamps, normalization, staleness/gap handling and deterministic parsing tests.

**Exit:** Paper/Backtest consumers cannot receive generated prices through the real-data contract.

## Phase 2 — Portfolio & Accounting

Introduce authoritative orders/fills/positions/account/equity semantics and reconciliation invariants.

**Exit:** open/close/fees/PnL/restart are deterministic and tested.

## Phase 3 — Paper Execution

Implement virtual orders/fills against real market observations with explicit fees/slippage and persistent state.

**Exit:** a real-data/virtual-money end-to-end session can run without random market or random-close behavior.

## Phase 4 — Risk Engine

Enforce sizing, exposure, loss/drawdown limits, stale-data rejection and circuit breakers independently of strategies.

**Exit:** unsafe orders are rejected and critical failures fail closed.

## Phase 5 — Backtesting & Evidence

Build reproducible historical runs and evidence metadata. Evaluate S1-S4 as baselines.

**Exit:** strategy claims can be supported or rejected with reproducible reports.

## Phase 6 — Agent Evolution

Replace simplistic fitness/replication assumptions with evidence-aware lifecycle rules, lineage and explicit capital allocation.

**Exit:** replication cannot be triggered by misleading short-term/synthetic performance.

## Phase 7 — 24/7 Paper Operation

Add recovery, reconciliation, provider resilience, observability, sessions and long-running Paper operation.

**Exit:** agents can operate unattended with real data and virtual capital while preserving traceable state.

## Phase 8 — Strategy Research

Evaluate richer ideas from historical Alpha/Beta/Gamma material and new research. Promote only reproducibly useful logic.

**Exit:** candidate strategies have deterministic code, backtests and Paper evidence.

## Phase 9 — Live Readiness

Satisfy `LIVE_TRADING_GATE.md`, design the exchange execution adapter, secret handling, emergency controls and staged deployment plan.

**Exit:** technical readiness is documented; Live remains disabled pending explicit authorization.

## Phase 10 — Live (optional)

Only after a separate decision. Start with minimal capital, strict limits and defined rollback/stop criteria.

## Deferred product areas

Auth, payments, LLM chat, public APIs, multi-user features and UI customization remain deferred unless they become necessary to operate or validate the core trading product.
