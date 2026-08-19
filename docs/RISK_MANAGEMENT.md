# Risk Management

## Current Phase 4 role

Risk is an independent persistent approval layer between order intent and Paper Execution. It never mutates cash/positions and never places orders. Every normal `PaperExecutionService.execute_market_order()` call requires a **persisted current-profile `ALLOW` RiskDecision**, and every active `POST /api/paper/orders/market` command is evaluated before Paper creates Order/Fill state.

```text
Operator intent -> real Market Data -> RiskService -> ALLOW/REJECT
                                            |
                                            +-> persisted RiskDecision

ALLOW -> PaperExecutionService -> AccountingService
REJECT -> no Paper Order/Fill
```

Automated strategy/agent submission is still disabled. Phase 4 establishes the gate; later integration must use it rather than bypass it.

## `risk-v1`

The initial profile is bootstrapped idempotently and persisted.

| Limit | `risk-v1` |
|---|---:|
| Maximum order notional | 250 USDT |
| Maximum order / equity | 25% |
| Maximum total exposure / equity | 60% |
| Maximum symbol exposure / equity | 35% |
| Maximum open positions | 4 |
| Maximum realized loss / funded capital | 10% |
| Maximum drawdown | 15% |
| Maximum quote age | 30 s |

These are conservative operational defaults, **not profitability or optimality claims**. A materially different policy used for evidence must receive a different version.

## Persisted RiskDecision

Each evaluation records:

- account/agent and profile/version;
- symbol, side, quantity;
- real provider, quote time and market price;
- requested notional;
- funded capital/equity context;
- total/symbol exposure before and projected;
- open-position count before/projected;
- realized PnL and drawdown context;
- `ALLOW` or `REJECT`;
- machine-readable reason code and readable reason;
- one-time consumption time and linked Paper execution when consumed.

At Paper consumption time the decision must:

- exist in authoritative SQLite persistence;
- still be `ALLOW` and unconsumed;
- belong to an active, unpaused matching profile/version;
- match account, symbol, side, quantity, provider, quote timestamp and market price.

This prevents in-memory fabricated approvals, payload reuse and approvals surviving a circuit-breaker pause.

## Common fail-closed gates

Risk rejects when it cannot establish safe state, including:

- inactive/paused profile;
- inactive agent;
- invalid side/quantity/price;
- non-real/provider-less quote;
- stale/future quote;
- symbol/currency mismatch;
- unresolved Paper recovery;
- Accounting integrity failure.

## BUY

BUY additionally requires **real marks for every open position** and full `AccountingService.reconcile()` before risk limits are calculated.

It then checks:

- absolute order notional;
- order/equity percentage;
- projected total exposure;
- projected symbol concentration;
- projected open-position count;
- realized-loss limit;
- drawdown limit;
- cash for notional plus the exact current `paper-v1` execution-cost reserve.

Current `paper-v1` compounds 10 bps adverse slippage and a 10 bps fee on the slipped fill: `1.001 × 1.001 = 1.002001`. Risk therefore reserves **20.01 bps**, not 20 bps. Accounting remains the final financial authority and can still reject if state changes after Risk approval.

## Risk-reducing SELL

A SELL reducing an existing long is intentionally not blocked by order-size, exposure, concentration, realized-loss or drawdown caps. Risk must not trap an already risky position.

SELL still requires:

- real/fresh quote for the symbol being sold;
- active account/agent;
- currency consistency;
- no unresolved Paper recovery;
- **valuation-free structural Accounting integrity** (`AccountingIntegrityService`);
- sufficient existing long quantity.

It does **not** require a real mark for unrelated open positions. This means equity/total-exposure fields persisted on a SELL decision may be partial when unrelated marks are unavailable. Those fields are authorization context, not a portfolio-performance snapshot. BUY decisions continue to require complete marks and fully reconciled valuation.

Oversells remain rejected.

## Drawdown in `risk-v1`

Phase 4 does not yet persist a historical equity high-water series.

For BUY:

- high-water baseline = `max(funded_capital, funded_capital + realized_pnl)`;
- current equity = fully marked authoritative Accounting snapshot;
- drawdown = `(high_water - current_equity) / high_water` when below high water.

Missing marks fail closed rather than fabricating equity. A future persisted equity-high-water model must use a new Risk profile version.

## Circuit breaker

The active RiskProfile has persistent `paused` state.

- `POST /api/risk/pause`
- `POST /api/risk/resume`

A pause rejects new Risk evaluation and also invalidates a previously produced but not-yet-consumed authorization at Paper consumption time. Pause/resume does not enable or disable autonomous trading because autonomous trading is not active.

## API

- `GET /api/risk/status`
- `GET /api/risk/profiles/active`
- `GET /api/risk/decisions`
- `POST /api/risk/pause`
- `POST /api/risk/resume`

There is deliberately **no public approve endpoint**. Approval comes only from `RiskService.evaluate()` using authoritative state.

## Paper integration and idempotency

Active API flow:

1. reserve `request_id`;
2. obtain real requested-symbol quote;
3. for BUY, obtain real marks for all open positions;
4. evaluate and persist Risk;
5. REJECT -> complete request with 409, no Paper Order/Fill;
6. ALLOW -> Paper independently validates/consumes that persisted decision;
7. Paper creates execution provenance and delegates fill mutation to Accounting.

For SELL, unrelated position marks are not fetched because safe position reduction must not depend on an unrelated provider observation.

A completed idempotent replay resolves before Market Data/Risk and cannot create another RiskDecision or Fill. Provider failure before Risk creates no decision and remains retryable. Missing account/agent lookup is completed idempotently with a fail-closed error instead of leaving `PROCESSING` state.

## Current boundaries

Not implemented in Phase 4:

- strategy/agent automatic submission;
- ATR/volatility sizing;
- stop-loss/take-profit orchestration;
- shorts/leverage/margin;
- Live execution;
- exchange trading credentials.

The legacy RiskManager remains non-authoritative.

## Completion status

**Phase 4 source/contract implementation:** complete.

**Phase 4 exact-HEAD static audit:** complete after reconciling service-level Risk enforcement, SELL valuation semantics, circuit-breaker consumption, idempotency/error handling and documentation.

**Execution certification:** still requires fresh output on the exact final HEAD:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

A real-provider virtual-capital smoke must also confirm `RiskDecision -> PaperExecution -> Accounting` reconciliation before operational validation is claimed.