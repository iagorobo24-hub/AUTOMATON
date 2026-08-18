# Arquitectura Frontend — AUTOMATON v2

Este documento describe únicamente el frontend que `frontend/src/App.jsx` monta actualmente.

## Rutas activas

```text
main.jsx
  -> App.jsx
     /          -> DashboardPro -> BentoGrid
     /crypto    -> CryptoPro -> MarketGrid
     /monitor   -> OpsMonitorPro -> LiveTradeFeed
     /agents    -> AgentsPage
     /settings  -> SettingsPage
```

Las demás páginas presentes en `frontend/src/pages/` son históricas y no forman parte del router activo salvo que se incorporen explícitamente en el futuro.

## Cliente API

El único cliente HTTP activo es:

`frontend/src/lib/api.js`

Namespaces soportados por el runtime actual:

- `agentsAPI`
- `cryptoAPI`
- `tradesAPI`
- `stateAPI`
- `healthAPI`

El `baseURL` se normaliza a `/api` exactamente una vez. `/health` y `/` se consultan fuera de ese prefijo.

No se exponen desde este cliente los antiguos contratos `systemAPI`, `tradingAPI`, paper trading, pagos, auth, notificaciones o simulación porque sus routers no están montados por `app.main`.

## Dashboard

`BentoGrid` consulta:

- `/api/agents/`
- `/api/trades/stats`
- `/health`

Los KPIs se derivan de datos persistidos. No contiene cifras de portfolio, win rate, PnL o agentes codificadas como ejemplos.

## Crypto

`MarketGrid` usa `cryptoAPI` y `useMarketData` para normalizar las respuestas de los endpoints `top-coins` y `trending`. Quick Deploy crea un agente SQLModel S1 mediante `/api/agents/`.

## Monitor operativo

`LiveTradeFeed` conserva su nombre por compatibilidad de imports, pero ya no representa un WebSocket. Consulta `/api/trades/` mediante TanStack Query cada 5 segundos y muestra únicamente campos que existen en `Trade` SQLModel.

No existe `/ws/trading` en el backend activo.

## Agents

`AgentsPage` usa `frontend/src/lib/agentContract.js` para adaptar el contrato SQLModel a la presentación Dark Pro sin crear una segunda fuente de verdad.

## Settings

`SettingsPage` es una vista informativa del runtime y consulta `/health`. No presenta controles Live/Paper ni opciones globales que el backend SQLModel no persiste.

## Legacy frontend

Se eliminan dos duplicados inequívocos:

- `frontend/src/services/api.js`, reemplazado por `frontend/src/lib/api.js`.
- `frontend/src/shared/hooks/useTradingSocket.js`, cuyo endpoint nunca estuvo montado en `app.main`.

Otras páginas/componentes históricos se conservan por ahora porque su eliminación completa requiere una decisión separada sobre material de referencia, pruebas manuales y posible reutilización. Su mera presencia no las convierte en runtime activo.
