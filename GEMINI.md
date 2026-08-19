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
- `app.main` does **not** start a trading engine.
- The old `AgentEngine` remains versioned only as explicit Synthetic/Test utility code.
- `/health` reports transition mode, synthetic disabled, real Market Data available, Phase 2 accounting authoritative and Paper not implemented.
- Pre-provenance `Trade` rows are `legacy_unclassified` and excluded from verified financial metrics.
- Active HTTP client: `frontend/src/lib/api.js`.

## Architecture boundaries

New trading work follows:

`Market Data -> Strategy -> Risk -> Execution -> Portfolio/Accounting -> Metrics/Evidence`.

Agent lifecycle consumes these contracts; UI observes them. Strategy code must not directly mutate balances or place real orders. Risk must be able to reject execution. Paper must be structurally isolated from any future Live adapter.

## Market Data constraint

Do not reuse legacy `BinanceService` as the real-data provider without redesign: it silently returns mock/generated data on failures. Paper-capable Market Data must fail closed.

## Phase 2 accounting constraint

`backend/app/accounting/` and `backend/app/models/accounting.py` are authoritative for new financial state.

- Do not mutate `Agent.presupuesto_actual` as trading PnL.
- `Agent.presupuesto_*` are compatibility mirrors only.
- Deposits are ledger funding events, never profit.
- Fills must flow through `AccountingService`.
- Phase 2 is long-only; do not invent short/margin semantics.
- Do not expose order/fill execution mutations before Paper Execution.
- Do not erase account balances when an agent is killed/retired.
- Replication is blocked until Phase 6 defines a capital-transfer policy; never duplicate parent capital into a child.
- Existing agents are bootstrapped from initial/funded capital only; do not promote legacy current balance because it may contain synthetic PnL.

## Legacy

Mongo `DatabaseService`, old Trading/Paper engines, registry, auth/payments/chat/notifications and unmounted pages are legacy. Do not reactivate them wholesale. Audit useful concepts and migrate only what fits the new contracts. `docs/LEGACY_AUDIT.md` remains transitional until pruning.

## Strategy/evidence rules

- S1-S4 are baseline implementations, not proven profitable strategies.
- Historical Alpha/Beta/Gamma ideas are research hypotheses only.
- No `optimized`, `validated`, `profitable` or `safe` claim without reproducible evidence.
- Unknown strategy IDs must fail explicitly.
- Financial telemetry must carry mode/provenance; missing data stays missing.

## Validation

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report green status without fresh output for the exact HEAD.

## Change discipline

Follow the roadmap dependency order. Do not implement Live early, weaken accounting/risk for a test, fabricate UI activity or introduce a second active persistence/API stack.
