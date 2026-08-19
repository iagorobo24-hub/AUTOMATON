# Phase 5 Backtesting & Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build reproducible real-data historical backtests for S1-S4 with immutable datasets, deterministic no-look-ahead execution, isolated accounting and persisted evidence.

**Architecture:** Historical Binance data is frozen into immutable SQLModel dataset/candle records identified by SHA-256. A deterministic `backtest-v1` runner consumes those snapshots, calls existing S1-S4 unchanged, executes only on the next candle, maintains isolated long-only accounting, persists trades/equity, and computes evidence metrics.

**Tech Stack:** Python, FastAPI, SQLModel/SQLite, Decimal, httpx, pytest, existing React/Vite client conventions.

**Spec:** `docs/superpowers/specs/2026-08-19-phase-5-backtesting-evidence-design.md`

## Global Constraints

- Work directly on `main`; no PR/branch unless explicitly requested.
- Do not modify S1-S4 algorithms to improve results.
- Real historical data only; no synthetic/mock fallback in production historical provider.
- Backtest state must not mutate Paper accounts, PaperExecution, PaperRequest, RiskDecision or legacy Trade evidence.
- Signal at candle `t` may execute no earlier than candle `t+1`.
- `backtest-v1` is long-only, no pyramiding, MARKET-like deterministic fills, default 10 bps adverse slippage and 10 bps fee.
- Persist undefined metrics as null, not zero/fabricated values.
- No Live capability, optimizer or automatic agent execution.
- Never claim executable verification without fresh exact-HEAD output.

---

### Task 1: Persist immutable historical datasets

**Files:**
- Create: `backend/app/models/backtesting.py`
- Create: `backend/app/backtesting/__init__.py`
- Create: `backend/app/backtesting/datasets.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_backtest_dataset.py`

**Interfaces:**
- Produces: `BacktestDataset`, `BacktestCandle`, `canonical_dataset_sha256(candles)`, `persist_dataset(session, ...)`.

- [ ] Write tests proving canonical SHA equality for identical candle content and rejection of gaps, duplicate/out-of-order/open-window data.
- [ ] Implement SQLModel dataset/candle records and deterministic JSON serialization of normalized candle fields.
- [ ] Implement validation and immutable persistence; a READY dataset cannot be overwritten.
- [ ] Review that persistence contains provider/symbol/interval/requested and actual windows plus hash/count.
- [ ] Commit dataset domain.

### Task 2: Add paginated real historical Binance provider

**Files:**
- Create: `backend/app/backtesting/providers/__init__.py`
- Create: `backend/app/backtesting/providers/binance_history.py`
- Test: `backend/tests/test_backtest_history_provider.py`

**Interfaces:**
- Produces: `BinanceHistoricalDataProvider.fetch_candles(symbol, interval, start, end) -> list[Candle]`.
- Consumes: Phase 1 `Candle`, normalization and interval helpers.

- [ ] Write fixture tests for pagination, closed-candle filtering, millisecond UTC parsing and provider failure.
- [ ] Implement public read-only `/api/v3/klines` pagination using `startTime`, `endTime`, bounded 1000-row pages and no credentials.
- [ ] Ensure 429/5xx/timeouts fail closed with bounded retries and never return generated candles.
- [ ] Validate final contiguous series through dataset validation before persistence.
- [ ] Commit provider.

### Task 3: Build isolated deterministic backtest accounting/execution

**Files:**
- Create: `backend/app/backtesting/execution.py`
- Test: `backend/tests/test_backtest_execution.py`

**Interfaces:**
- Produces: `BacktestLedger`, `BacktestFill`, `BacktestExecutionPolicy`, deterministic `buy`, `sell`, `mark`, `force_close` operations.

- [ ] Write tests for capital conservation, long-only flat/long state transitions, fee/slippage, no pyramiding, oversell prevention and final close.
- [ ] Implement Decimal-only isolated ledger using the same cash/cost-basis/PnL invariants as AccountingService without creating active portfolio rows.
- [ ] Default `BacktestExecutionPolicy(version='backtest-v1', slippage_bps=10, fee_bps=10, position_fraction=0.25)`.
- [ ] Ensure buy sizing reserves compounded slippage+fee exactly and cannot create negative cash.
- [ ] Commit execution layer.

### Task 4: Implement no-look-ahead runner and persistence

**Files:**
- Extend: `backend/app/models/backtesting.py`
- Create: `backend/app/backtesting/runner.py`
- Test: `backend/tests/test_backtest_runner.py`

