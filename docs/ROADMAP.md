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

**Goal:** Build a provider-neutral, real-only layer for current quotes and closed OHLCV candles.

Implemented in code/documentation:

- immutable `Quote` and `Candle` contracts with `evidence_mode=real`;
- canonical `BASE/USDT` symbol normalization;
- UTC-only timestamps and provider provenance;
- `MarketDataService` provider-neutral boundary;
- public read-only `BinancePublicMarketDataProvider` with no credentials or execution methods;
- current quotes from provider-timestamped aggregate trades;
- closed candles only;
- stale/future quote rejection;
- candle gap/order/staleness validation;
- bounded retry on transport errors, 429 and 5xx;
- fail-closed errors with no generated/mock fallback;
- `/api/market-data/status`, `/quote/{symbol}` and `/candles/{symbol}`;
- deterministic unit/API tests authored for parsing, quality and failure semantics;
- legacy `BinanceService` remains unmounted and is not reused as the real-data provider.

**Exit condition:** Paper/Backtest consumers cannot receive generated prices through the real-data contract.

**Status:** source/contract gate is statically satisfied. Fresh backend/frontend/build execution on the exact Phase 1 HEAD is still required for execution certification.

## Phase 2 — Portfolio & Accounting

**Goal:** Establish one authoritative, persistent long-only accounting layer before any Paper execution exists.

Implemented in code/documentation:

- SQLModel Account, Order, Fill, Position and LedgerEntry records;
- funded capital, cash, fees, average cost, realized/unrealized PnL, equity and exposure contracts;
- BUY fee included in acquisition basis and SELL fee included in realized result;
- additive buys, partial closes and full closes;
- fail-closed insufficient-cash, oversell and overfill checks;
- explicit funding ledger separate from PnL;
- restart/reload reconstruction from persisted records;
- reconciliation checks for financial identity and persisted-order/fill consistency;
- safe bootstrap of legacy agents from initial/funded capital only, excluding unverified synthetic current balance;
- accounting-backed new-agent creation and deposits;
- lifecycle deletion no longer erases financial balances;
- manual replication blocked until a non-duplicating capital-allocation policy exists;
- read-only `/api/accounting/agents/{agent_id}` inspection API;
- no HTTP path for creating orders/fills or executing trades in Phase 2.

**Exit condition:** open/close/fees/PnL/funding/restart behavior is deterministic, persisted and reconcilable, with no competing financial source of truth for new work.

**Status:** source/contract gate is statically satisfied. Fresh backend/frontend/build execution on the exact Phase 2 HEAD is still required for execution certification.

## Phase 3 — Paper Execution

Implement virtual orders/fills against real market observations with explicit fees/slippage and persistent state. Every accepted fill must enter through Phase 2 accounting.

**Exit:** a real-data/virtual-money end-to-end session can run without random market or random-close behavior.

## Phase 4 — Risk Engine

Enforce sizing, exposure, loss/drawdown limits, stale-data rejection and circuit breakers independently of strategies.

**Exit:** unsafe orders are rejected and critical failures fail closed.

## Phase 5 — Backtesting & Evidence

Build reproducible historical runs and evidence metadata. Evaluate S1-S4 as baselines.

**Exit:** strategy claims can be supported or rejected with reproducible reports.

## Phase 6 — Agent Evolution

Replace simplistic fitness/replication assumptions with evidence-aware lifecycle rules, lineage and explicit capital transfer/allocation. Replication stays blocked until it cannot duplicate money.

**Exit:** replication cannot create capital or be triggered by misleading short-term/synthetic performance.

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
