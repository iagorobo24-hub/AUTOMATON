# AUTOMATON

AUTOMATON is a local platform for developing, testing and evaluating autonomous crypto-trading agents.

## Product contract

The immediate product goal is **Paper Trading with real market data and virtual capital**. Paper results are valid only when decisions are driven by real market observations and execution is simulated under explicit rules.

AUTOMATON distinguishes four modes:

| Mode | Market data | Capital | Purpose |
|---|---|---|---|
| Synthetic/Test | synthetic | virtual | deterministic technical tests only |
| Backtest | historical real data | virtual | reproducible strategy evaluation |
| Paper | current real data | virtual | forward validation of agents and operations |
| Live | current real data | real | future production mode, gated and disabled until explicitly approved |

Synthetic prices, random fills or mock telemetry must never be presented as Paper, Backtest or Live performance.

## Current transition state

The active runtime is FastAPI + SQLModel + SQLite with React/Vite. `backend/app/main.py` and `frontend/src/App.jsx` remain the authority for what runs today.

The legacy `AgentEngine` still exists as explicit Synthetic/Test utility code, but **the normal application runtime no longer starts it**. `/health` and `/api/estado` identify the runtime as `transition`, report the synthetic engine as disabled and do not publish synthetic price/PnL telemetry.

Historical `Trade` rows created before evidence provenance existed are preserved but classified as `legacy_unclassified`. They are excluded from verified PnL, Win Rate, ROI and trade-count metrics instead of being silently promoted into future Paper evidence.

Paper Trading itself is **not implemented yet**. The next phase is Real Market Data.

## Target architecture

```text
Real Market Data
      ↓
Strategy / Signal Engine
      ↓
Risk Engine
      ↓
Paper Execution Engine
      ↓
Portfolio & Accounting
      ↓
Agent Lifecycle / Evolution
      ↓
Metrics & Evidence
      ↓
API / UI / Monitoring
```

Live execution, if it is ever enabled, must be a separate adapter behind explicit safety gates. Paper code must not be able to spend real funds accidentally.

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

The project should advance by dependency, not by visual polish: real market data → accounting → paper execution → risk → backtesting/evidence → agent evolution → 24/7 paper operation → strategy research → live-readiness.

Authentication, payments, chat, monetization and other peripheral capabilities are outside the current core unless they become necessary for the trading product.

## Running the current app

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

Never describe a HEAD as execution-verified without fresh command output for that exact HEAD.
