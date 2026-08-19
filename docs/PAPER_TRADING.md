# Paper Trading

## Definition

Paper Trading means **real market data + virtual capital + simulated execution**. It is forward validation, not a visual simulation.

## Current Phase 4 boundary

The active Paper domain is `backend/app/paper_execution/` under `/api/paper`.

It remains deliberately narrower than autonomous trading:

- Market Data is real-only through `MarketDataService`.
- Capital is virtual and financial mutation goes only through Phase 2 `AccountingService`.
- Only MARKET BUY/SELL is supported.
- Commands are still explicit operator-originated actions.
- **Every active request-backed Paper order requires Phase 4 Risk authorization before an Order/Fill can be created.**
- Strategy/agent automation is not enabled yet.
- No exchange trading credentials or Live execution adapter are present.

Active request flow:

```text
request_id -> real Quote/marks -> RiskDecision -> PaperExecution -> Accounting
```

A Risk REJECT completes the command with no Paper Order/Fill. A Risk ALLOW is payload-bound, one-time consumable and linked to the resulting Paper execution.

## `paper-v1` fill policy

The first execution model is deliberately simple and deterministic; it does not claim exchange-grade realism.

- MARKET only;
- full fill or rejection;
- current real Quote from the Phase 1 market-data boundary;
- maximum quote age: 30 seconds;
- maximum future clock skew: 5 seconds;
- BUY: 10 bps adverse slippage;
- SELL: 10 bps adverse slippage;
- fee: 10 bps of simulated fill notional;
- long-only Accounting;
- account currency must match market quote currency;
- agent must be active.

Policy version, provider, quote timestamps, real market price, simulated fill price, fee and evidence mode are persisted with each execution.

## Risk gate

The active HTTP mutation path cannot bypass Risk.

- A request-backed call without a Risk decision is rejected before Order creation.
- Risk decision must be `ALLOW`, unconsumed and match account/symbol/side/quantity/price/provider/quote timestamp.
- Once a PaperExecution is persisted, the decision is consumed and linked to that execution.
- A consumed or mismatched decision cannot be reused.

Low-level service calls without `PaperRequest` remain only as deterministic unit-test/recovery seams; they are not exposed as active HTTP bypasses.

## Persistence and provenance

`PaperExecution` is execution provenance, not financial authority. It links to the Phase 2 `Order` and optional `Fill`.

`PaperRequest` is the persistent command-idempotency/recovery record.

`RiskDecision` is the Phase 4 authorization evidence.

Legacy `Trade` rows remain historical non-evidence records and are not mixed into the active Paper feed.

## Idempotency

Every mutating Paper API request requires a non-blank `request_id`.

- Same completed `request_id` + same payload returns the existing execution without another market lookup, Risk decision or fill.
- Reusing the ID for another payload is a conflict.
- Risk financial rejection is completed/idempotent.
- Provider/quality failure before Risk/financial state is `RETRYABLE`.
- An interrupted `PROCESSING` request without safe execution linkage becomes `RECOVERY_REQUIRED`, never an automatic retry.

## State and recovery

Startup order:

1. Accounting baseline bootstrap.
2. `risk-v1` profile bootstrap.
3. pending PaperExecution recovery.
4. pending PaperRequest recovery.

Recovery never blindly resubmits an uncertain order.

- persisted full fill -> link and mark `FILLED` when unambiguous;
- linked execution with no fill -> conservatively cancel;
- ambiguous partial state -> `RECOVERY_REQUIRED`;
- interrupted request with no safe execution linkage -> `RECOVERY_REQUIRED`.

Risk also blocks active orders when Paper recovery for the account is unresolved.

## Risk-reducing SELL

A SELL that reduces an existing long is intentionally easier to authorize than a new BUY: Risk must not trap an already risky position because an unrelated symbol temporarily lacks a real mark.

For this path:

- the sold symbol still requires a real fresh quote;
- Accounting structural integrity is mandatory;
- oversell is rejected;
- unrelated-position valuation marks are not mandatory for authorization;
- the decision's equity/exposure context may therefore be partial and is authorization evidence, **not a portfolio-performance snapshot**.

BUY continues to require real marks for all open positions and full Accounting reconciliation before exposure/drawdown limits are evaluated.

## API and UI

Active Paper API:

- `GET /api/paper/status`
- `POST /api/paper/orders/market`
- `GET /api/paper/executions`

Active Risk API is documented in `RISK_MANAGEMENT.md`.

Ops Monitor uses `paper_executions`. Settings/Dashboard report Paper operator-only with Risk active and autonomous trading still disabled.

There is no active Paper Live endpoint or automatic-trading start endpoint.

## Isolation from Live

Paper is structurally incapable of placing a real exchange order. Future Live execution must use a separate adapter behind `docs/LIVE_TRADING_GATE.md` and explicit authorization.

## Completion status

Phase 3 Paper source contract remains implemented. Phase 4 now places mandatory Risk in front of the active request-backed Paper mutation path.

Executable certification still requires fresh exact-HEAD evidence:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

A real-provider virtual-capital smoke must also verify `RiskDecision -> PaperExecution -> Accounting` before operational validation is claimed.
