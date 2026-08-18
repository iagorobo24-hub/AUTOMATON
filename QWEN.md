# QWEN.md — Current AUTOMATON Context

This file reflects the current repository state. Historical Mongo/CRACO/port-8001 descriptions are obsolete.

## Active architecture

- Desktop shell: Electron (optional).
- Frontend: React 19 + Vite on `localhost:5173`.
- Backend: FastAPI on `127.0.0.1:8000`.
- Persistence: SQLModel + SQLite.
- Runtime engine: `AgentEngine`.
- Mounted backend routers: agents, trades, crypto.
- Active frontend client: `frontend/src/lib/api.js`.

`frontend/src/App.jsx` is the authority for active pages. `backend/app/main.py` is the authority for active backend routes.

## Legacy boundary

MongoDB, `DatabaseService`, TradingEngine, PaperTradingEngine, MockEngine, registry, rich Pydantic models and their associated routers remain in the repository as legacy code. They are not part of the runtime launched by `app.main`.

Do not describe them as stable/current functionality and do not mount them as a shortcut around a missing SQLModel contract.

## Runtime behavior

- Agents use S1-S4 strategies and states ACTIVO/MUERTO/REPLICADO.
- Dashboard derives metrics from `/api/agents/`, `/api/trades/stats` and `/health`.
- Crypto Terminal consumes the active crypto router.
- Ops Monitor polls `/api/trades/`; no active trading WebSocket exists.
- Settings reports runtime health and does not expose fake global or Live/Paper settings.

## Commands

```bash
npm run setup
npm run dev
npm run dev:backend
npm run dev:frontend
npm run dev:electron
```

Tests:

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
cd frontend && npm run build
```

Do not claim verification without fresh command output for the current HEAD.

## Development rules

- Keep SQLModel as the source of truth for active agents/trades.
- Use `frontend/src/lib/api.js` for active HTTP calls.
- Prefer minimal fixes over architecture expansion.
- Preserve legacy modules unless deletion is proven safe.
- Update `ARCHITECTURE.md` and README when the active contract changes.
