# Risk Management

## Current Phase 4 role

Risk is now an independent persistent approval layer between Paper order intent and Paper Execution. It never mutates cash/positions and never places orders. Every active `POST /api/paper/orders/market` command must receive a persisted `ALLOW` decision before Paper creates an Order or Fill.

Current flow:

```text
Operator intent -> real Market Data -> RiskService -> ALLOW/REJECT
                                            |
                                            +-> persisted RiskDecision

ALLOW -> PaperExecutionService -> AccountingService
REJECT -> no Paper Order/Fill
```

Automated strategy/agent execution is still disabled. Phase 4 builds the safety gate first; later work may connect strategy intents to it.

## Persistence

### `RiskProfile`

`risk-v1` is bootstrapped idempotently and is the active initial profile.

Defaults:

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

These are conservative operational defaults, **not claims that these values are profitable or optimal**. Any future change that affects experiment comparability requires a new profile/version.

### `RiskDecision`

Every evaluation persists:

- account and agent;
- profile/version;
- symbol, side and quantity;
- quote provider, timestamp and market price;
- requested notional;
- equity/funded capital;
- exposure before/projected;
- symbol concentration before/projected;
- open-position count before/projected;
- realized PnL and drawdown;
- `ALLOW` or `REJECT`;
- machine-readable reason code and human-readable reason;
- one-time consumption timestamp and linked Paper execution when used.

A decision cannot be reused for another Paper execution or another payload.

## Fail-closed gates

Risk rejects new orders when it cannot establish trustworthy state.

Common gates include:

- inactive/paused profile;
- inactive agent;
- invalid side/quantity/price;
- non-real or provider-less quote;
- stale/future quote;
- symbol/currency mismatch;
- unresolved Paper recovery state;
- missing real marks for open positions;
- Accounting reconciliation failure.

### BUY limits

BUY also checks:

- absolute order notional;
- order/equity ratio;
- projected total exposure;
- projected symbol concentration;
- projected open-position count;
- realized-loss limit;
- drawdown limit;
- cash sufficient for requested notional plus a conservative 20 bps Paper execution cost reserve.

The reserve matches the current `paper-v1` 10 bps adverse slippage + 10 bps fee assumptions. Accounting remains the final financial authority.

### SELL risk reduction

A valid SELL that reduces an existing long position is not blocked by order-size, exposure, concentration, realized-loss or drawdown caps. This prevents Risk from trapping an already risky account.

SELL still requires:

- real/fresh market data;
- active agent/account;
- currency consistency;
- Accounting reconciliation;
- no unresolved recovery;
- sufficient existing long quantity.

Oversells are rejected.

## Drawdown definition in `risk-v1`

Phase 4 does not yet have a persisted equity time series. `risk-v1` therefore uses a documented conservative approximation:

- high-water baseline = `max(funded_capital, funded_capital + realized_pnl)`;
- current equity = authoritative Accounting snapshot marked with current real prices for every open position;
- drawdown = `(high_water - current_equity) / high_water` when current equity is below high water.

If real marks for all open positions are unavailable, Risk rejects instead of fabricating equity. A future persisted equity-high-water model must use a new Risk version.

## Circuit breaker

The active profile has a persistent `paused` flag.

Active controls:

- `POST /api/risk/pause`
- `POST /api/risk/resume`

While paused, new Paper orders receive `RISK_PAUSED`. Pause/resume does not start or stop autonomous trading because autonomous trading is not enabled.

## API

Read/control endpoints:

- `GET /api/risk/status`
- `GET /api/risk/profiles/active`
- `GET /api/risk/decisions`
- `POST /api/risk/pause`
- `POST /api/risk/resume`

There is deliberately no public endpoint that allows a client to manufacture an `ALLOW` decision. Approval is produced internally by `RiskService.evaluate()` from authoritative state.

## Paper integration and idempotency

Paper request flow is:

1. reserve required `request_id`;
2. obtain real quote and real marks for open positions;
3. evaluate/persist Risk;
4. REJECT -> complete request with 409 and create no Paper Order/Fill;
5. ALLOW -> pass one-time `RiskDecision` to Paper Execution;
6. Paper validates account/symbol/side/quantity/quote/provider against the decision;
7. Paper consumes/links the decision when the Paper execution record is created.

A completed idempotent replay is resolved before Market Data/Risk, so it cannot create a second Risk decision or fill.

Provider failures before Risk create no Risk decision and remain retryable because no financial state was created.

## Current boundaries

Not implemented in Phase 4:

- strategy/agent automatic order submission;
- ATR or volatility sizing;
- stop-loss/take-profit orchestration;
- shorts/leverage/margin;
- Live execution;
- exchange trading credentials.

Historical legacy `RiskManager` code is not reactivated as the active contract.

## Completion status

**Phase 4 source/contract gate:** implemented in source and subject to final static audit.

**Execution certification:** requires fresh output on the exact final HEAD:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

A real-provider virtual-capital smoke run must also confirm RiskDecision -> PaperExecution -> Accounting reconciliation before operational validation is claimed.
