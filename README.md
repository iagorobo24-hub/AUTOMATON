# AUTOMATON v2

AUTOMATON es una aplicación local de agentes de trading simulados. El runtime efectivo actual utiliza **FastAPI + SQLModel + SQLite** y un `AgentEngine` que ejecuta estrategias simuladas sobre BTC.

## Estado actual

La aplicación activa expone cinco vistas:

- `/` — dashboard con métricas reales de agentes y trades persistidos.
- `/crypto` — datos de mercado crypto y Quick Deploy de agentes S1.
- `/monitor` — historial operativo leído de `/api/trades/` mediante polling REST.
- `/agents` — gestión del ciclo de vida SQLModel.
- `/settings` — estado y límites del runtime realmente montado.

No hay WebSocket `/ws/trading` activo ni cambio Live/Paper en `app.main`. La antigua capa Mongo/`DatabaseService`, `TradingEngine`, `PaperTradingEngine`, pagos, auth y otros routers permanece en el repositorio como **legacy no montado** y no debe tratarse como fuente de verdad del runtime actual.

## Quick start

```bash
npm install
npm run setup
npm run dev
```

`npm run dev` inicia:

- FastAPI: `http://127.0.0.1:8000`
- Vite: `http://localhost:5173`
- Electron después de que backend y frontend respondan

También pueden arrancarse por separado:

```bash
npm run dev:backend
npm run dev:frontend
npm run dev:electron
```

## Arquitectura activa

```text
frontend/src/main.jsx
  -> App.jsx
     -> DashboardPro -> BentoGrid -> agentsAPI / tradesAPI / healthAPI
     -> CryptoPro -> MarketGrid -> cryptoAPI / Quick Deploy
     -> OpsMonitorPro -> LiveTradeFeed -> tradesAPI (REST polling)
     -> AgentsPage -> agentsAPI
     -> SettingsPage -> healthAPI

backend/app/main.py
  -> /api/agents  -> SQLModel Agent
  -> /api/trades  -> SQLModel Trade
  -> /api/crypto  -> market-data router
  -> /api/estado  -> AgentEngine state
  -> /health      -> API + AgentEngine health

Persistencia: backend/automaton.db (SQLite, generado localmente)
```

El único cliente HTTP del frontend activo es `frontend/src/lib/api.js`.

## Contrato de agentes

El modelo activo usa:

- `nombre`
- `estrategia`: `S1`, `S2`, `S3`, `S4`
- `presupuesto_inicial`
- `presupuesto_actual`
- `estado`: `ACTIVO`, `MUERTO`, `REPLICADO`
- `padre_id`
- `umbral_replica`

El frontend adapta ese contrato para su presentación, pero no introduce una segunda fuente de verdad.

## Monitor y dashboard

El dashboard no contiene KPIs inventados: deriva agentes activos, win rate, PnL y trades de los endpoints SQLModel existentes.

El monitor operativo no simula un feed "live" ni abre un WebSocket inexistente. Lee trades persistidos cada 5 segundos desde `/api/trades/`.

## Variables de entorno

Para el frontend:

```env
VITE_API_URL=http://127.0.0.1:8000
```

`normalizeApiBase()` añade `/api` exactamente una vez.

## Testing

```bash
cd frontend && npm test
cd backend && pytest tests/ -v
```

La CI contiene estos pasos, pero su ejecución depende de disponibilidad de GitHub Actions.

## Legacy preservado

Siguen versionados componentes de la arquitectura anterior —MongoDB, modelos Pydantic ricos, servicios de trading/paper trading, auth, pagos, notificaciones y páginas antiguas— porque eliminarlos sin una migración o decisión explícita sería destructivo. Están **fuera de `app.main`** y no deben montarse simplemente para hacer funcionar una pantalla nueva.

Para el detalle técnico y la clasificación de capas, ver [ARCHITECTURE.md](ARCHITECTURE.md).
