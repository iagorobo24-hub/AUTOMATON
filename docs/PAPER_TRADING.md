# Paper Trading

## Definition

Paper Trading means **real market data + virtual capital + simulated execution**. It is forward validation, not a visual simulation.

## Current Phase 3 boundary

Phase 3 implements an operator-only Paper execution boundary under `backend/app/paper_execution/` and `/api/paper`.

It is deliberately narrower than autonomous trading:

- Market Data is real-only through `MarketDataService`.
- Capital is virtual and mutated only through Phase 2 `AccountingService`.
- Only MARKET BUY/SELL orders are supported.
- Phase 3 accepts explicit operator-originated orders only.
- Strategy/agent automation remains blocked until Phase 4 Risk can approve or reject every proposed order.
- No exchange credentials or Live execution adapter are present.

An automated strategy order may be created only after the future Risk gate approves it. This does not prevent the current explicit operator Paper path from being used to validate execution/accounting semantics.

## `paper-v1` fill policy

The first execution model is deliberately simple, conservative and deterministic. It does not claim exchange-grade fill realism.

`paper-v1` currently defines:

- order type: MARKET only;
- fill policy: full fill or rejection; no partial Paper fill simulation;
- quote source: current real `Quote` from the Phase 1 provider-neutral market-data boundary;
- maximum quote age: 30 seconds;
- maximum future clock skew: 5 seconds;
- BUY slippage: market price plus 10 bps;
- SELL slippage: market price minus 10 bps;
- fee: 10 bps of simulated fill notional;
- account scope: long-only accounting;
- account currency must match the market quote currency;
- the account's agent must be active.

The policy version, provider, provider symbol, market quote, fill price, fee, timestamps and evidence mode are persisted with each Paper execution.

## Persistence and provenance

`PaperExecution` records the execution fact and provenance separately from the historical `Trade` table. It links to the authoritative Phase 2 `Order` and `Fill` records.

Persisted Paper fields include:

- account and agent;
- order/fill identity;
- symbol and side;
- requested quantity;
- operator origin;
- `paper-v1` policy version;
- provider and provider symbol;
- quote observed/received timestamps;
- real market price;
- simulated fill price;
- slippage and fee assumptions;
- execution status and rejection/cancellation reason;
- `evidence_mode=paper`.

Legacy `Trade` rows remain historical non-evidence records and are not mixed into the Paper execution feed.

## Idempotency

Every mutating Paper API request requires a non-blank `request_id`.

`PaperRequest` persists the request identity and a fingerprint of account/symbol/side/quantity.

Rules:

- replaying the same `request_id` with the same completed payload returns the same execution and cannot create a second fill;
- reusing a `request_id` with a different payload fails with conflict;
- financial rejections are also idempotent and stay linked to their rejected execution;
- provider/quality failures before any financial order is created are `RETRYABLE`;
- requests interrupted by restart are recovered before new work is accepted;
- an interrupted `PROCESSING` request with no execution linkage is **not** automatically retryable, because the crash may have happened after an `Order` was persisted. It becomes `RECOVERY_REQUIRED` and fails closed.

## State and recovery

Paper execution is persistent and restart-aware.

On startup:

1. Phase 2 accounting baseline is reconciled/bootstrapped.
2. Pending Paper executions are recovered.
3. Pending idempotency requests are recovered.

Recovery never blindly re-submits an uncertain order.

- If accounting already contains the full fill, the pending `PaperExecution` is linked to it and marked `FILLED`.
- If no fill exists for a linked pending execution, the pending order/execution is conservatively cancelled.
- Ambiguous partial execution state becomes `RECOVERY_REQUIRED` and that account is blocked from new Paper execution until resolved.
- A `PROCESSING` request with no execution linkage becomes `RECOVERY_REQUIRED` rather than `RETRYABLE`; automatic retry is blocked because persistent order creation may already have occurred.
- A request whose linked execution record is missing also becomes `RECOVERY_REQUIRED`.

## Failure semantics

Paper fails closed:

- unavailable real-market provider -> HTTP 503, no financial order/fill; request may be retried with the same id because failure happened before financial state;
- invalid/stale market data -> HTTP 502/409 as appropriate, no synthetic replacement;
- insufficient cash, oversell, inactive agent, currency mismatch or unresolved recovery -> rejection/conflict;
- ambiguous crash/idempotency state -> conflict/manual recovery, never automatic re-execution;
- no random opening/closing behavior is reachable from the active Paper path.

## API and UI

Active API:

- `GET /api/paper/status`
- `POST /api/paper/orders/market`
- `GET /api/paper/executions`

The Ops Monitor uses `paper_executions` as its active execution feed and labels records as Paper/real-market evidence, including provider, quote price, simulated fill price, fee and status.

There is no `/api/paper/live` or automatic-trading start endpoint.

## Isolation from Live

A Paper command is structurally incapable of placing a real exchange order. The active Market Data provider is public/read-only, and the Paper service has no account/exchange execution methods or trading credentials.

Future Live execution must be a separate adapter behind `docs/LIVE_TRADING_GATE.md` and explicit authorization.

## Completion status

**Phase 3 source/contract gate:** implemented and statically reviewed, including fail-closed execution/request recovery and persistent idempotency.

**Execution certification:** pending until the exact Phase 3 HEAD successfully runs:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

A real provider end-to-end smoke run is also still required before claiming operational Paper validation.

Phase 3 does **not** make agents autonomous. Phase 4 Risk is the next prerequisite before strategy/agent-generated orders can reach Paper Execution.
