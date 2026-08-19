# GEMINI.md — AUTOMATON Project Contract

## Read first

Canonical product direction is defined by `docs/PRODUCT_CONTRACT.md`, `ARCHITECTURE.md` and `docs/ROADMAP.md`. Inspect `backend/app/main.py` and `frontend/src/App.jsx` before claiming current implementation status.

## Product objective

Build a trustworthy autonomous-agent trading platform whose immediate target is **Paper Trading on real market data with virtual capital**.

Modes are distinct:

- Synthetic/Test: synthetic + virtual; technical tests only.
- Backtest: historical real data + virtual execution.
- Paper: current real data + virtual capital.
- Live: real data + real capital; future and gated.

Never present synthetic/random/mock results as Paper, Backtest or Live evidence.

## Current transition runtime

- FastAPI + SQLModel + SQLite.
- React 19 + Vite; Electron optional.
- `app.main` mounts agents/trades/crypto and **does not start a trading engine**.
- The old `AgentEngine` remains versioned only as explicit Synthetic/Test utility code.
- `/health` reports `runtime_mode=transition`, `synthetic_engine=disabled`, `paper_trading=not_implemented`.
- Pre-provenance `Trade` rows are `legacy_unclassified` and excluded from verified financial metrics.
- Active HTTP client: `frontend/src/lib/api.js`.

## Architecture boundaries

New trading work follows:

`Market Data -> Strategy -> Risk -> Execution -> Portfolio/Accounting -> Metrics/Evidence`.

Agent lifecycle consumes these contracts; UI observes them. Strategy code must not directly mutate balances or place real orders. Risk must be able to reject execution. Paper must be structurally isolated from any future Live adapter.

## Phase 1 constraint

Do not reuse legacy `BinanceService` as the real-data provider without redesign: it silently returns mock/generated prices, candles and orderbook data on missing credentials/provider errors. A Paper-capable Market Data adapter must fail closed instead.

## Legacy

Mongo `DatabaseService`, old Trading/Paper engines, registry, auth/payments/chat/notifications and unmounted pages are legacy. Do not reactivate them wholesale. Audit useful concepts and migrate only what fits the new contracts. `docs/LEGACY_AUDIT.md` remains transitional until pruning.

## Strategy/evidence rules

- S1-S4 are baseline implementations, not proven profitable strategies.
- Historical Alpha/Beta/Gamma ideas are research hypotheses only.
- No `optimized`, `validated`, `profitable` or `safe` claim without reproducible evidence.
- Unknown strategy IDs must fail explicitly.
- Financial telemetry must carry mode/provenance; missing data stays missing.
- Deposits/funding are capital flows, not trading profit.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report green status without fresh output for the exact HEAD.

## Change discipline

Follow the roadmap dependency order. Do not implement Live early, weaken accounting/risk for a test, fabricate UI activity or introduce a second active persistence/API stack.
