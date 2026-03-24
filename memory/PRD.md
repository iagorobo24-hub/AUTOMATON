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
**Date: 2026-01-12**

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

### Frontend (React + Tailwind)
- ✅ Login page (estilo Electric Void)
- ✅ Dashboard con métricas, gráficos, crypto ticker
- ✅ Agents page con visualización de generación y clones
- ✅ Crypto page (lista de coins, charts, trending)
- ✅ Wallet page (balance, funding, transacciones)
- ✅ Chat page (conversación con Orquestador AI)

### Integraciones
- ✅ CoinGecko API (datos crypto en tiempo real)
- ✅ Stripe Checkout (pagos con tarjeta y crypto)
- ✅ Emergent LLM Key (OpenAI GPT-4o)

## Prioritized Backlog

### P0 (Critical)
- Ninguno pendiente

### P1 (High Priority)
- Implementar ejecución real de trades (Binance API)
- Auto-replicación automática cuando ROI > 50%
- Sistema de señales activas compartidas entre agentes
- Background jobs para actualización de market_data

### P2 (Medium Priority)
- Alpha Vantage para análisis técnico avanzado
- Múltiples LLMs (Claude, Gemini) con selección automática
- Sistema de oportunidades de negocio detectadas
- Alertas de precio crypto personalizables
- Notificaciones cuando agentes están "dying"

### P3 (Nice to have)
- Backtesting de estrategias
- Modo oscuro/claro toggle
- Exportar datos a CSV
- Webhooks para eventos de agentes
- API pública documentada

## Next Tasks
1. Conectar con exchange real (Binance) para ejecutar trades
2. Implementar background worker para auto-replicación
3. Sistema de señales compartidas entre agentes
4. Visualización del árbol genealógico en el frontend
