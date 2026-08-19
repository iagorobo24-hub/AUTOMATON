# Database Architecture

## Active baseline

The runtime uses SQLModel + SQLite through `backend/app/database.py`. MongoDB remains legacy and is not a source of truth for new product work.

## Active records

### Legacy/transition

- `Agent`: identity, strategy and lifecycle state. Budget fields are compatibility mirrors only.
- `Trade`: historical pre-provenance record. Existing rows remain `legacy_unclassified` and are outside authoritative Paper evidence.

### Phase 2 Accounting

- `portfolio_accounts` (`Account`): funded capital, cash, reserve, realized PnL and fees.
- `portfolio_orders` (`Order`): requested long-only BUY/SELL lifecycle.
- `portfolio_fills` (`Fill`): persisted Paper/Backtest execution fact.
- `portfolio_positions` (`Position`): long quantity, average cost and realized PnL.
- `portfolio_ledger` (`LedgerEntry`): funding and migration baseline events.

Accounting tables are the only financial source of truth.

### Phase 3 Paper

- `paper_executions` (`PaperExecution`): provider/quote/fill-policy provenance linked to Account, Order and optional Fill.
- `paper_requests` (`PaperRequest`): persistent request-id idempotency and restart state.

Paper records describe execution provenance/idempotency; they do not replace Accounting.

### Phase 4 Risk

- `risk_profiles` (`RiskProfile`): versioned persistent risk policy. Initial active profile is `risk-v1`.
- `risk_decisions` (`RiskDecision`): persisted ALLOW/REJECT evidence for each evaluated order intent.

Each RiskDecision records account/agent, profile version, order payload, market provenance, requested notional, equity/exposure state, realized PnL, drawdown, decision/reason and one-time Paper-consumption linkage.

Risk records do not mutate cash or positions. Their role is authorization and evidence.

## Source-of-truth rules

- Accounting owns balances, positions, PnL, fees and equity.
- PaperExecution owns Paper execution provenance.
- PaperRequest owns Paper mutation idempotency/recovery state.
- RiskProfile owns versioned risk limits.
- RiskDecision owns risk authorization evidence.
- `Agent.presupuesto_*` never becomes a competing accounting system.

## Accounting invariants

`equity = cash + market_value(open_positions)`

and

`equity = funded_capital + realized_pnl + unrealized_pnl`

Funding never counts as PnL. Buy fees enter acquisition basis; sell fees reduce realized proceeds.

## Startup and recovery

Normal startup:

1. initializes SQLModel tables;
2. bootstraps missing Phase 2 accounts from initial/funded capital only;
3. bootstraps `risk-v1` idempotently;
4. reconciles pending Paper executions;
5. reconciles Paper request reservations.

A PROCESSING request with no safe execution linkage becomes `RECOVERY_REQUIRED`, never an automatic retry.

Risk also rejects new active Paper orders when Accounting cannot reconcile, required real marks are incomplete, or Paper recovery remains unresolved.

## Current scope limits

- long-only;
- no leverage/margin/shorts;
- operator-only Paper MARKET execution;
- Risk mandatory for the active Paper HTTP mutation path;
- no automatic strategy execution yet;
- no Live execution;
- no broad strategy-performance claims without later evidence phases.

## Future records

Later phases may add persisted equity/high-water snapshots, strategy configuration/version, backtest/run identity, evidence bundles and richer lineage/allocation records.

## Rules

- One authoritative financial calculation path.
- Every active Paper order has real-market provenance.
- Every successful active Paper API order is linked to a one-time Risk ALLOW decision.
- Risk rejection cannot create Paper Order/Fill state.
- Ambiguous recovery fails closed.
- Existing data is migrated or quarantined explicitly; never silently promoted.
- No new active Mongo collection is introduced.
