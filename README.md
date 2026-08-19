# AUTOMATON

AUTOMATON is a local platform for developing, testing and evaluating autonomous crypto-trading agents.

## Product contract

The immediate product goal is **autonomous Paper Trading with real market data and virtual capital**, supported by reproducible historical evidence and explicit safety/evolution gates. Synthetic/Test, Backtest, Paper and Live remain separate evidence modes.

## Current runtime

Active stack: FastAPI + SQLModel + SQLite with React/Vite.

- synthetic `AgentEngine`: disabled from normal startup;
- Market Data: real-only, provider-neutral and fail-closed;
- Accounting: authoritative financial source for active Paper state;
- Paper: operator-only MARKET execution against real quotes;
- Risk: persistent mandatory `risk-v1` authorization gate;
- Backtesting: immutable real historical datasets, deterministic `backtest-v1` and strategy-source SHA-256 evidence;
- Agent Evolution: persistent `evolution-v1` fitness, lineage/lifecycle evidence and manual non-duplicating replication;
- automated strategy execution: **blocked until Phase 7 runtime**;
- Live execution: disabled and structurally separate.

Legacy pre-provenance `Trade` rows remain excluded from valid Paper/Backtest/fitness evidence.

## Implemented core

### Phase 1 — Real Market Data

`backend/app/market_data/` provides real Quotes/closed Candles, UTC/provider provenance, symbol normalization, quality validation and bounded retry behavior with no generated fallback.

### Phase 2 — Portfolio & Accounting

`backend/app/accounting/` owns Account, Order, Fill, Position and LedgerEntry state, funded capital, cash, fees, PnL/equity and reconciliation. Phase 6 extends Accounting with an atomic funded-liquid parent→child transfer that conserves capital.

### Phase 3 — Paper Execution

`backend/app/paper_execution/` provides deterministic virtual MARKET BUY/SELL against current real quotes, persistent provenance, request-id idempotency and conservative recovery. Accepted financial mutation always flows through Accounting.

### Phase 4 — Risk Engine

`backend/app/risk/` persists versioned ALLOW/REJECT decisions and enforces size/exposure/loss/drawdown/data/accounting/recovery gates plus a pause/resume circuit breaker before Paper financial state can be created.

### Phase 5 — Backtesting & Evidence

`backend/app/backtesting/` freezes immutable real historical datasets and executes S1-S4 deterministically with signal on candle `t` and execution no earlier than `t+1`. Runs persist dataset SHA, strategy-source SHA, costs, trades, equity and metrics in an evidence path isolated from Paper.

S1-S4 are still baseline algorithms, not proven profitable strategies. Real-provider baseline performance remains unobserved until an executable/provider run exists.

### Phase 6 — Agent Evolution

`backend/app/agent_evolution/` makes replication evidence-aware.

`evolution-v1` currently requires:

- active agent;
- matching completed Backtest with source fingerprint still equal to current strategy source;
- at least 5 Backtest round trips;
- positive Backtest net return and expectancy;
- Backtest max drawdown <= 15%;
- at least 3 agent-specific FILLED Paper SELL executions with real `PaperExecution` provenance;
- positive authoritative Paper realized PnL;
- structurally valid Accounting;
- no `RECOVERY_REQUIRED` Paper request.

Every replication attempt creates a fresh fitness evaluation. Legacy `Trade` rows and unprovenanced fills never count.

A successful manual replication transfers 25% of eligible parent capital:

`eligible = min(cash - reserved_cash, funded_capital)`

The parent loses exactly the amount the flat child receives. Paired `CAPITAL_TRANSFER_OUT/IN` ledger entries, lineage, generation, strategy version/source fingerprint and lifecycle reasons are persisted. The parent remains ACTIVE. No strategy mutation or automatic replication is enabled.

## Active APIs

- `/api/market-data/*`
- `/api/accounting/*`
- `/api/risk/*`
- `/api/paper/*`
- `/api/backtests/*`
- `/api/evolution/status`
- `/api/evolution/policies/active`
- `/api/evolution/agents/{agent_id}/fitness`
- `/api/evolution/agents/{agent_id}/lineage`
- `/api/agents/{agent_id}/replicate`

No active Live, autonomous-trading-start, auto-replication or backtest-optimizer endpoint exists.

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

## Development order

real market data → accounting → paper execution → risk → backtesting/evidence → agent evolution → **24/7 Paper** → strategy research → legacy pruning → live-readiness.

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

Source/static gates are not runtime certification. Never claim a strategy result, fitness quality or green repository state without fresh exact-HEAD execution evidence.
