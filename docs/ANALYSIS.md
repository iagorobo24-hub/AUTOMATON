# Estado técnico de AUTOMATON v2

## Verificado como runtime actual

- FastAPI + SQLModel + SQLite.
- `AgentEngine` de simulación local.
- Agentes con estrategias S1-S4 y replicación.
- Trades persistidos en SQLModel.
- Terminal Crypto con CoinGecko.
- React 19 + Vite y cinco rutas activas.
- Electron como shell opcional.

## No activo

El repositorio contiene una arquitectura Mongo/TradingEngine histórica con más routers, servicios y modelos. No se monta desde `app.main` y no debe describirse como funcionalidad actual.

En particular, no están activas en este runtime:

- ejecución Live/Paper de Binance;
- cambios de modo de trading;
- MongoDB como fuente de verdad;
- notificaciones, pagos, auth y otros routers legacy;
- WebSocket de trading;
- páginas frontend no registradas en `App.jsx`.

## Integridad de la UI

Las vistas activas deben mostrar únicamente datos observables:

- Dashboard: agentes, estadísticas de trades y health reales.
- Crypto: datos CoinGecko; RSI se muestra N/D si no existe.
- Monitor: trades SQLModel mediante polling; no hay feed WebSocket ficticio.
- Agents: contrato SQLModel.
- Settings: estado del runtime, no controles legacy.

## Próximo trabajo de producto

Antes de añadir trading real o reactivar servicios históricos debe decidirse expresamente entre:

1. migrar la capacidad necesaria a SQLModel y al runtime actual; o
2. sustituir el runtime actual por una arquitectura diferente de forma deliberada.

No se recomienda volver a mezclar ambos stacks de manera incremental.
