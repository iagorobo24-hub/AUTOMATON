# AUTOMATON Roadmap

This roadmap defines dependency order. A later phase must not be treated as complete while a prerequisite remains materially broken.

## Phase 0 — Transition baseline

**Goal:** Preserve the SQLModel application while removing ambiguity and contamination from the old simulator.

Completed in code/documentation:

- active agents/trades/UI contracts remain coherent;
- normal startup does not start the synthetic `AgentEngine`;
- synthetic prices/random closes are isolated from the normal runtime;
- manual simulated-PnL mutation is removed from the active API/UI;
- deposits do not manufacture profit;
- pre-provenance trade records are retained as `legacy_unclassified` but excluded from verified financial metrics;
- health/state explicitly identify transition mode, synthetic disabled and Paper not implemented;
- legacy Mongo/trading code remains unmounted.

**Exit condition:** current runtime is understandable and cannot create new synthetic financial evidence through normal startup or active UI/API paths.

**Status:** code gate is statically satisfied. Fresh `pytest`, frontend tests and frontend build on the same HEAD are still required for execution certification.

## Phase 1 — Real Market Data

Build a provider-neutral real-data layer for candles/current prices with UTC timestamps, normalization, staleness/gap handling and deterministic parsing tests.

The legacy `BinanceService` is not an acceptable provider adapter as-is because provider/key failures silently fall back to mock/generated data. Phase 1 must fail closed instead.

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

Replace simplistic fitness/replication assumptions with evidence-aware lifecycle rules, lineage and explicit capital allocation. Manual replication remains an operator action; automatic replication must wait for validated evidence criteria.

**Exit:** automatic replication cannot be triggered by misleading short-term/synthetic performance.

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
