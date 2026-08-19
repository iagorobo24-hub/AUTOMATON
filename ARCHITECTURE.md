# AUTOMATON Architecture

## Objective

AUTOMATON is being rebuilt around one core path: autonomous agents trading with **real market data and virtual capital** until the system has enough evidence and safeguards to consider any Live mode.

## Non-negotiable boundaries

1. Synthetic data is test-only and must be labelled synthetic.
2. Backtest and Paper use real market data.
3. Paper uses virtual funds only.
4. Live execution is a separate future adapter and cannot be enabled by toggling a Paper flag.
5. Every financial metric must identify its evidence mode: synthetic, backtest, paper or live.
6. SQLModel/SQLite remains the active persistence baseline unless a later architecture decision deliberately changes it.
7. Historical Mongo services are not reactivated as shortcuts.

## Target domains

### Market Data
Owns provider access, timestamps, candles, quotes, symbol normalization, gaps, retries and data quality. It produces immutable market observations; it never decides trades.

### Strategy / Signals
Consumes market observations and produces deterministic, inspectable intents or signals. Strategy logic must not mutate portfolio balances or call an exchange directly.

### Risk
Receives a proposed order plus account/portfolio state and decides whether it is allowed and at what size. It owns exposure limits, drawdown controls, position sizing, stop requirements and circuit breakers.

### Execution
Paper execution converts approved orders into simulated fills against real market observations. Fees, slippage, order state and fill assumptions must be explicit and reproducible where possible.

### Portfolio & Accounting
Single source of truth for cash, positions, cost basis, realized PnL, unrealized PnL, equity, exposure and fees. Strategies and UI do not calculate competing balances.

### Agent Lifecycle
Owns agent identity, assigned strategy/configuration, status, death, replication, lineage and future mutation. Replication must eventually depend on evidence quality, not a single short-term balance threshold.

### Metrics & Evidence
Computes comparable performance from persisted trades/equity observations. It records provenance and never mixes results from different modes.

### API / UI / Monitoring
Observes and controls the domains through explicit contracts. UI must show missing data as missing rather than fabricate substitutes.

## Data flow

```text
Provider -> Market Data -> Strategy -> Risk -> Paper Execution
                                      |             |
                                      v             v
                                  Portfolio <--- Fills
                                      |
                                      v
                               Metrics / Evidence
                                      |
                                      v
                              Agent Lifecycle + UI
```

## Current runtime versus target

`backend/app/main.py` currently mounts SQLModel agents/trades/crypto but **does not start a trading engine**. The old `AgentEngine` remains versioned only as explicit Synthetic/Test utility code and is not reachable from normal startup.

The current runtime reports mode `transition`; Paper is `not_implemented`. `/api/estado` intentionally exposes no generated prices or PnL.

The pre-provenance `Trade` table is preserved for historical inspection. Existing rows are surfaced as `legacy_unclassified` with `evidence_valid=false`; verified financial metrics remain unavailable until future Backtest/Paper records carry explicit provenance.

`frontend/src/App.jsx` exposes Dashboard, Crypto, Ops Monitor, Agents and Settings. Dashboard/Agents show financial metrics as `N/D` while evidence is unavailable. Ops Monitor labels existing rows as historical non-Paper records.

## Synthetic isolation

Synthetic code may be invoked only explicitly by tests or dedicated future test harnesses. It must not:

- start from the normal FastAPI lifespan;
- write evidence that is indistinguishable from Paper;
- feed dashboard Paper/Backtest metrics;
- provide a silent fallback for real market-data failures.

The legacy `BinanceService` violates the last rule because it falls back to generated data. It remains unmounted and must not become the Phase 1 provider without redesign.

## Persistence target

SQLModel should evolve from current `Agent` and legacy `Trade` tables toward explicit entities for at least:

- market observations/cache metadata where persistence is needed;
- orders;
- fills;
- positions;
- account/equity snapshots;
- strategy configuration/version;
- risk decisions/events;
- agent lineage/evidence summaries.

Exact schemas are implementation decisions made phase by phase. The accounting invariant is more important than mirroring the historical Mongo schema.

## Live boundary

Future Live trading uses the same upstream strategy/risk concepts but a different execution adapter and additional authorization/safety controls. No Paper test, UI control or environment default may implicitly activate Live.

## Verification

Architecture claims are considered execution-verified only when code, tests and fresh execution evidence agree. Static source review may establish contract coherence but does not substitute for running the repository gate.
