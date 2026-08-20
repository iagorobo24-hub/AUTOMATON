# Legacy audit and Phase 9 pruning record

Audit origin: 2026-08-18  
Phase 9 reconciliation: 2026-08-20

## Purpose

Record what historical architecture was removed, what transition data remains intentionally quarantined, and which active contracts must not be confused with the deleted implementation.

## Current runtime boundary

`backend/app/main.py` now exposes the Phase 1–8 SQLModel architecture plus `legacy_pruning=pruned_phase_9`.

Active runtime surfaces are:

- agents / quarantined legacy trade inspection / CoinGecko UI market browser;
- real fail-closed Market Data;
- authoritative Accounting;
- mandatory Risk;
- deterministic Paper Execution;
- reproducible Backtesting;
- Agent Evolution;
- persistent autonomous Paper Runtime;
- Strategy Research.

Live execution remains disabled.

## Physically removed in Phase 9

The repository no longer contains the historical Mongo/mock/trading implementation:

- Mongo `DatabaseService`, Mongo injection/API aggregation and Mongo seed/config;
- auth/chat/payments/notifications/dashboard/system/signals/strategy-CRUD Mongo routers;
- simulation, old Paper, old trading and old risk routers;
- `AgentEngine`, `MockEngine`, `PaperTradingEngine`, `TradingEngine`, registry, old replication, old risk manager and portfolio snapshot services;
- credentialed/mock-fallback `BinanceService`;
- executable Alpha/Beta/Gamma/regime/indicator legacy strategy stack;
- Mongo/auth/trading Pydantic models that were not part of the active SQLModel model registry;
- packages used only by those implementations: Mongo drivers, JWT/passlib, multipart auth support, python-binance, slowapi and pydantic-settings;
- Docker Compose MongoDB/mongo-express services and Mongo environment wiring;
- obsolete tests that exercised deleted endpoints/modules or external preview deployments;
- unreachable legacy frontend pages, mock data, simulation-mode hooks, neural-fiber UI and their exclusive components.

No compatibility wrapper was retained merely to preserve imports.

## Intentionally retained transition surface

### `Agent` and `Trade`

`models/sql_models.py` remains active because `Agent` is still the identity/lifecycle anchor used by Accounting, Evolution, Runtime and Research.

The old `Trade` table is retained only for historical inspection. `routers/trades.py` exposes it as:

- `evidence_mode=legacy_unclassified`;
- `evidence_valid=false`;
- no verified PnL/win-rate derivation.

It is not a Paper, Backtest, Runtime or Research evidence source.

### `models/enums.py`

This module is retained because active SQLModel models import `AgentStatus`, `StrategyEnum` and `TradeType`. Its existence is not evidence that the removed Mongo model stack remains active.

### `routers/crypto.py`

This CoinGecko-backed route is retained as a UI market browser. Financial execution/evidence uses the provider-neutral `market_data/` contract instead.

### Historical strategy documents

Old Alpha/Beta/Gamma documents remain research references only. Their executable implementations were removed. Historical percentages are not evidence and may only become candidates again through the current Backtest/Research pipeline.

## Active strategy implementation

`backend/app/services/` now contains only:

- `__init__.py`;
- `strategies.py`.

S1–S4 remain unchanged by Phase 9. Unknown strategy IDs still fail explicitly; no legacy Alpha/Beta/Gamma or regime-switcher implementation is active.

## Architecture guards

`backend/tests/test_legacy_pruning_architecture.py` guards, in source, that:

- deleted backend/frontend paths do not return;
- active financial/evidence domains do not import legacy engines or Mongo;
- only the active strategy service remains under `app/services/`;
- removed backend dependencies stay absent;
- dev Docker Compose does not reintroduce Mongo;
- Live remains disabled.

Executable certification is separate from this static guard.

## Current limitation

Phase 9 source/static pruning does not prove the complete application test suite or frontend build passes. The exact final HEAD still requires:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Do not report those gates as green without observed execution.

## Stop conditions

- do not recreate Mongo or a second financial source of truth;
- do not restore generated/mock market data to Paper/evidence paths;
- do not restore deleted trading engines as shortcuts around Accounting/Risk/Paper Runtime;
- do not treat quarantined `Trade` rows or historical strategy claims as evidence;
- do not reintroduce Live capability during cleanup or documentation work.
