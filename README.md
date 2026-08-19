# AUTOMATON

AUTOMATON is a local platform for developing, testing and evaluating autonomous crypto-trading agents.

## Product contract

The immediate product goal is **Paper Trading with real market data and virtual capital**, supported by reproducible historical evidence. Synthetic/Test, Backtest, Paper and Live are separate evidence modes. Synthetic/random/mock activity must never be presented as Backtest, Paper or Live performance.

## Current runtime

The active stack is FastAPI + SQLModel + SQLite with React/Vite. `backend/app/main.py` and `frontend/src/App.jsx` remain the authority for what actually runs.

Current runtime contracts:

- synthetic `AgentEngine`: disabled from normal startup;
- Market Data: provider-neutral, real-only, fail-closed;
- Accounting: authoritative long-only financial source of truth for Paper;
- Paper: operator-only MARKET BUY/SELL against real quotes;
- Risk: mandatory persistent `risk-v1` gate for normal Paper execution;
- Backtesting: immutable real historical datasets + deterministic `backtest-v1` evidence + strategy-source fingerprint;
- automated strategy/agent execution: **not enabled yet**;
- Live execution: disabled and structurally separate.

Historical pre-provenance `Trade` rows remain `legacy_unclassified` and are excluded from valid Paper/Backtest evidence.

## Implemented phases

### Phase 1 — Real Market Data

`backend/app/market_data/` provides real Quotes/closed Candles, UTC/provider provenance, symbol normalization, stale/gap/order validation and bounded retry behavior. The active public Binance provider has no trading credentials or execution methods and never substitutes generated prices.

### Phase 2 — Portfolio & Accounting

`backend/app/accounting/` owns Account, Order, Fill, Position and LedgerEntry state plus funded capital, cash, fees, realized/unrealized PnL, equity and reconciliation. Existing agents bootstrap from funded/initial capital only so old synthetic PnL is not promoted.

### Phase 3 — Paper Execution

`backend/app/paper_execution/` provides deterministic virtual execution with current real quotes, virtual capital, MARKET BUY/SELL, `paper-v1`, 10 bps adverse slippage, 10 bps fee, persistent execution provenance, request-id idempotency and conservative recovery. All accepted financial mutation is delegated to Accounting.

### Phase 4 — Risk Engine

`backend/app/risk/` is an independent persistent authorization layer. `risk-v1` limits order size, exposure, concentration, open positions, realized loss and drawdown, requires trustworthy market/accounting state and provides a persistent pause/resume circuit breaker.

Every normal Paper order is resolved through:

```text
request_id -> real Market Data -> RiskDecision -> PaperExecution -> Accounting
```

A successful Paper execution requires a matching persisted one-time ALLOW. BUY reserves the exact current `paper-v1` compounded execution cost (**20.01 bps**). Risk-reducing SELL can reduce an existing long without depending on unrelated market marks, while still requiring structural integrity and no oversell.

### Phase 5 — Backtesting & Evidence

`backend/app/backtesting/` provides a separate historical-evidence path:

```text
real historical candles -> immutable SHA-256 dataset -> S1-S4 signal -> next-candle execution -> isolated ledger -> persisted trades/equity/metrics
```

Important contracts:

- historical Binance access is public/read-only and fails closed;
- datasets are immutable snapshots with provider/symbol/interval/window/count/SHA-256 provenance;
- mixed providers, gaps, duplicates and ordering errors are rejected;
- a signal produced from candle `t` can execute no earlier than candle `t+1` open;
- `backtest-v1` is deterministic, long-only, no pyramiding, default 10 bps adverse slippage + 10 bps fee;
- BUY allocates a persisted configurable fraction of capital (default 25%);
- open positions are explicitly liquidated at dataset end and labelled `DATASET_END_EXIT`;
- Backtest state does not create or mutate active Paper Account/PaperExecution/RiskDecision records;
- every new run persists a SHA-256 fingerprint of the active strategy source in `BacktestRunEvidence`;
- older runs without that fingerprint remain readable but are not retroactively given missing provenance;
- runs persist configuration, trades, equity series and machine-readable metrics;
- undefined metrics remain null;
- interrupted RUNNING backtests become INVALID on restart rather than valid evidence;
- no parameter optimizer exists in Phase 5.

S1-S4 algorithms are **unchanged**. Backtesting capability does not mean any strategy is profitable, optimized or validated. Performance claims require observed reproducible runs.

## Active APIs relevant to the trading core

- `/api/market-data/*`
- `/api/accounting/agents/{agent_id}`
- `/api/risk/*`
- `/api/paper/*`
- `/api/backtests/status`
- `/api/backtests/datasets`
- `/api/backtests/datasets/{id}`
- `/api/backtests/runs`
- `/api/backtests/runs/{id}`

No active Live, strategy-automation-start or backtest-optimizer endpoint exists.

## Documentation source of truth

- [Product contract](docs/PRODUCT_CONTRACT.md)
- [Architecture](ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Market data](docs/MARKET_DATA.md)
- [Paper trading](docs/PAPER_TRADING.md)
- [Portfolio and accounting](docs/PORTFOLIO_ACCOUNTING.md)
- [Risk management](docs/RISK_MANAGEMENT.md)
- [Strategies](docs/STRATEGIES.md)
- [Backtesting](docs/BACKTESTING.md)
- [Metrics and evidence](docs/METRICS_AND_EVIDENCE.md)
- [Agent lifecycle](docs/AGENT_LIFECYCLE.md)
- [Live trading gate](docs/LIVE_TRADING_GATE.md)
- [Legacy transition audit](docs/LEGACY_AUDIT.md)

## Development order

The project advances by dependency: real market data → accounting → paper execution → risk → backtesting/evidence → agent evolution → 24/7 Paper → strategy research → live-readiness.

## Running

```bash
npm run setup
npm run dev
```

Backend: `127.0.0.1:8000`  
Frontend: `localhost:5173`

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

**Phase 5 source/contract/static gate is complete.** Execution certification and real-provider S1-S4 baseline evidence remain pending until fresh exact-HEAD commands/runs are observed. Never claim strategy results or a green repository gate without that evidence.