**Interfaces:**
- Produces: `BacktestRun`, `BacktestTrade`, `BacktestEquityPoint`, `BacktestRunner.run(dataset_id, strategy_id, config) -> BacktestRun`.
- Consumes: `get_strategy`, immutable dataset candles, isolated execution.

- [ ] Write a fixture where a BUY signal occurs on candle `t` and assert fill timestamp/market price come from `t+1` open only.
- [ ] Write deterministic duplicate-run test asserting identical trades/equity/metrics for identical config/dataset.
- [ ] Implement chronological loop: signal on close history through t, execute pending intent at next candle open, then mark equity at that candle close.
- [ ] BUY only while flat; SELL only while long; ignore non-actionable duplicate signals rather than inventing trades.
- [ ] Force-close any final open position at final close and persist `DATASET_END_EXIT`.
- [ ] Mark invariant failures as `INVALID` with reason rather than COMPLETED.
- [ ] Commit runner.

### Task 5: Compute machine-readable evidence metrics

**Files:**
- Create: `backend/app/backtesting/metrics.py`
- Test: `backend/tests/test_backtest_metrics.py`

**Interfaces:**
- Produces: `BacktestMetrics`, `compute_metrics(...)`.

- [ ] Write fixed-ledger tests for final equity, net PnL/return, wins/losses, average win/loss, expectancy, profit factor, maximum drawdown, fees, exposure fraction and forced exits.
- [ ] Define null profit factor when gross loss is zero and null win rate/averages when no completed round trips exist.
- [ ] Compute drawdown from persisted chronological equity high-water series.
- [ ] Persist metrics onto BacktestRun after successful run.
- [ ] Commit metrics.

### Task 6: Add Backtesting API and startup safety

**Files:**
- Create: `backend/app/backtesting/router.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_backtest_api.py`
- Modify: `backend/tests/test_api_integration.py`

**Interfaces:**
- Mount `/api/backtests` status/datasets/runs surfaces.

- [ ] Test status reports historical real-only, deterministic, no Live capability.
- [ ] Test POST dataset uses provider internally and client cannot inject arbitrary candles as real evidence.
- [ ] Test POST run rejects missing/non-READY dataset and unknown strategy.
- [ ] Test GET dataset/run returns hashes, config and metrics/provenance.
- [ ] On startup mark stale `RUNNING` backtests `INVALID`/`INTERRUPTED` rather than treating them as valid evidence.
- [ ] Mount router and bump truthful runtime metadata without enabling automation.
- [ ] Commit API/startup boundary.

### Task 7: Reconcile UI/client and evidence documentation

**Files:**
- Modify: `frontend/src/lib/api.js`
- Modify: `frontend/src/pages/SettingsPage.jsx`
- Modify: `frontend/src/pages/SettingsPage.test.jsx`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `IMPLEMENTATION_PLAN.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/BACKTESTING.md`
- Modify: `docs/METRICS_AND_EVIDENCE.md`
- Modify: `docs/STRATEGIES.md`
- Modify: `docs/DATABASE_ARCHITECTURE.md`
- Modify: `GEMINI.md`
- Modify: `QWEN.md`

- [ ] Add read/run Backtesting client methods but no optimizer UI.
- [ ] Settings reports Phase 5 evidence boundary truthfully; does not claim strategies profitable/validated.
- [ ] Document dataset immutability/hash, next-candle execution, forced end exits, costs and metric null semantics.
- [ ] Mark S1-S4 as backtest-capable only after runner implementation; performance remains unverified until actual runs exist.
- [ ] Mark Phase 5 source/static gate complete only after final audit.
- [ ] Commit documentation/UI contract.

### Task 8: Exact-HEAD validation and optional real S1-S4 baseline

**Files:**
- No production change unless a defect is discovered.
- If real baseline executes, persist results only through normal Backtest records; do not hardcode metrics into strategy docs.

- [ ] Compare final HEAD to Phase 4 baseline `4014e19714a211ed8c61be40f08ede5e78407d21` and inspect every changed file for scope.
- [ ] Search for synthetic fallback, same-candle fill, optimizer, Live or active-agent automation regressions.
- [ ] Run `cd backend && pytest tests/ -v` on exact HEAD when execution is available.
- [ ] Run `cd frontend && npm test` and `npm run build` on exact HEAD when available.
- [ ] If real provider execution is available, create one common BTC/USDT dataset and run S1-S4 under identical `backtest-v1` assumptions; report observed results as baseline evidence only.
- [ ] If execution/provider is unavailable, record certification/baseline as pending and do not invent numbers.
- [ ] Finalize Phase 5 gate status in roadmap/implementation plan if needed.
