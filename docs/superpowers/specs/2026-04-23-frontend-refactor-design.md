# Especificación de Diseño: AUTOMATON Frontend Refactor (Dark Professional v1)

**Fecha:** 2026-04-23
**Estado:** Borrador para Revisión
**Autor:** CTO Gemini CLI

## 1. Visión General
Sustitución completa de la interfaz actual de AUTOMATON por un sistema de alta densidad de información denominado **"Dark Professional v1"**. El objetivo es proporcionar un entorno de monitorización táctica para agentes de trading autónomos, optimizado para el rendimiento y la toma de decisiones rápida.

## 2. Arquitectura Técnica
Se adoptará un patrón de **Arquitectura Modular por Dominios (Feature-based)** para garantizar el aislamiento y la escalabilidad.

### 2.1 Stack Tecnológico
- **Core:** React 19 + Vite (para máxima velocidad de HMR).
- **Estilo:** TailwindCSS v4 + shadcn/ui (basado en el Design System "Autonomous Command").
- **Estado:**
  - **Server State:** TanStack Query v5 (sincronización con FastAPI).
  - **Client State:** Zustand (ligero, para UI y filtros).
- **Comunicación:** WebSockets (FastAPI integration) para precios y eventos de agentes en tiempo real.
- **Tipografía:** Dual stack (Geist Sans para UI, Geist Mono para métricas y logs).

### 2.2 Estructura de Directorios
```text
src/
  features/
    dashboard/       # Panel de Control v1
    agents/          # Gestión de Agentes v1
    ops-monitor/     # Monitor de Operaciones v1
    crypto/          # Terminal Táctica Crypto (Nueva)
    memory/          # Inspector de Memoria v1
    settings/        # Configuración v1
  shared/
    components/      # UI primitives (button, input, card, grid)
    hooks/           # useTradingSocket, useAgentManager, etc.
    lib/             # api.js, utils, constants
    layouts/         # RootLayout, DashboardLayout
```

## 3. Especificación de Pantallas

### 3.1 Crypto Tactical Terminal (Nueva)
- **Grid de Mercado:** Tabla de alta densidad con BTC, ETH, SOL y top coins.
- **Métricas Clave:** Precio (real-time), Variación 24h, RSI (14), Volumen, Agentes Activos.
- **Quick Deploy:** Botón de acción inmediata por fila.
  - **Acción:** Lanza un agente con Estrategia Alpha, Riesgo Moderado y Capital de Prueba ($1,000).
  - **Feedback:** Animación de pulso en verde esmeralda y entrada en el log lateral.
- **Log Lateral:** Feed de eventos de sistema (despliegues, cambios de régimen de mercado).

### 3.2 Panel de Control (Dashboard)
- **Bento Grid:** Layout modular con KPIs animados (Win Rate, PnL Total, Tokens en uso).
- **Visualización:** Gráfico de rendimiento del portfolio (conectado a `PortfolioHistoryAPI`).
- **Quick Actions:** Panel de control global (Pausa Total, Reanudación, Parada de Emergencia).

### 3.3 Monitor de Operaciones
- **Live Feed:** Lista de trades abiertos con PnL latente actualizándose cada segundo.
- **Telemetría:** Logs específicos por cada operación activa.

## 4. Flujo de Datos y Conectividad
1. **Initial Sync:** Al cargar, TanStack Query recupera el estado actual de los agentes y el balance simulado.
2. **WebSocket Stream:** Se abre un túnel con el backend para recibir:
   - `MARKET_UPDATE`: Precios en vivo.
   - `AGENT_EVENT`: Notificaciones de replicación o muerte de agentes.
   - `TRADE_UPDATE`: Ejecución de órdenes simuladas.
3. **Optimistic Updates:** El "Quick Deploy" mostrará el agente en la lista inmediatamente mientras la petición viaja al servidor para mejorar la sensación de velocidad.

## 5. Diseño UI/UX (Technical Minimalism)
- **Colores:** Fondo `#0e1511`, Acentuación `#10b981` (Emerald Green).
- **Bordes:** 1px sólido `#3c4a42`. Sin sombras proyectadas.
- **Interacción:** Transiciones rápidas (150ms) y micro-interacciones de "terminal" (texto que parpadea sutilmente).

---
**CTO Self-Review:**
- Se ha eliminado el Chat IA y el Wallet por ahora para simplificar el MVP.
- Se ha incluido el requisito de "Quick Deploy" instantáneo.
- El diseño es compatible con el backend FastAPI actual.
