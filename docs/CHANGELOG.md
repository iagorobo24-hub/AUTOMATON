# Changelog — AUTOMATON v2

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/spec/v2.0.0.html).

---

## [Unreleased]

### Fixed

- **`process.env` → `import.meta.env`** en `frontend/src/lib/api.js`
  - Reemplazado el uso incorrecto de `process.env.REACT_APP_API_URL` por `import.meta.env.VITE_API_URL`
  - Vite requiere el prefijo `VITE_` para variables de entorno expuestas al cliente
  - Fallback a `http://127.0.0.1:8000` si la variable no está definida

- **Imports rotos `@/shared/*`** corregidos en componentes de feature
  - `BentoGrid.jsx`: import de `@/components/ui/card` verificado
  - `MarketGrid.jsx`: imports de hooks y componentes verificados
  - `LiveTradeFeed.jsx`: import de `@/shared/hooks/useTradingSocket` corregido

- **Import faltante `cn`** añadido en `SettingsPage.jsx`
  - Añadida línea: `import { cn } from "@/lib/utils";`
  - La función `cn()` (clsx + tailwind-merge) es requerida para composición de clases

- **Hook `useTradingSocket`** ubicado correctamente en `frontend/src/shared/hooks/`
  - Exporta: `isConnected`, `lastMessage`, `sendMessage`
  - Reconexión automática cada 3 segundos en caso de desconexión

### Added

- **Dependencia `axios`** instalada en `frontend/package.json`
  - Cliente HTTP para todas las llamadas API
  - Configurado con interceptores para error handling uniforme
  - Base URL configurable via `VITE_API_URL`

- **Nuevas páginas Pro** (interfaz Dark Professional):
  - `DashboardPro.jsx` — Dashboard con estilo Bento Grid
  - `CryptoPro.jsx` — Terminal táctico de mercado crypto
  - `OpsMonitorPro.jsx` — Monitor operativo en tiempo real
  - `AgentsPage.jsx` — Gestión completa de agentes (ya existente, refactorizado)
  - `SettingsPage.jsx` — Configuración del sistema con tabs

- **Componentes Feature** (bajo `frontend/src/features/`):
  - `features/dashboard/components/BentoGrid.jsx` — Grid estilo Bento con KPIs
  - `features/crypto/components/MarketGrid.jsx` — Tabla de mercado con RSI
  - `features/ops-monitor/components/LiveTradeFeed.jsx` — Feed de trades WebSocket

- **Hooks Feature**:
  - `features/crypto/hooks/useMarketData.js` — Query de datos de mercado (30s refresh)
  - `features/crypto/hooks/useQuickDeploy.js` — Mutación de deploy rápido de agentes
  - `shared/hooks/useTradingSocket.js` — WebSocket para trading en tiempo real

- **Estructura shared/**:
  - `shared/components/ui/` — Componentes UI reutilizables
  - `shared/hooks/` — Hooks compartidos entre features
  - `shared/layouts/` — Layouts reutilizables
  - `shared/lib/` — Utilidades compartidas

### Changed

- **Tailwind CSS v4** migración completa:
  - Eliminado `tailwind.config.js` (CSS-only configuration)
  - Nueva sintaxis `@import "tailwindcss"` en `index.css`
  - Variables de tema definidas con `@theme { --color-* }`
  - Añadidas clases de utilidad personalizadas:
    - `.evo-input`, `.evo-button-primary`, `.evo-button-outline`
    - `.evo-badge-*`, `.evo-section-title`, `.glass-card`

- **Frontend entry point** (`main.jsx`) simplificado:
  - QueryClient con `refetchOnWindowFocus: false`
  - ErrorBoundary envolvente
  - Logging de debug en desarrollo

- **Router** (`App.jsx`) actualizado a rutas Pro:
  - Sidebar tipo terminal con navegación monospace
  - Rutas: `/`, `/crypto`, `/monitor`, `/agents`, `/settings`
  - Layout flex con `min-h-screen bg-background`

- **API client** (`lib/api.js`) refactorizado:
  - Ahora usa `axios` en lugar de `fetch`
  - Interceptores de respuesta para error handling
  - Timeouts configurables (15s default, 30s para chat)
  - Namespaces de API organizados por dominio

- **Componentes UI** actualizados a estilo Dark Pro:
  - Colores: `background: #0e1511`, `surface: #1a211d`
  - Color primario: `emerald-pro: #10b981`
  - Bordes: `border-pro: #3c4a42`
  - Fonts: Geist, JetBrains Mono, Rajdhani, Orbitron

### Deprecated

- Páginas legacy mantenidas por compatibilidad:
  - `Dashboard.jsx`, `DashboardPage.jsx` — Usar `DashboardPro.jsx`
  - `CryptoPage.jsx` — Usar `CryptoPro.jsx`
  - `Agents.jsx` — Usar `AgentsPage.jsx`
  - `Settings.jsx` — Usar `SettingsPage.jsx`

### Removed

- **Eliminado** `frontend/tailwind.config.js` — Configuración ahora en CSS
- **Eliminado** soporte directo para `process.env` — Usar `import.meta.env`

### Security

- Variables de entorno con prefijo `VITE_` solo expuestas intencionalmente
- Context isolation en Electron (preload.js)
- CORS configurado para desarrollo local

---

## [2.2.0] — 2025-04-XX

### Added

- Feature: Terminal táctico crypto con despliegue rápido
- Feature: Dashboard estilo Bento Grid
- Feature: Monitor operativo en tiempo real
- Hook: `useTradingSocket` para WebSocket
- Hook: `useMarketData` para datos de mercado
- Hook: `useQuickDeploy` para deploy instantáneo

### Changed

- Actualizado React a v19.0.0
- Actualizado React Router a v7.1.0
- Actualizado TailwindCSS a v4.2.4
- Refactor completo de la arquitectura frontend a feature-based

---

## [2.0.0] — 2025-03-XX

### Added

- Versión inicial de AUTOMATON v2
- Backend FastAPI con SQLModel
- Frontend React + Vite
- Electron shell para desktop
- Sistema de agentes autónomos
- Estrategias de trading: Momentum, Mean Reversion, Breakout
- Paper trading con simulación

---

## Notas de Versión

### Sobre el Versionado

- **MAJOR**: Cambios incompatibles en la API o arquitectura
- **MINOR**: Nuevas features manteniendo compatibilidad
- **PATCH**: Bug fixes y mejoras menores

### Enlaces de Referencia

- [Documentación de Arquitectura](./ARCHITECTURE.md)
- [Documentación de Análisis](./ANALYSIS.md)
- [Repositorio GitHub](https://github.com/iagorobo24-hub/AUTOMATON)

---

*Changelog mantenido por el equipo AUTOMATON*
