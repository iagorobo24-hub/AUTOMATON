# Database Architecture

## Active baseline

The current runtime uses SQLModel + SQLite through `backend/app/database.py`. MongoDB is legacy and is not a source of truth for new product work.

## Active records

### Legacy/transition records

- `Agent`: identity, strategy and lifecycle state. Its budget fields remain compatibility mirrors during migration.
- `Trade`: historical transition record. Pre-provenance rows remain `legacy_unclassified` and are not part of the authoritative accounting chain.

### Phase 2 accounting records

- `portfolio_accounts` (`Account`): one account per agent; initial/funded capital, cash, reserve, realized PnL and fees.
- `portfolio_orders` (`Order`): requested long-only BUY/SELL action and fill state.
- `portfolio_fills` (`Fill`): persisted Paper/Backtest execution fact supplied to accounting.
- `portfolio_positions` (`Position`): one position per account/symbol with quantity and average cost.
- `portfolio_ledger` (`LedgerEntry`): explicit funding movements and migration baseline events.

The Phase 2 models live in `backend/app/models/accounting.py` and are manipulated by `backend/app/accounting/service.py`.

## Source-of-truth rule

For all new financial work, accounting tables are authoritative. `Agent.presupuesto_inicial` and `Agent.presupuesto_actual` must not become a second independent accounting system.

During transition, agent API responses may mirror funded capital/cash from the accounting account for compatibility with the existing frontend.

## Accounting invariants

The system must reconcile:

`equity = cash + market_value(open_positions)`

and:

`equity = funded_capital + realized_pnl + unrealized_pnl`

Funding events never count as PnL. Buy fees enter acquisition basis; sell fees reduce realized proceeds.

## Legacy-agent bootstrap

On normal startup, agents without an accounting account receive an idempotent Phase 2 baseline account.

Only `Agent.presupuesto_inicial` is used as funded capital. Historical `presupuesto_actual` is ignored because it may contain synthetic/unverified PnL.

The migration writes `BASELINE_FUNDING` with reason `phase_2_legacy_reset_excludes_unverified_pnl`.

## Persistence/recovery

Account, orders, fills and positions are persisted so accounting can be reconstructed after restart without relying on in-memory execution state.

`AccountingService.reconcile()` detects equity identity mismatches, negative financial state, order/fill quantity mismatch, overfills and orphan fills.

## Current scope limits

- long-only;
- no leverage/margin;
- no short positions;
- no Paper execution endpoint yet;
- no Live execution;
- no authoritative performance claim until Paper/Backtest produces valid evidence.

## Future records

Later phases may add:

- equity snapshots;
- strategy configuration/version;
- risk decisions/events;
- run/session identity and provenance;
- richer lineage/allocation records.

These should be added only when their owning phase requires them.

## Rules

- One authoritative financial calculation path.
- Virtual deposits/adjustments are explicit and never counted as PnL.
- Mode/session provenance is preserved on execution facts.
- Open financial state survives restart.
- Existing data is explicitly migrated or quarantined; never silently promoted.
- No new Mongo collection is introduced for active functionality.
