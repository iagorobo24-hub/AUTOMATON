# GEMINI.md — Current Project Context

## Runtime source of truth

Before changing AUTOMATON, inspect `backend/app/main.py` and `frontend/src/App.jsx`. Do not infer active functionality from historical routers, old pages or planning documents.

Current runtime:

- Backend: FastAPI + SQLModel + SQLite.
- Engine: `backend/app/services/agent_engine.py`.
- Active routers mounted by `app.main`: `agents`, `trades`, `crypto`.
- Active extra endpoints: `/api/estado`, `/health`, `/`.
- Frontend: React 19 + Vite.
- Active HTTP client: `frontend/src/lib/api.js`.
- Active pages: `DashboardPro`, `CryptoPro`, `OpsMonitorPro`, `AgentsPage`, `SettingsPage`.

## Important architectural boundary

The repository still contains a legacy MongoDB architecture (`DatabaseService`, rich Pydantic agent models, TradingEngine, PaperTradingEngine, MockEngine, registry, auth/payments/notifications/system/trading routers). It is preserved but **not mounted by `app.main`**.

Do not mount legacy routers merely to satisfy a missing frontend endpoint. First determine whether the required behavior belongs to the SQLModel runtime or requires an explicit migration/reactivation decision.

## Agent contract

The active SQLModel agent uses:

- `nombre`
- `estrategia`: S1/S2/S3/S4
- `presupuesto_inicial`
- `presupuesto_actual`
- `estado`: ACTIVO/MUERTO/REPLICADO
- `padre_id`
- `umbral_replica`

Manual and automatic replication share `app/services/agent_replication.py`.

## Frontend data rules

- All active API calls go through `frontend/src/lib/api.js`.
- Dashboard metrics must come from active agents/trades/health endpoints; do not hard-code demo KPIs as live data.
- Ops Monitor uses REST polling on `/api/trades/`; there is no active `/ws/trading` WebSocket.
- Settings is informational until the SQLModel runtime exposes persisted global settings.
- Do not reintroduce `frontend/src/services/api.js` or a second API client.

## Running

```bash
npm run setup
npm run dev
```

Ports:

- Backend: `127.0.0.1:8000`
- Frontend: `localhost:5173`

Docker/MongoDB is not required by the active SQLModel runtime.

## Testing

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Never report these as passing without a fresh execution on the current HEAD.

## Change discipline

- Prefer minimal changes in the responsible layer.
- Preserve legacy code unless deletion is proven safe and in scope.
- Do not add new Paper/Live trading behavior during stabilization.
- Review the real diff and current branch before publishing.
- Treat `ARCHITECTURE.md` as the canonical architecture summary.
