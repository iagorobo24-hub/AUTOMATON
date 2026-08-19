# AUTOMATON

AUTOMATON is a local platform for developing, testing and evaluating autonomous crypto-trading agents.

## Product contract

The immediate product goal is **Paper Trading with real market data and virtual capital**. Synthetic/Test, Backtest, Paper and Live are separate evidence modes. Synthetic/random/mock activity must never be presented as Paper, Backtest or Live performance.

## Current runtime

The active stack is FastAPI + SQLModel + SQLite with React/Vite. `backend/app/main.py` and `frontend/src/App.jsx` remain the authority for what actually runs.

Current runtime contracts:

- synthetic `AgentEngine`: disabled from normal startup;
- Market Data: provider-neutral, real-only, fail-closed;
- Accounting: authoritative long-only financial source of truth;
- Paper: operator-only MARKET BUY/SELL against real quotes;
- Risk: mandatory persistent `risk-v1` gate for active Paper API orders;
- automated strategy/agent execution: **not enabled yet**;
- Live execution: disabled and structurally separate.

Historical pre-provenance `Trade` rows remain `legacy_unclassified` and are excluded from verified Paper metrics.

## Implemented phases

### Phase 1 — Real Market Data

`backend/app/market_data/` provides real Quotes/closed Candles, UTC/provider provenance, symbol normalization, stale/gap/order validation and bounded retry behavior. The initial Binance public provider has no trading credentials or execution methods and never substitutes generated prices.

### Phase 2 — Portfolio & Accounting

`backend/app/accounting/` owns Account, Order, Fill, Position and LedgerEntry state plus funded capital, cash, fees, realized/unrealized PnL, equity and reconciliation. Existing agents bootstrap from funded/initial capital only so old synthetic PnL is not promoted.

### Phase 3 — Paper Execution

`backend/app/paper_execution/` provides deterministic virtual execution:

- current real quote;
- virtual capital only;
- MARKET BUY/SELL;
- `paper-v1` full-fill-or-reject model;
- 10 bps adverse slippage;
- 10 bps fee;
- persistent `PaperExecution` provenance;
- required `request_id` idempotency;
- conservative restart/recovery;
- all financial mutation delegated to Accounting.

### Phase 4 — Risk Engine

`backend/app/risk/` is now an independent persistent authorization layer.

The active `risk-v1` profile defaults to:

- max order notional: 250 USDT;
- max order/equity: 25%;
- max total exposure/equity: 60%;
- max symbol exposure/equity: 35%;
- max open positions: 4;
- max realized loss/funded capital: 10%;
- max drawdown: 15%;
- max quote age: 30 seconds.

Every active `POST /api/paper/orders/market` request is resolved in this order:

```text
request_id -> real Market Data -> RiskDecision -> PaperExecution -> Accounting
```

Risk decisions persist ALLOW/REJECT, profile/version, market provenance, requested notional, equity/exposure state and reason codes. ALLOW decisions are one-time consumable and linked to their Paper execution. A REJECT creates no Paper Order/Fill.

`POST /api/risk/pause` and `/resume` provide a persistent circuit breaker. There is no public endpoint that can fabricate an approval.

**Agents still do not trade autonomously.** Risk is now available, but the future Strategy/Signal integration must explicitly submit intents through this gate before automation can be enabled.

## Active APIs relevant to the trading core

- `/api/market-data/*`
- `/api/accounting/agents/{agent_id}`
- `/api/risk/status`
- `/api/risk/profiles/active`
- `/api/risk/decisions`
- `/api/risk/pause`
- `/api/risk/resume`
- `/api/paper/status`
- `/api/paper/orders/market`
- `/api/paper/executions`

No active Live or automatic-trading start endpoint exists.

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
- [Agent lifecycle](docs/AGENT_LIFECYCLE.md)
- [Metrics and evidence](docs/METRICS_AND_EVIDENCE.md)
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

Phase 4 may be source/contract complete without being execution-certified. Never call a HEAD green without fresh command output for that exact HEAD.
