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

## What's Been Implemented
**Date: 2026-01-12**

### Backend (FastAPI + MongoDB)
- ✅ CRUD de Agentes (crear, replicar, destruir, simular trades)
- ✅ Sistema de estados (active, replicating, dying, dead)
- ✅ Integración CoinGecko (top coins, trending, histórico, precios)
- ✅ Integración Stripe (pagos con tarjeta + crypto)
- ✅ Chat con Orquestador AI (GPT-4o via Emergent LLM Key)
- ✅ Dashboard stats API
- ✅ Transaction tracking

### Frontend (React + Tailwind)
- ✅ Login page (estilo Electric Void)
- ✅ Dashboard con métricas, gráficos, crypto ticker
- ✅ Agents page (crear, replicar, destruir, simular)
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
- Implementar Alpha Vantage para análisis técnico (requiere API key del usuario)
- Sistema de notificaciones cuando un agente está "dying"
- Historial de trades por agente
- Auto-replicación automática cuando ROI > 50%

### P2 (Medium Priority)
- Múltiples LLMs (Claude, Gemini) para comparar respuestas
- Sistema de oportunidades de negocio detectadas
- Alertas de precio crypto personalizables
- Métricas de uso de tokens LLM

### P3 (Nice to have)
- Modo oscuro/claro toggle
- Exportar datos a CSV
- Webhooks para eventos de agentes
- API pública documentada

## Next Tasks
1. Agregar Alpha Vantage para análisis financiero más profundo
2. Implementar auto-replicación automática de agentes exitosos
3. Sistema de alertas y notificaciones
4. Panel de oportunidades de negocio detectadas por AI
