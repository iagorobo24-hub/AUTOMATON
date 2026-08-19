# Database Architecture

## Active baseline

The current runtime uses SQLModel + SQLite through `backend/app/database.py`. MongoDB is legacy and is not a source of truth for new product work.

## Active records

### Legacy/transition records

- `Agent`: identity, strategy and lifecycle state. Its budget fields remain compatibility mirrors during migration.
- `Trade`: historical transition record. Pre-provenance rows remain `legacy_unclassified` and are not part of the authoritative accounting/Paper chain.

### Phase 2 accounting records

- `portfolio_accounts` (`Account`): one account per agent; initial/funded capital, cash, reserve, realized PnL and fees.
- `portfolio_orders` (`Order`): requested long-only BUY/SELL action and fill state.
- `portfolio_fills` (`Fill`): persisted Paper/Backtest execution fact supplied to accounting.
- `portfolio_positions` (`Position`): one position per account/symbol with quantity and average cost.
- `portfolio_ledger` (`LedgerEntry`): explicit funding movements and migration baseline events.

The Phase 2 models live in `backend/app/models/accounting.py` and are manipulated by `backend/app/accounting/service.py`.

### Phase 3 Paper records

- `paper_executions` (`PaperExecution`): provenance record for each operator Paper attempt linked to its account, `Order`, optional `Fill`, real quote metadata, deterministic fill policy, fee/slippage and final status.
- `paper_requests` (`PaperRequest`): persistent idempotency reservation keyed by `request_id`, command fingerprint and optional linked `PaperExecution`.

The Phase 3 models live in `backend/app/models/paper_execution.py`. The Paper domain does not replace accounting: all financial effects still enter through `AccountingService`.

## Source-of-truth rule

For all new financial work, accounting tables are authoritative. `Agent.presupuesto_inicial` and `Agent.presupuesto_actual` must not become a second independent accounting system.

`PaperExecution` is authoritative for Paper execution provenance, not for balances. `PaperRequest` is authoritative for command idempotency/recovery, not for trading PnL.

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

Account, orders, fills, positions, Paper executions and Paper request reservations survive restart.

Startup recovery is conservative:

1. reconcile pending `PaperExecution` records;
2. link an already-persisted full fill where unambiguous;
3. cancel an unfilled pending execution rather than resubmitting it;
4. mark ambiguous execution state `RECOVERY_REQUIRED`;
5. reconcile `PaperRequest` reservations only after execution recovery;
6. a `PROCESSING` request with no execution linkage becomes `RECOVERY_REQUIRED`, never automatically retryable, because a crash may have occurred after an `Order` was persisted;
7. commands in unresolved recovery state fail closed.

`AccountingService.reconcile()` separately detects equity identity mismatches, negative financial state, order/fill quantity mismatch, overfills and orphan fills.

## Current scope limits

- long-only;
- no leverage/margin;
- no short positions;
- operator-only Paper MARKET execution;
- real market quote required;
- deterministic `paper-v1` fee/slippage policy;
- persistent `request_id` idempotency required for Paper mutations;
- no automated strategy execution until Risk exists;
- no Live execution;
- no broad strategy-performance claim until sufficient Paper/Backtest evidence exists.

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
- Idempotency/recovery uncertainty fails closed rather than creating duplicate Paper orders.
- Existing data is explicitly migrated or quarantined; never silently promoted.
- No new Mongo collection is introduced for active functionality.
