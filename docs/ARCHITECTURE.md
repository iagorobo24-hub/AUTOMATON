# Arquitectura Frontend — AUTOMATON v2

Este documento describe la arquitectura técnica del frontend de AUTOMATON tras el refactor a la versión "Dark Professional".

---

## 1. Flujo de Datos General

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINT                               │
│                     frontend/src/main.jsx                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  QueryClientProvider (TanStack Query)                    │   │
│  │  ErrorBoundary                                           │   │
│  │  └── App.jsx                                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ROUTING LAYER                                │
│                      frontend/src/App.jsx                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  BrowserRouter (React Router v7)                         │   │
│  │  ├── /              → DashboardPro                        │   │
│  │  ├── /crypto        → CryptoPro                          │   │
│  │  ├── /monitor       → OpsMonitorPro                      │   │
│  │  ├── /agents        → AgentsPage                        │   │
│  │  └── /settings      → SettingsPage                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PAGES / VIEWS                               │
│                   frontend/src/pages/                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │DashboardPro │  │  CryptoPro  │  │OpsMonitorPro│             │
│  │  (Bento)    │  │  (Market)   │  │  (LiveFeed) │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FEATURE MODULES                               │
│                 frontend/src/features/                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│  │    dashboard/   │ │     crypto/     │ │   ops-monitor/  │  │
│  │  BentoGrid.jsx  │ │  MarketGrid.jsx │ │ LiveTradeFeed   │  │
│  │                 │ │                 │ │    .jsx         │  │
│  │                 │ │ useMarketData() │ │                 │  │
│  │                 │ │ useQuickDeploy()│ │                 │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SHARED RESOURCES                             │
│                   frontend/src/shared/                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  hooks/         │ │ components/     │ │     lib/        │   │
│  │useTradingSocket │ │   (UI kit)      │ │   api-client    │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API LAYER                                    │
│                    frontend/src/lib/api.js                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  axios instance with interceptors                        │   │
│  │  baseURL: import.meta.env.VITE_API_URL                   │   │
│  │                                                          │   │
│  │  API namespaces:                                         │   │
│  │  • agentsAPI  • dashboardAPI  • cryptoAPI                │   │
│  │  • tradingAPI • notificationsAPI • systemAPI             │   │
│  │  • chatAPI    • strategiesAPI  • simulationAPI           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND API                                  │
│              FastAPI on http://127.0.0.1:8000                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Estructura de Carpetas

```
frontend/src/
│
├── main.jsx                 # Entry point: ReactDOM + QueryClient
├── App.jsx                  # Router principal con rutas Pro
├── index.css                # Tailwind v4 con @theme
├── App.css                  # Estilos adicionales de la app
│
├── pages/                   # 17 páginas de la aplicación
│   ├── ActivityPage.jsx
│   ├── Agents.jsx           # Legacy (mantiene compatibilidad)
│   ├── AgentsPage.jsx       # Nueva gestión de agentes
│   ├── ChatPage.jsx
│   ├── CryptoPage.jsx       # Página crypto legacy
│   ├── CryptoPro.jsx        # Terminal táctico (nuevo)
│   ├── Dashboard.jsx        # Dashboard legacy
│   ├── DashboardPage.jsx    # Dashboard legacy extendido
│   ├── DashboardPro.jsx     # Dashboard Pro con BentoGrid
│   ├── LoginPage.jsx
│   ├── Memory.jsx
│   ├── OpsMonitorPro.jsx    # Monitor operativo Pro
│   ├── Settings.jsx         # Settings legacy
│   ├── SettingsPage.jsx     # Settings Pro (usa cn() de utils)
│   ├── SimulationPage.jsx
│   ├── Trades.jsx
│   └── WalletPage.jsx
│
├── features/               # Módulos por dominio (feature-based)
│   ├── agents/
│   │   └── .gitkeep
│   ├── crypto/
│   │   ├── .gitkeep
│   │   ├── components/
│   │   │   └── MarketGrid.jsx      # Tabla de mercado táctico
│   │   └── hooks/
│   │       ├── useMarketData.js    # TanStack Query hook
│   │       └── useQuickDeploy.js   # Mutación de deploy rápido
│   ├── dashboard/
│   │   ├── .gitkeep
│   │   └── components/
│   │       └── BentoGrid.jsx       # Grid estilo Bento
│   ├── memory/
│   │   └── .gitkeep
│   ├── ops-monitor/
│   │   ├── .gitkeep
│   │   └── components/
│   │       └── LiveTradeFeed.jsx   # Feed de trades en tiempo real
│   └── settings/
│       └── .gitkeep
│
├── components/             # Componentes compartidos
│   ├── agents/
│   │   ├── AgentDetailPanel.jsx
│   │   └── AgentTable.jsx
│   ├── dashboard/
│   │   ├── ActivityFeed.jsx
│   │   ├── AgentOverview.jsx
│   │   └── StatCard.jsx
│   ├── layout/
│   │   ├── Breadcrumbs.jsx
│   │   ├── DashboardLayout.jsx
│   │   ├── Layout.jsx
│   │   ├── Sidebar.jsx
│   │   └── TopBar.jsx
│   ├── memory/
│   │   ├── (componentes de memoria)
│   │   └── (hooks de memoria)
│   ├── neural-fiber/
│   │   └── (6 componentes de fibra neural)
│   ├── shared/
│   │   ├── CodeBlock.jsx
│   │   ├── EmptyState.jsx
│   │   ├── ErrorBoundary.jsx
│   │   └── StatusBadge.jsx
│   └── ui/                 # 46 componentes shadcn/ui
│       ├── accordion.jsx
│       ├── alert.jsx
│       ├── avatar.jsx
│       ├── button.jsx
│       ├── card.jsx
│       └── ... (40 más)
│
├── hooks/                  # Custom React hooks
│   ├── use-toast.js        # Sistema de notificaciones toast
│   ├── useAppMode.js       # Modo simulación vs normal
│   └── usePullToRefresh.js # Pull to refresh para móvil
│
├── lib/                    # Utilidades y configuración
│   ├── api.js              # Cliente API centralizado (axios)
│   ├── mockData.js         # Datos mock para desarrollo
│   ├── types.js            # Tipos TypeScript (JSDoc)
│   └── utils.js            # cn() para merge de clases Tailwind
│
├── shared/                 # Recursos compartidos cross-feature
│   ├── components/
│   │   └── ui/
│   │       └── (botones, cards reusables)
│   ├── hooks/
│   │   └── useTradingSocket.js   # WebSocket para trading
│   ├── layouts/
│   │   └── .gitkeep
│   └── lib/
│       └── (utilidades compartidas)
│
└── styles/
    └── theme.css           # Variables de tema legacy
```

