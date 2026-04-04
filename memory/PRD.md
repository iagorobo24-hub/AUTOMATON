# Automaton Orchestrator - PRD

## Problem Statement
Crear una plataforma de agentes autoreplicados (inspirada en Automaton) con acciones monetarias reales. El sistema incluye un orquestador principal ("cerebro") que gestiona agentes que se replican según rendimiento o se autodestruyen cuando llegan a 0€.

## User Personas
- **Traders**: Buscan automatización para análisis y trading crypto
- **Inversores**: Quieren gestión pasiva con agentes autónomos
- **Emprendedores Tech**: Exploran nuevos modelos de negocio con AI
- **Entusiastas Crypto/AI**: Experimentan con agentes autoreplicantes

## Core Requirements (Static)
1. Sistema de agentes autoreplicantes basado en rendimiento
2. Análisis de mercado crypto en tiempo real
3. Integración de pagos (Stripe + Crypto)
4. Chat con orquestador AI (múltiples LLMs)
5. Dashboard cyberpunk con métricas en vivo
6. Gestión del ciclo de vida de agentes
7. **Base de datos estructurada para escalabilidad y herencia**

## Database Architecture (NEW)
Ver `/app/docs/DATABASE_ARCHITECTURE.md` para documentación completa.

### Colecciones Principales:
- **agents**: Agentes con jerarquía, linaje, finanzas, performance, trading_stats
- **strategies**: Estrategias de trading heredables con indicadores y reglas
- **trades**: Historial de operaciones con entrada/salida/resultado detallado
- **positions**: Posiciones abiertas con PnL en tiempo real
- **wallets**: Billeteras individuales por agente con múltiples assets
- **risk_profiles**: Perfiles de riesgo heredables
- **signals**: Señales de trading compartidas
- **market_data**: Datos de mercado con indicadores precalculados
- **agent_lineages**: Árboles genealógicos completos
- **audit_logs**: Registros inmutables con hash de integridad
- **orchestrator_state**: Estado global del sistema

### Características de Herencia (Clonación):
- Estrategias heredables con mutación opcional
- Perfiles de riesgo heredables
- Tracking de generaciones (G1, G2, G3...)
- Árbol genealógico completo (root → children → descendants)
- Estadísticas de linaje (survival rate, combined ROI)

## What's Been Implemented
**Date: 2026-04-04**

### Backend v2.0 (FastAPI + MongoDB)
- ✅ Schema completo de agentes con 12 colecciones
- ✅ Sistema de linaje y árbol genealógico
- ✅ Herencia de estrategias y perfiles de riesgo
- ✅ Audit logging con hash de integridad
- ✅ CRUD de Agentes con modelo completo
- ✅ Replicación con herencia y mutación
- ✅ Simulación de trades con actualización de stats
- ✅ Integración CoinGecko (top coins, trending, histórico)
- ✅ Integración Stripe (pagos con tarjeta + crypto)
- ✅ Chat con Orquestador AI (GPT-4o)
- ✅ Dashboard stats comprehensivo
- ✅ **Quick Actions API**: Pause All, Resume All, Emergency Stop
- ✅ **Portfolio History API**: Datos reales de gráfico basados en trades
- ✅ **Notifications API**: Sistema completo de notificaciones
- ✅ **Trading Engine**: Motor de trading con datos reales de Binance (paper trading)
- ✅ **Regime Detector**: Detección automática de régimen de mercado (tendencia, rango, compresión)
- ✅ **Strategy Alpha**: Momentum Rider v2.0 implementada como código ejecutable
- ✅ **Strategy Beta**: Range Scalper v2.0 implementada como código ejecutable
- ✅ **Strategy Gamma**: Breakout Hunter v2.0 implementada como código ejecutable
- ✅ **Risk Manager**: Gestión de riesgo centralizada con circuit breaker
- ✅ **Portfolio Snapshots**: Background worker para snapshots periódicos cada 15 min
- ✅ **BinanceService**: Integración con python-binance (soporte testnet y mainnet)
- ✅ **Technical Indicators**: EMA, RSI, ATR, MACD, Bollinger Bands (implementación pura)
- ✅ **Trading Router**: Endpoints para estado del engine, régimen, riesgo y posiciones

### Frontend (React + Tailwind)
- ✅ Login page (estilo Electric Void)
- ✅ Dashboard Bento Grid con métricas KPI (Win Rate, PnL 24h, Tokens Used)
- ✅ **Quick Actions Panel**: Deploy, Pause All/Resume, Emergency Stop
- ✅ **Emergency Stop Dialog**: Modal de confirmación con advertencias
- ✅ **Command Palette**: Navegación rápida (⌘K) con búsqueda
- ✅ **System Health Gauge**: Indicador visual del estado del sistema
- ✅ **Agent Distribution Pie Chart**: Distribución visual de estados
- ✅ **Portfolio Performance Chart**: Gráfico conectado a datos reales con selector de período
- ✅ **Notifications Dropdown**: Bell icon con botones Read All, Clear y X funcionales
- ✅ Agents page con visualización de generación y clones
- ✅ Crypto page (lista de coins, charts, trending)
- ✅ Wallet page (balance, funding, transacciones)
- ✅ Chat page (conversación con Orquestador AI)
- ✅ Activity page (feed de actividad filtrable)
- ✅ Settings page (configuración del sistema)
- ✅ **Animaciones del Dashboard**: Contadores animados, confeti para replicación, shake para dying
- ✅ **Traducción completa al Castellano**: Toda la UI traducida con coherencia

### Integraciones
- ✅ CoinGecko API (datos crypto en tiempo real)
- ✅ Stripe Checkout (pagos con tarjeta y crypto)
- ✅ Emergent LLM Key (OpenAI GPT-4o)

## Prioritized Backlog

### P0 (Critical)
- Ninguno pendiente

### P1 (High Priority)
- ~~Background worker para snapshots periódicos del portfolio~~ ✅ DONE
- ~~Implementar ejecución real de trades (Binance API)~~ ✅ DONE (paper trading activo)
- ~~Auto-replicación automática cuando ROI > 50%~~ ✅ DONE (ReplicationService corriendo)
- ~~Sistema de señales activas compartidas entre agentes~~ ✅ DONE (signals router + DB)
- Configurar API keys de Binance testnet para paper trading real
- Activar modo paper trading con datos reales de mercado

### P2 (Medium Priority)
- Dashboard widgets arrastrables/reorganizables
- Árbol visual de jerarquía de agentes (family tree)
- Alpha Vantage para análisis técnico avanzado
- Múltiples LLMs (Claude, Gemini) con selección automática
- Alertas de precio crypto personalizables

### P3 (Nice to have)
- Backtesting de estrategias
- Exportar datos a CSV
- Webhooks para eventos de agentes
- API pública documentada

## Next Tasks
1. Implementar background worker para snapshots periódicos del portfolio
2. Añadir intervalos granulares al gráfico (15 min, 1 hora, 24 horas)
3. Implementar árbol visual de jerarquía de agentes
4. Conectar con exchange real (Binance) para ejecutar trades

## Refactoring Pendiente
- Dividir `server.py` en routers más pequeños (`/routers/agents.py`, `/routers/dashboard.py`)
- Extraer tarjetas de métricas del dashboard en componente reutilizable
