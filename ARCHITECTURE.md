# AUTOMATON Architecture

## Objective

AUTOMATON is built around autonomous-agent research using **real market data and virtual capital** until explicit evidence/safety gates justify any future Live mode.

## Non-negotiable boundaries

1. Synthetic data is test-only and must be labelled synthetic.
2. Backtest and Paper use real market data.
3. Paper uses virtual funds only.
4. Live execution is a separate future adapter; it cannot be enabled by toggling Paper.
5. Financial evidence carries its mode/provenance.
6. SQLModel/SQLite is the active persistence baseline.
7. Legacy Mongo/trading services are not reactivated as shortcuts.
8. Accounting is the only active financial authority.
9. Paper mutations are idempotent and fail closed on ambiguous recovery.
10. Every normal Paper execution requires a persisted Phase 4 Risk ALLOW decision before financial state is created.

## Active domains

### Market Data — Phase 1

`backend/app/market_data/` owns provider access, real Quote/Candle contracts, UTC/provenance, symbol normalization, freshness/gaps/order validation and bounded retries. It never decides trades or executes orders.

### Strategy / Signals

S1-S4 remain deterministic baseline strategy code, not proven profitable strategies. Strategy code must not mutate balances or execute orders directly.

No active automatic Strategy -> Risk integration exists yet.

### Risk — Phase 4

`backend/app/risk/` plus `backend/app/models/risk.py` is the active independent authorization domain.

`RiskProfile` persists versioned limits. The initial `risk-v1` profile defines:

- max order notional: 250 USDT;
- max order/equity: 25%;
- max total exposure/equity: 60%;
- max symbol exposure/equity: 35%;
- max open positions: 4;
- max realized loss/funded capital: 10%;
- max drawdown: 15%;
- max quote age: 30 s.

`RiskDecision` persists ALLOW/REJECT plus account/agent, profile version, real-market provenance, requested notional, equity/exposure state and reason code.

Risk fails closed on paused/inactive profile, inactive agent, non-real/stale/future data, currency mismatch, Accounting mismatch or unresolved Paper recovery. BUY additionally requires complete real marks for open positions.

BUY orders are constrained by notional/equity/exposure/concentration/open-position/loss/drawdown/cash-reserve limits. A valid SELL reducing an existing long may bypass those size/loss caps but still requires integrity, data and recovery gates and cannot oversell.

Every normal `PaperExecutionService.execute_market_order()` call requires a persisted current-profile ALLOW decision. Paper verifies that the decision exists in SQLite, is unconsumed, matches the payload and provider observation, and remains valid under an active/unpaused profile at consumption time.

### Paper Execution — Phase 3 + Phase 4 gate

`backend/app/paper_execution/` supports operator-originated MARKET BUY/SELL only.

`paper-v1`:

- real current Quote;
- full fill or rejection;
- 10 bps adverse slippage;
- 10 bps fee;
- persistent `PaperExecution` provenance;
- persistent `PaperRequest` idempotency;
- conservative restart/recovery;
- no exchange credentials or Live adapter.

The active path is Risk-gated:

```text
request_id
   -> Real Market Data
   -> RiskService.evaluate()
   -> RiskDecision
        REJECT -> no Paper Order/Fill
        ALLOW  -> PaperExecutionService
                     -> AccountingService
```

There is no normal Paper execution bypass without Risk. Recovery routines reconcile already-persisted Paper state but do not submit new orders.

### Portfolio & Accounting — Phase 2

`backend/app/accounting/` plus `backend/app/models/accounting.py` owns Account, Order, Fill, Position and LedgerEntry.

Accounting invariants include:

`equity = cash + market_value(open_positions)`

and

`equity = funded_capital + realized_pnl + unrealized_pnl`

Funding never counts as PnL. Buy fees enter acquisition basis; sell fees reduce realized proceeds. Shorts, leverage and margin remain undefined/rejected.

`AccountingIntegrityService` provides valuation-free structural checks needed by risk-reducing SELL when unrelated market marks are unavailable. BUY continues to require full `AccountingService.reconcile()` with real marks.

### Agent Lifecycle

Owns identity, strategy assignment, status and future lineage/replication. Replication remains blocked until Phase 6 defines evidence-aware fitness and non-duplicating capital allocation.

### Metrics & Evidence

Consumes persisted Accounting/Paper/Risk records. Legacy `Trade` rows remain `legacy_unclassified`; they are not promoted into Paper evidence.

## Active API/UI boundary

Trading-core surfaces:

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

Settings reports Market Data, Accounting, Risk, Paper, automation and Live state. Ops Monitor displays Paper execution provenance instead of legacy Trade data.

## Current runtime

`backend/app/main.py` reports:

- `runtime_mode=transition`;
- `market_data=real_contract_available`;
- `accounting=authoritative_phase_2`;
- `risk=authoritative_phase_4`;
- `paper_trading=operator_only_phase_4`;
- `automated_trading=blocked_until_strategy_integration`;
- `live_execution=disabled`.

Normal startup initializes the DB, bootstraps Accounting and `risk-v1`, then reconciles Paper execution/request recovery before accepting normal work.

## Target automated data flow

```text
Provider -> Market Data -> Strategy Intent -> Risk -> Paper Execution
                                                |          |
                                                v          v
                                           Decision    Accounting
                                                |          |
                                                +----> Evidence
```

The Strategy Intent -> Risk integration is not active yet. Phase 4 deliberately establishes the safety gate without silently enabling autonomous agents.

## Synthetic and Live isolation

Synthetic code may be used only by explicit tests/harnesses. It must never provide fallback data, mutate authoritative Accounting or appear as Paper evidence.

Future Live trading must use a separate execution adapter behind `docs/LIVE_TRADING_GATE.md`, explicit credentials/safety controls and explicit authorization.

## Verification

**Phase 4 static architecture audit:** complete for the current Phase 4 source gate.

Static source review establishes contract coherence but cannot certify runtime correctness. Exact-HEAD execution certification still requires fresh backend tests, frontend tests/build and the relevant real-provider virtual-capital smoke run.