---

## 3. Sistema de Estilos (Tailwind CSS v4)

### Configuración

Tailwind v4 usa CSS-only configuration (sin `tailwind.config.js`):

```css
/* frontend/src/index.css */
@import "tailwindcss";

@theme {
  --color-background: #0e1511;
  --color-surface: #1a211d;
  --color-emerald-pro: #10b981;
  --color-border-pro: #3c4a42;
  --font-geist: "Geist", sans-serif;
  --font-geist-mono: "Geist Mono", monospace;
  
  /* Legacy HSL mappings for shadcn compatibility */
  --color-primary: hsl(160 84% 39%);
  --color-secondary: hsl(0 0% 16%);
  --color-muted: hsl(0 0% 16%);
  --color-accent: hsl(160 84% 39%);
  --color-destructive: hsl(0 84% 60%);
  --color-border: hsl(0 0% 20%);
  --color-input: hsl(0 0% 20%);
  --color-ring: hsl(160 84% 39%);
}
```

### Cambios de Tailwind v3 a v4

| Aspecto | Tailwind v3 | Tailwind v4 |
|---------|-------------|-------------|
| Config | `tailwind.config.js` | CSS-only `@theme` |
| Import | `@tailwind` directives | `@import "tailwindcss"` |
| Variables | `theme.extend.colors` | `@theme { --color-* }` |
| Plugins | JS config | CSS-native |

### Clases de Utilidad Personalizadas

```css
/* Componentes de UI Evo (Emerald Pro) */
.evo-input         /* Inputs con estilo oscuro */
.evo-button-primary /* Botón primario emerald */
.evo-button-outline /* Botón outline */
.evo-button-destructive /* Botón peligro */
.evo-badge-*       /* Badges de estado */
.evo-section-title /* Títulos de sección */
.glass-card        /* Tarjetas con efecto glass */
```

---

## 4. Flujo de Datos API

### Cliente API Centralizado (`src/lib/api.js`)

```javascript
// Configuración base
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Interceptores para error handling uniforme
api.interceptors.response.use(
  (response) => response,
  (error) => { /* unified error handling */ }
);
```

### Namespaces de API

| Namespace | Métodos | Descripción |
|-----------|---------|-------------|
| `agentsAPI` | list, create, get, updateStatus, replicate, delete, deposit, simulateTrade, getTrades, getWallet, getLineage, pauseAll, resumeAll, emergencyStop | Gestión completa de agentes |
| `dashboardAPI` | stats, portfolioHistory | Métricas del dashboard |
| `cryptoAPI` | topCoins, trending, price, history | Datos de mercado crypto |
| `tradingAPI` | engineStatus, start, stop, regime, risk, positions | Control del motor de trading |
| `notificationsAPI` | list, count, markRead, markAllRead, dismiss, dismissAll, activity | Sistema de notificaciones |
| `systemAPI` | mode, setMode, resetAgents | Configuración del sistema |
| `simulationAPI` | status, start, stop, reset | Control de simulación |

### Hooks de Datos (TanStack Query)

```javascript
// Ejemplo: useMarketData.js
export function useMarketData() {
  return useQuery({
    queryKey: ['market-data'],
    queryFn: async () => {
      const [trending, top] = await Promise.all([
        api.get('/crypto/trending').catch(() => []),
        api.get('/crypto/top').catch(() => []),
      ]);
      // Merge, sanitize, normalize...
    },
    refetchInterval: 30000, // 30 segundos
  });
}
```

