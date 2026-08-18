# AUTOMATON Architecture

## Fuente de verdad actual

El runtime que arranca `backend/app/main.py` utiliza FastAPI, SQLModel, SQLite, `AgentEngine` y los routers `agents`, `trades` y `crypto`. No monta el agregador histórico `backend/app/api/api.py` ni los routers Mongo de system/trading/auth/payments/notifications/paper-trading.

## Flujo activo

```text
Electron (opcional)
  -> Vite / React
     -> frontend/src/lib/api.js
        -> FastAPI app.main
           -> agents router -> SQLModel Agent
           -> trades router -> SQLModel Trade
           -> crypto router -> datos de mercado
           -> /api/estado -> AgentEngine
           -> /health -> estado del runtime
              -> SQLite
```

### Frontend activo

`frontend/src/App.jsx` registra exclusivamente:

| Ruta | Vista | Fuente de datos |
|---|---|---|
| `/` | `DashboardPro` | agents/trades/health |
| `/crypto` | `CryptoPro` | crypto + agents Quick Deploy |
| `/monitor` | `OpsMonitorPro` | trades REST polling |
| `/agents` | `AgentsPage` | agents |
| `/settings` | `SettingsPage` | health |

`frontend/src/lib/api.js` es el único cliente HTTP del frontend activo. No existe un WebSocket `/ws/trading` en `app.main`; el monitor utiliza polling REST.

## Dominio Agents

La fuente de verdad es `backend/app/models/sql_models.py` y `backend/app/routers/agents.py`.

Estados válidos: `ACTIVO`, `MUERTO`, `REPLICADO`.

Estrategias válidas: `S1`, `S2`, `S3`, `S4`.

La replicación manual y automática comparten `backend/app/services/agent_replication.py`.

## Trading actual

`AgentEngine` realiza una simulación local sobre BTC y persiste `Trade` en SQLite. No debe confundirse con los servicios históricos `TradingEngine` o `PaperTradingEngine`.

El dashboard usa `/api/trades/stats`, `/api/agents/` y `/health`. El monitor usa `/api/trades/`.

## Arquitectura legacy preservada

El repositorio conserva una arquitectura anterior basada en MongoDB y modelos Pydantic ricos. Incluye, entre otros:

- `backend/app/services/database.py` (`DatabaseService`)
- `backend/app/services/trading_engine.py`
- `backend/app/services/paper_engine.py`
- `backend/app/services/mock_engine.py`
- `backend/app/services/registry.py`
- routers `system.py`, `trading.py`, `paper_trading.py`, `payments.py`, `auth.py`, `notifications.py` y otros
- modelos Pydantic ricos de `backend/app/models/`
- páginas frontend históricas no registradas por `App.jsx`
- infraestructura Mongo histórica como `.devops/docker-compose.yml` e `install-mongodb.ps1`

Estas piezas están **conservadas, no activas**. No deben añadirse a `app.main` para resolver un 404 o satisfacer una pantalla. Cualquier reactivación requiere decidir primero si se migra a SQLModel o se recupera explícitamente esa arquitectura como subsistema independiente.

## Legado y duplicados retirados

La consolidación elimina piezas inequívocamente incompatibles con el runtime actual:

- `frontend/src/services/api.js`: segundo cliente HTTP.
- `frontend/src/shared/lib/api-client.js`: tercer cliente HTTP sin consumidores.
- `frontend/src/shared/hooks/useTradingSocket.js`: cliente de `/ws/trading`, endpoint inexistente.
- `frontend/jest.config.js` y `frontend/setupTests.js`: configuración Jest/CRA mientras el proyecto usa Vitest.
- `frontend/plugins/health-check/*`: plugin webpack no utilizado por Vite.
- tests placeholder que solo comprobaban constantes/estructura y no comportamiento real.
- logs y reportes de tests generados de ejecuciones históricas.
- launchers `_FIXED` duplicados; el launcher Windows canónico delega ahora en `npm run dev`.

## Tooling actual

- Vite en `localhost:5173`.
- Vitest para frontend.
- Uvicorn/FastAPI en `127.0.0.1:8000`.
- `npm run dev` es el orquestador principal y también es usado por `AUTOMATON.bat`/`launcher.ps1`.
- `Makefile` delega en los scripts existentes y no referencia comandos frontend inexistentes.

## Persistencia

`backend/app/database.py` configura SQLite en `./automaton.db` con `check_same_thread=False`. Bases locales, logs, coverage y reportes de test son artefactos de ejecución ignorados por Git.

## Validación

Tests relevantes:

- `backend/tests/test_agents_sqlmodel.py`
- `backend/tests/test_api_integration.py`
- `frontend/src/lib/api.test.js`
- `frontend/src/lib/agentContract.test.js`
- `frontend/src/pages/SettingsPage.test.jsx`
- tests de normalización de dashboard y monitor

La existencia de tests no equivale a ejecución verde; el resultado solo se considera verificado cuando una suite se ejecuta sobre el HEAD correspondiente.
