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

The legacy `AgentEngine` still exists as explicit Synthetic/Test utility code, but **the normal application runtime does not start it**. Synthetic/random execution is isolated from the active financial path.

Historical `Trade` rows created before evidence provenance existed remain `legacy_unclassified` and are excluded from verified Paper metrics.

### Phase 1 — Real Market Data

`backend/app/market_data/` provides the provider-neutral real-only market-data boundary. The initial `BinancePublicMarketDataProvider` uses public read-only Binance market endpoints without trading credentials or execution capability. Quotes/candles carry provider provenance and UTC timestamps; stale, gapped, malformed or unavailable data fails closed and is never replaced by synthetic values.

### Phase 2 — Portfolio & Accounting

`backend/app/accounting/` is the authoritative long-only financial layer: Account, Order, Fill, Position and LedgerEntry records plus deterministic cash/PnL/fees/equity/reconciliation rules. New agents and deposits use this layer. Historical agents are bootstrapped from funded/initial capital only so old synthetic PnL is not promoted.

Manual replication remains blocked because the previous implementation duplicated parent capital into a child. It returns only after Agent Evolution defines an explicit non-duplicating allocation policy.

### Phase 3 — Paper Execution

Paper execution is now implemented as an **operator-only** boundary under `/api/paper`:

- current real market Quote;
- virtual capital only;
- MARKET BUY/SELL;
- deterministic `paper-v1` fill policy;
- 10 bps adverse slippage;
- 10 bps fee;
- persistent PaperExecution provenance;
- required persistent `request_id` idempotency;
- conservative restart recovery;
- every financial effect delegated to Phase 2 Accounting;
- Ops Monitor displays Paper execution provenance rather than legacy Trade data.

The runtime reports `paper_trading=operator_only_phase_3`, `automated_trading=blocked_until_risk` and `live_execution=disabled`.

**Agents do not trade autonomously yet.** The next development domain is Phase 4 Risk. Strategy/agent-generated orders must not reach Paper Execution until Risk can approve sizing/exposure and fail closed on unsafe state.

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

Live execution, if it is ever enabled, must be a separate adapter behind explicit safety gates. Paper code cannot spend real funds.

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

Authentication, payments, chat, monetization and other peripheral capabilities remain outside the current core unless needed by the trading product.

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

Phase 3 is source/contract implemented, but the current environment has not produced fresh executable evidence for the exact HEAD. Never describe a HEAD as execution-verified without fresh command output for that exact HEAD.