---

## 5. Variables de Entorno

### Vite (Frontend)

Las variables deben comenzar con `VITE_`:

```javascript
// Uso en código
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
```

| Variable | Tipo | Descripción | Default |
|----------|------|-------------|---------|
| `VITE_API_URL` | string | URL base del backend | `http://127.0.0.1:8000` |

### Nota sobre `process.env`

En el refactor se migró de:
```javascript
// ANTES (incorrecto en Vite)
process.env.REACT_APP_API_URL

// DESPUÉS (correcto)
import.meta.env.VITE_API_URL
```

**Excepción:** En `api.js` línea 136-137, `healthAPI` aún referencia `process.env` como fallback legacy. Esto se corregirá en futuras versiones.

---

## 6. Estado de la Aplicación

### useAppMode (Simulación vs Normal)

```javascript
// frontend/src/hooks/useAppMode.js
export function useAppMode() {
  const [mode, setModeState] = useState(() => {
    const stored = localStorage.getItem('automaton_mode');
    return validModes.includes(stored) ? stored : 'normal';
  });
  
  return { 
    mode, 
    setMode, 
    toggleMode, 
    isSimulation: mode === 'simulation', 
    isNormal: mode === 'normal' 
  };
}
```

Persistencia en `localStorage` con sincronización cross-tab via `CustomEvent`.

---

## 7. Componentes Principales

### BentoGrid (DashboardPro)

```javascript
// Grid estilo Bento con 4 columnas
// - Portfolio Chart (3x2 celdas)
// - KPI Cards (1x1 cada uno)
// - System Health (1x1)
```

### MarketGrid (CryptoPro)

```javascript
// Tabla táctica de mercado con:
// - Símbolo + nombre del activo
// - Precio en tiempo real
// - Cambio 24h con color
// - RSI con indicador visual
// - Contador de agentes activos
// - Botón Quick Deploy
```

### LiveTradeFeed (OpsMonitorPro)

```javascript
// Feed de operaciones en tiempo real:
// - WebSocket connection status
// - Tabla de trades activos
// - PnL latente calculado
// - Badges de LONG/SHORT
// - Filtros por estado
```

---

## 8. Convenciones de Código

### Importaciones

```javascript
// Orden recomendado:
1. React y librerías externas
2. Componentes de UI (@/components/ui/*)
3. Hooks (@/hooks/*)
4. API y utilidades (@/lib/*)
5. Feature components (@/features/*)
6. Estilos

// Ejemplo:
import { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { agentsAPI } from '@/lib/api';
import { useAppMode } from '@/hooks/useAppMode';
import { cn } from '@/lib/utils';
```

### Nomenclatura

| Tipo | Convención | Ejemplo |
|------|------------|---------|
| Componentes | PascalCase | `AgentCard`, `MarketGrid` |
| Hooks | camelCase con prefix `use` | `useMarketData`, `useAppMode` |
| API methods | camelCase | `agentsAPI.list`, `cryptoAPI.price` |
| Constantes | UPPER_SNAKE_CASE | `GREEN`, `CYAN`, `PERIODS` |
| Archivos JSX | PascalCase | `AgentsPage.jsx` |
| Archivos JS | camelCase | `use-toast.js`, `api.js` |

---

## 9. Dependencias Clave

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.0.0",    // Data fetching
    "axios": "^1.x",                       // HTTP client (añadido en refactor)
    "framer-motion": "^12.38.0",           // Animaciones
    "lucide-react": "^0.400.0",            // Iconos
    "react": "^19.0.0",                    // React
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.1.0",          // Routing
    "recharts": "^3.8.1",                  // Gráficos
    "sonner": "^2.0.7",                    // Toasts
    "tailwindcss": "^4.2.4"               // CSS v4
  }
}
```

---

## 10. Vite Config

```javascript
// frontend/vite.config.js
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

El alias `@/` apunta a `frontend/src/` facilitando imports absolutos.

---

## 11. Notas de Implementación

### Cambios Post-Refactor

1. **`process.env` → `import.meta.env`**: Migración completa en `api.js` excepto fallback en `healthAPI`

2. **Imports corregidos**: `@/shared/*` ahora resuelve correctamente desde `frontend/src/shared/`

3. **`cn()` importado**: `SettingsPage.jsx` ahora importa correctamente `cn` desde `@/lib/utils`

4. **axios instalado**: Requerido por `api.js` para HTTP requests

5. **Tailwind v4**: Eliminado `tailwind.config.js`, ahora configuración pura en CSS con `@theme`

### Rutas del Router

| Ruta | Página | Componente Feature |
|------|--------|-------------------|
| `/` | DashboardPro | BentoGrid |
| `/crypto` | CryptoPro | MarketGrid |
| `/monitor` | OpsMonitorPro | LiveTradeFeed |
| `/agents` | AgentsPage | (inline) |
| `/settings` | SettingsPage | (inline) |

---

*Documentación generada tras el refactor del frontend - Abril 2025*
