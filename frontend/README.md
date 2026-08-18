# AUTOMATON Frontend

Frontend activo de AUTOMATON basado en React 19 + Vite.

## Comandos

```bash
npm install
npm run dev
npm test
npm run build
```

Vite sirve por defecto en `http://localhost:5173`.

## API

Las llamadas del frontend activo pasan por `src/lib/api.js`. Para cambiar el backend:

```env
VITE_API_URL=http://127.0.0.1:8000
```

El cliente añade `/api` exactamente una vez. `/health` se consulta fuera de ese prefijo.

## Rutas activas

`src/App.jsx` monta:

- `/` — DashboardPro
- `/crypto` — CryptoPro
- `/monitor` — OpsMonitorPro
- `/agents` — AgentsPage
- `/settings` — SettingsPage

Las demás páginas conservadas bajo `src/pages/` son históricas y no forman parte del router activo.

## Tooling

- Build/dev server: Vite.
- Tests: Vitest + jsdom.
- Estilos: Tailwind CSS.
- Datos remotos: Axios/TanStack Query.

La antigua configuración Create React App/Jest/webpack no forma parte del frontend actual.
