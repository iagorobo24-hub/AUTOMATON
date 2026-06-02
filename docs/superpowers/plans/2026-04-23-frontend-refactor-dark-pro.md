# AUTOMATON Frontend Refactor (Dark Professional v1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sustituir el frontend actual por el sistema de alta densidad "Dark Professional v1" con arquitectura modular y conectividad real.

**Architecture:** Domain-Driven Design (Feature-based). Aislamiento total por módulos (Crypto, Dashboard, Agents) con estado de servidor gestionado por TanStack Query y tiempo real vía WebSockets.

**Tech Stack:** React 19, Vite, TailwindCSS v4, shadcn/ui, TanStack Query, Zustand, Lucide React (Icons).

---

### Tarea 1: Scaffolding y Estructura de Dominios
**Archivos:**
- Modificar: `frontend/package.json` (upgrade deps)
- Crear: Estructura de carpetas en `src/features/` y `src/shared/`
- Modificar: `frontend/vite.config.js` (alias setup)

- [ ] **Paso 1: Actualizar dependencias a React 19 y TanStack Query v5**
- [ ] **Paso 2: Crear estructura de carpetas por dominios:** `features/{dashboard,agents,ops-monitor,crypto,memory,settings}`
- [ ] **Paso 3: Configurar alias `@/` en Vite para apuntar a `src/`**
- [ ] **Paso 4: Commit**

### Tarea 2: Core Design System (Autonomous Command)
**Archivos:**
- Crear: `src/styles/theme.css` (Tailwind variables)
- Crear: `src/shared/components/ui/` (Buttons, Cards, Badges con estilo Dark Pro)

- [ ] **Paso 1: Inyectar variables de color y tipografía Geist Mono/Sans en el CSS global**
- [ ] **Paso 2: Crear componente `Card` con bordes de 1px y fondo `#1a211d`**
- [ ] **Paso 3: Crear componente `Button` con variante "Emerald" (Primary)**
- [ ] **Paso 4: Commit**

### Tarea 3: Capa de Conectividad (API & WS)
**Archivos:**
- Crear: `src/shared/lib/api-client.js` (Axios/Fetch con TanStack Query wrapper)
- Crear: `src/shared/hooks/useTradingSocket.js`

- [ ] **Paso 1: Implementar cliente de API base con interceptores de error**
- [ ] **Paso 2: Crear Hook `useTradingSocket` para suscripción a canales de precio y eventos**
- [ ] **Paso 3: Commit**

### Tarea 4: Feature - Crypto Tactical Terminal
**Archivos:**
- Crear: `src/features/crypto/components/MarketGrid.jsx`
- Crear: `src/features/crypto/hooks/useMarketData.js`
- Crear: `src/features/crypto/hooks/useQuickDeploy.js`

- [ ] **Paso 1: Implementar Tabla de alta densidad con Sparklines y métricas RSI**
- [ ] **Paso 2: Implementar lógica de "Quick Deploy" instantáneo (Llamada a `POST /agents/replicate`)**
- [ ] **Paso 3: Commit**

### Tarea 5: Feature - Dashboard & Monitor
**Archivos:**
- Crear: `src/features/dashboard/components/BentoGrid.jsx`
- Crear: `src/features/ops-monitor/components/LiveTradeFeed.jsx`

- [ ] **Paso 1: Implementar KPIs animados y Gráfico de Portfolio real-time**
- [ ] **Paso 2: Implementar Feed de Operaciones con PnL dinámico**
- [ ] **Paso 3: Commit**

### Tarea 6: Integración Final y Cleanup
- [ ] **Paso 1: Configurar Router principal para sustituir las rutas antiguas**
- [ ] **Paso 2: Verificar persistencia de estados de "Simulación"**
- [ ] **Paso 3: Ejecutar build de producción y validar en Electron**
- [ ] **Paso 4: Final Commit**
