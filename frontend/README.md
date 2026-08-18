# AUTOMATON Frontend

React 19 + Vite frontend for the AUTOMATON trading-agent platform.

## Product truthfulness

The UI is an observation/control layer. It must not fabricate financial activity.

Every financial view must distinguish the evidence mode when relevant:

- Synthetic/Test
- Backtest
- Paper
- Live

Missing market/financial data is shown as unavailable (`N/D` or equivalent), never replaced with random or demo values that resemble real performance. Synthetic/demo data is allowed only in explicitly labelled development/test contexts.

## Current routes

`src/App.jsx` currently mounts:

- `/` — DashboardPro
- `/crypto` — CryptoPro
- `/monitor` — OpsMonitorPro
- `/agents` — AgentsPage
- `/settings` — SettingsPage

Other preserved pages are legacy until deliberately migrated or deleted.

## API

Active calls go through `src/lib/api.js`.

```env
VITE_API_URL=http://127.0.0.1:8000
```

Do not create a second active API client to access legacy endpoints.

## Target UI responsibilities

As Paper Trading is built, the frontend should expose data from the canonical backend domains rather than calculate competing financial truth. Important future views include mode/provenance, market-data freshness, orders/fills/positions, account equity/PnL, risk blocks/circuit breakers, agent evidence and run/session identity.

## Commands

```bash
npm install
npm run dev
npm test
npm run build
```

Vite default: `http://localhost:5173`.
