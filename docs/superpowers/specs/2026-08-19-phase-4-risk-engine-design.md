# Phase 4 Risk Engine Design

## Objective

Introduce an independent, persistent, fail-closed Risk domain between order intent and Paper Execution. Risk decides whether an order is allowed under an explicit versioned profile; it never mutates financial state and never executes orders.

## Scope

Phase 4 adds:

- versioned risk profiles;
- persisted allow/reject decisions;
- deterministic limits for order size, exposure, concentration, open positions, realized loss and drawdown;
- stale/invalid real-market-data rejection;
- accounting reconciliation and Paper recovery gates;
- global pause/circuit-breaker state;
- mandatory Risk approval for operator Paper orders;
- a reusable service contract for future strategy/agent-originated orders.

Phase 4 does not add:

- automatic strategy execution;
- ATR/volatility sizing;
- leverage, shorts or margin;
- stop-loss/take-profit orchestration;
- Live execution;
- exchange credentials;
- a second accounting source of truth.

## Architecture

```text
Operator / future Strategy Intent
          |
          v
    Real Market Data
          |
          v
       RiskService
      /           \
 REJECT          ALLOW
  |                |
 persisted          v
 decision     PaperExecutionService
                    |
                    v
             AccountingService
```

Risk consumes authoritative state but does not own it:

- Market Data owns Quote freshness/provenance.
- Accounting owns cash, positions, equity and reconciliation.
- Paper Execution owns virtual fills.
- Risk owns policy and authorization decisions.

## Persistence

### RiskProfile

One active profile is used initially. Fields:

- `name`
- `version`
- `active`
- `paused`
- `max_order_notional`
- `max_order_equity_pct`
- `max_total_exposure_pct`
- `max_symbol_exposure_pct`
- `max_open_positions`
- `max_realized_loss_pct`
- `max_drawdown_pct`
- `max_quote_age_seconds`
- timestamps

The initial profile is `risk-v1` and is bootstrapped idempotently.

### RiskDecision

Each evaluation persists:

- account/agent;
- profile/version;
- symbol, side, quantity;
- quote provider and observed timestamp;
- market price;
- requested notional;
- equity and funded capital;
- total exposure before/projected;
- symbol exposure before/projected;
- open-position count before/projected;
- realized PnL;
- current drawdown;
- `ALLOW` or `REJECT`;
- machine-readable reason code;
- human-readable reason;
- timestamp;
- `consumed_at` and optional linked Paper execution.

A decision is immutable as evidence except for one-time consumption metadata.

## Initial `risk-v1` policy

Conservative defaults for virtual capital:

- `max_order_notional = 250 USDT`
- `max_order_equity_pct = 25%`
- `max_total_exposure_pct = 60%`
- `max_symbol_exposure_pct = 35%`
- `max_open_positions = 4`
- `max_realized_loss_pct = 10%` of funded capital
- `max_drawdown_pct = 15%`
- `max_quote_age_seconds = 30`

These are operational defaults, not validated profitability claims. They are persisted/versioned so later experiments can compare profiles correctly.

## Evaluation rules

Risk is fail-closed. Evaluation rejects when any required invariant cannot be established.

### Common gates

Reject when:

- account does not exist;
- agent is not active;
- profile is paused;
- quote is not real/provider-provenanced;
- quote is stale/future-dated;
- account currency differs from market quote currency;
- Accounting reconciliation fails;
- Paper execution/recovery is unresolved;
- realized loss exceeds the configured limit;
- drawdown exceeds the configured limit.

### BUY

BUY evaluates projected notional/exposure:

- order notional <= absolute order cap;
- order notional <= equity percentage cap;
- projected total exposure <= total exposure cap;
- projected symbol exposure <= concentration cap;
- opening a new symbol must not exceed max open positions;
- cash must be sufficient for notional plus a conservative Paper fee/slippage reserve.

### SELL

SELL is risk-reducing and must not be blocked by exposure concentration/order-size caps, but it still requires:

- real fresh data;
- active account/agent;
- reconciled Accounting;
- no global pause/recovery ambiguity;
- sufficient existing long position.

Loss/drawdown limits do not prevent reducing/closing an existing position. This avoids trapping risk when the account is already in distress.

## Drawdown definition

Phase 4 has no historical equity-snapshot series yet. Therefore `risk-v1` uses a conservative persisted-account approximation:

- high-water baseline = `max(funded_capital, funded_capital + realized_pnl)`;
- current equity comes from Accounting snapshot using the current quote for the requested symbol and persisted average cost for other open symbols only when a trustworthy mark is available;
- if complete marks for all open positions are unavailable, Risk rejects BUY with `ACCOUNTING_MARKS_INCOMPLETE` rather than inventing equity.

For SELL of an existing position, a missing unrelated-symbol mark does not prevent risk reduction.

Phase 7/metrics work may replace this with persisted equity snapshots; that will require a new profile version.

## Paper integration

All `POST /api/paper/orders/market` requests must evaluate Risk before creating a Paper order.

- Risk REJECT -> HTTP 409, no Paper Order/Fill.
- Risk ALLOW -> the returned `RiskDecision.id` is passed to Paper Execution.
- Paper Execution verifies the decision matches account/symbol/side/quantity/profile and is unconsumed.
- Successful or financially rejected execution consumes the decision once and links it to the Paper execution.
- A decision cannot authorize another payload or a second execution.

Operator remains the only allowed Paper origin in Phase 4. Strategy/agent automation remains disabled.

## API

Read/control surface:

- `GET /api/risk/status`
- `GET /api/risk/profiles/active`
- `GET /api/risk/decisions`
- `POST /api/risk/pause`
- `POST /api/risk/resume`

There is intentionally no public `approve` endpoint. Approval is produced internally by `RiskService.evaluate()` using authoritative system data.

Pause/resume is an explicit operator circuit-breaker control. It modifies only the active Risk profile's paused state.

## Recovery and idempotency

Paper `request_id` remains the mutation idempotency authority. Risk evaluation occurs after request reservation but before Paper financial mutation.

- replay of a completed Paper request returns the existing execution without creating a new Risk decision;
- provider failures remain retryable because no financial execution state exists;
- Risk rejection completes the request idempotently and persists the rejection decision;
- an ALLOW decision is one-time consumable;
- unresolved Paper recovery blocks new Risk ALLOW decisions.

## UI

Phase 4 requires truthful operational visibility, not a new trading workflow.

Settings/monitor should expose:

- Risk profile/version;
- active/paused state;
- automation still disabled;
- recent allow/reject decisions where useful.

No UI control may imply Live or autonomous agents are enabled.

## Completion gate

Source/contract completion requires tests covering:

- allow inside limits;
- order notional/equity cap;
- total exposure;
- concentration;
- max open positions;
- cash reserve;
- realized loss;
- drawdown;
- stale/non-real quote;
- inactive agent;
- accounting reconciliation failure;
- Paper recovery ambiguity;
- pause/resume;
- SELL risk-reduction exception;
- decision persistence/profile version;
- decision one-time consumption;
- mismatched/reused decision rejection;
- Paper API mandatory Risk integration;
- Risk rejection creates no Paper order/fill;
- idempotent replay creates no extra decision;
- no Live or synthetic bypass.

Execution certification still requires fresh backend tests, frontend tests/build and a real-provider Paper smoke test on the exact HEAD.
