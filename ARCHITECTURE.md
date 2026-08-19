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
8. New financial state is authoritative only through the Phase 2 accounting domain; strategies, lifecycle code and UI must not mutate competing balances.
9. Paper mutations are idempotent and fail closed on ambiguous recovery state.

## Target domains

### Market Data
Owns provider access, timestamps, candles, quotes, symbol normalization, gaps, retries and data quality. It produces immutable market observations; it never decides trades.

The active Phase 1 implementation is `backend/app/market_data/`:

- `contracts.py`: immutable real `Quote` and `Candle` contracts;
- `quality.py`: symbol/UTC/freshness/gap/order validation;
- `service.py`: provider-neutral `MarketDataService`;
- `providers/binance_public.py`: first read-only real provider;
- `router.py`: `/api/market-data` boundary.

`BinancePublicMarketDataProvider` uses public REST only. It has no API keys, account methods or execution methods. Errors never produce generated replacement prices.

### Strategy / Signals
Consumes market observations and produces deterministic, inspectable intents or signals. Strategy logic must not mutate portfolio balances or call an exchange directly.

### Risk
Receives a proposed order plus account/portfolio state and decides whether it is allowed and at what size. It owns exposure limits, drawdown controls, position sizing, stop requirements and circuit breakers.

Automated strategy execution remains blocked until this independent Risk domain exists. The current Phase 3 Paper surface is operator-only.

### Execution
The active Phase 3 implementation is `backend/app/paper_execution/` plus `backend/app/models/paper_execution.py`.

Paper execution currently supports operator-originated MARKET BUY/SELL only. It:

- obtains the price from the real Market Data contract; the client cannot provide a fill price;
- rejects stale/future/non-real quotes;
- applies deterministic adverse slippage and fees through versioned policy `paper-v1`;
- records provider/timestamp/market-price/fill-price provenance in `PaperExecution`;
- requires persistent `request_id` idempotency through `PaperRequest`;
- delegates every accepted financial effect to `AccountingService`;
- has no exchange credentials, account APIs or Live adapter.

The first policy is deliberately simple rather than exchange-grade: full-fill MARKET semantics, 10 bps adverse slippage and 10 bps fee. More realistic execution is future work only when evidence justifies it.

Recovery is conservative. A pending execution is never resubmitted. An already-completed fill may be linked when unambiguous; an unfilled pending execution is cancelled; ambiguous states become `RECOVERY_REQUIRED`. A request interrupted before execution linkage also becomes `RECOVERY_REQUIRED` rather than retryable because an `Order` may already have been persisted.

### Portfolio & Accounting
The active Phase 2 implementation is `backend/app/accounting/` plus `backend/app/models/accounting.py`.

It is the single source of truth for new financial work:

- `Account`: funded capital, cash, reserve, realized PnL and cumulative fees;
- `Order`: requested BUY/SELL lifecycle;
- `Fill`: persisted execution fact for Paper/Backtest consumers;
- `Position`: long quantity, average cost and realized PnL;
- `LedgerEntry`: explicit funding events;
- `AccountingService`: account/order/fill mutation, snapshots and reconciliation;
- `ensure_accounting_baseline`: idempotent migration of pre-Phase-2 agents;
- read-only `/api/accounting/agents/{agent_id}` inspection API.

Phase 2 is deliberately long-only. Shorts, leverage and margin are undefined and therefore rejected by design rather than guessed.

Accounting invariants include:

`equity = cash + market_value(open_positions)`

and

`equity = funded_capital + realized_pnl + unrealized_pnl`

Buy fees are embedded in acquisition basis; sell fees reduce realized proceeds. Deposits affect funded capital/cash, never PnL.

`Agent.presupuesto_inicial` and `Agent.presupuesto_actual` remain temporary compatibility mirrors. They are not the source of truth for future execution/accounting.

### Agent Lifecycle
Owns agent identity, assigned strategy/configuration, status, death, replication, lineage and future mutation. Lifecycle changes must not erase accounting records. Replication is currently blocked because the historical implementation duplicated parent capital; Phase 6 must define an explicit transfer/allocation policy before replication returns.

### Metrics & Evidence
Computes comparable performance from persisted accounting/equity observations. It records provenance and never mixes results from different modes. Legacy `Trade` rows remain historical/non-evidence records. `PaperExecution` records are valid Paper provenance, but broad strategy-performance claims still require sufficient runs and the later evidence/backtesting phases.

### API / UI / Monitoring
Observes and controls the domains through explicit contracts. UI must show missing data as missing rather than fabricate substitutes.

The active Paper surface is:

- `GET /api/paper/status`;
- `POST /api/paper/orders/market` (operator-only, `request_id` required);
- `GET /api/paper/executions`.

Ops Monitor reads `paper_executions` for the Paper feed. Legacy `Trade` rows remain separate historical records and are not mixed into Paper evidence.

## Data flow

```text
Provider -> Market Data -> Strategy -> Risk -> Paper Execution
                                      |             |
                                      v             v
                                  Accounting <--- Fills
                                      |
                                      v
                               Metrics / Evidence
                                      |
                                      v
                              Agent Lifecycle + UI
```

At the current Phase 3 boundary, the automated `Strategy -> Risk -> Paper Execution` path is not active. Operators can exercise `Market Data -> Paper Execution -> Accounting` explicitly so the execution/accounting infrastructure can be validated before automation.

## Current runtime versus target

`backend/app/main.py` mounts SQLModel agents/trades/crypto, real-only `/api/market-data`, read-only `/api/accounting`, and operator-only `/api/paper`. It **does not start an autonomous trading engine**.

The runtime remains mode `transition` and reports:

- `market_data=real_contract_available`;
- `accounting=authoritative_phase_2`;
- `paper_trading=operator_only_phase_3`;
- `automated_trading=blocked_until_risk`;
- `live_execution=disabled`.

On startup, pre-Phase-2 agents without an account are bootstrapped from `presupuesto_inicial` only. Then Paper execution and idempotency reservations are reconciled conservatively before new commands are accepted.

The existing `/api/crypto` CoinGecko router remains a UI-oriented real-data surface. It is not the trading-domain Market Data contract. Paper code consumes `MarketDataService`.

The pre-provenance `Trade` table is preserved for historical inspection. Existing rows remain `legacy_unclassified` and are not promoted into the new Order/Fill/PaperExecution chain.

## Synthetic isolation

Synthetic code may be invoked only explicitly by tests or dedicated future test harnesses. It must not:

- start from the normal FastAPI lifespan;
- write evidence that is indistinguishable from Paper;
- feed dashboard Paper/Backtest metrics;
- provide a silent fallback for real market-data failures;
- mutate the authoritative accounting domain.

The legacy `BinanceService` remains unmounted and is not used by the Market Data layer.

## Persistence state

Implemented active records now include:

- portfolio accounts;
- orders;
- fills;
- positions;
- funding ledger;
- Paper execution provenance;
- Paper idempotency reservations.

Future phases may add persisted equity snapshots, strategy configuration/version, risk decisions and run/session identity. Those are added only when their owning domain is implemented.

## Live boundary

Future Live trading uses the same upstream strategy/risk/accounting concepts but a different execution adapter and additional authorization/safety controls. No Paper test, UI control or environment default may implicitly activate Live.

## Verification

Architecture claims are considered execution-verified only when code, tests and fresh execution evidence agree. Static source review may establish contract coherence but does not substitute for running the repository gate.
