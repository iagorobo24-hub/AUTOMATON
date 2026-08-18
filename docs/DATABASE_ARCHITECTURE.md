# Database Architecture

## Active baseline

The current runtime uses SQLModel + SQLite through `backend/app/database.py`. MongoDB is legacy and is not a source of truth for new product work.

## Design goal

Persistence must support trustworthy Paper/Backtest accounting and evidence. The database should model financial facts explicitly instead of recreating the historical Mongo schema.

## Current active records

- `Agent`: identity, strategy, state, initial/current budget, parent and replication threshold.
- `Trade`: current transition record used by active agents/trades APIs.

These tables are a baseline, not the final financial model.

## Target records

Implementation phases should introduce only the entities required by their contracts, expected to include:

- **Order**: requested action and lifecycle state.
- **Fill**: simulated/exchange execution fact with price, quantity, fee and timestamp.
- **Position**: open quantity/cost basis and lifecycle.
- **Account/Ledger event**: capital movements and adjustments where needed for reconciliation.
- **Equity snapshot**: derived historical observation for analysis, linked to mode/session.
- **Strategy configuration/version**: exact configuration associated with decisions.
- **Risk event/decision**: approvals, rejections and circuit-breaker events.
- **Run/Session**: mode, provider, timestamps and evidence provenance.
- **Agent lineage**: parent/generation/config inheritance as the lifecycle evolves.

Exact table names/schema are decided in implementation plans; accounting invariants in `PORTFOLIO_ACCOUNTING.md` are mandatory.

## Rules

- One authoritative financial calculation path.
- Virtual deposits/adjustments are explicit and never counted as PnL.
- Mode/session provenance is preserved.
- Open financial state survives restart.
- Schema migrations preserve or explicitly migrate existing active data.
- No new Mongo collection is introduced for active functionality.

## Legacy

Historical Mongo models may contain ideas worth migrating, but no field/collection is retained merely because it existed before. Migration is driven by the new domain contracts.
