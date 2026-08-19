# Portfolio and Accounting

## Goal

Maintain one reconciled financial source of truth for Backtest and Paper.

## Implemented Phase 2 authority

New financial work uses the SQLModel records in `backend/app/models/accounting.py`:

- `Account` — funded capital, cash, reserve, realized PnL and fees;
- `Order` — requested BUY/SELL quantity and fill lifecycle;
- `Fill` — execution fact supplied by a future Paper/Backtest engine;
- `Position` — long quantity, fee-inclusive average cost and realized PnL;
- `LedgerEntry` — explicit funding events.

`Agent.presupuesto_inicial` / `Agent.presupuesto_actual` remain compatibility fields during migration. They are not the authoritative calculation path for new trading work.

The active runtime reports `accounting=authoritative_phase_2` and exposes a read-only inspection endpoint:

`GET /api/accounting/agents/{agent_id}`

Phase 2 does not expose order/fill mutation over HTTP. Future Paper Execution owns those mutations and must feed accepted fills through `AccountingService`.

## Supported financial model

Phase 2 is deliberately **long-only**. Margin, leverage and short positions are not defined yet and must not be inferred from SELL orders.

Core identity:

`equity = cash + market_value(open_positions)`

Reconciliation also checks:

`equity = funded_capital + realized_pnl + unrealized_pnl`

with buy fees included in acquisition cost and sell fees deducted from realized proceeds.

Tracked concepts:

- initial capital;
- total funded capital;
- available cash;
- reserved cash field for future execution semantics;
- open quantity;
- average cost;
- realized PnL;
- unrealized PnL;
- fees paid;
- equity;
- exposure.

## Fill semantics

### BUY

For quantity `q`, execution price `p` and fee `f`:

`cash_change = -(q * p + f)`

The position book basis includes the acquisition fee:

`new_average_cost = (old_basis + q * p + f) / new_quantity`

A BUY is rejected before mutation if cash is insufficient.

### SELL

A SELL is allowed only against an existing long position and cannot exceed its quantity.

`net_proceeds = q * p - f`

`realized_pnl = net_proceeds - q * average_cost`

Closing a position returns proceeds to cash exactly once. A full close leaves quantity and average cost at zero. Partial closes preserve the remaining average cost.

## Deposits

Virtual funding is an explicit ledger event. A deposit increases funded capital and cash, never realized PnL.

New agents receive an `INITIAL_FUNDING` ledger entry. Operator deposits create `DEPOSIT` entries.

## Existing-agent bootstrap

Agents created before Phase 2 are migrated conservatively on startup.

The bootstrap uses only legacy `presupuesto_inicial` as funded capital. It **does not** copy `presupuesto_actual`, because that value may include historical synthetic/unverified PnL.

The baseline ledger entry is:

- type: `BASELINE_FUNDING`;
- reason: `phase_2_legacy_reset_excludes_unverified_pnl`.

The migration is idempotent: an agent that already has an accounting account is not recreated.

## Agent lifecycle boundary

Killing/retiring an agent changes lifecycle state but does not erase its accounting cash or ledger.

Manual replication is currently blocked. The former implementation created a child with copied parent capital without debiting the parent, which violated conservation of capital. Replication may return only after Phase 6 defines and tests an explicit capital-transfer/allocation policy.

## Reconciliation

`AccountingService.reconcile()` checks at least:

- equity identity mismatch;
- negative cash/reserved cash;
- negative position quantity;
- order filled quantity versus persisted fills;
- overfilled orders;
- orphan fills.

A restart can rebuild snapshots directly from persisted Account/Position/Order/Fill records; financial truth does not depend on in-memory engine state.

## Tests authored

Phase 2 regression tests cover:

1. initial funding and deposits;
2. BUY accounting and fee-inclusive average cost;
3. partial SELL and realized PnL;
4. full close;
5. unrealized PnL/equity/exposure;
6. insufficient cash and oversell fail-closed behavior;
7. reload/restart reconstruction;
8. explicit reconciliation failure detection;
9. legacy-agent safe bootstrap;
10. agent creation/deposit integration;
11. replication blocked until capital allocation exists;
12. read-only accounting API boundaries.

## Completion status

**Source/contract gate:** implemented and statically reviewed.

**Execution certification:** pending until the exact resulting HEAD passes:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

No Phase 2 document should claim execution-green status without fresh output from those commands.
