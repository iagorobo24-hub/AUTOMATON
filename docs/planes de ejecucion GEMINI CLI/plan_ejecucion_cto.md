# Plan de Ejecución: AUTOMATON Local Orchestrator Alpha
**Versión:** 1.0 (CTO Strategy)
**Fecha:** 3 de abril de 2026

## 🏛️ 0. Arquitectura de Referencia
Arquitectura de **Servicios Desacoplados**:
* **Core:** FastAPI (Asíncrono, validación Pydantic).
* **Data:** MongoDB (Document-oriented para herencia dinámica).
* **UI:** React (Atomic Design, Shadcn/ui).
* **Orchestration:** Docker Compose (para la DB) + Launcher en PowerShell.

## 📂 1. Reestructuración de Carpetas
```text
AUTOMATON/
├── .devops/                # Scripts de orquestación local
│   ├── launcher.ps1        # EL "botón de encendido" de la App
│   └── docker-compose.yml  # Solo para MongoDB y MongoExpress
├── backend/
│   ├── app/
│   │   ├── core/           # Configuración global, seguridad, logs
│   │   ├── models/         # Esquemas Pydantic y DB
│   │   ├── services/       # Lógica de negocio (Trading, Replicación)
│   │   ├── routers/        # Endpoints divididos (agents, crypto, wallet)
│   │   └── main.py         # Punto de entrada limpio
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/            # Cliente de API centralizado (Axios/Fetch)
│   │   ├── components/     # UI Atómica
│   │   ├── hooks/          # Lógica de estado reutilizable
│   │   └── store/          # Estado global (Zustand o Context)
│   └── .env.local
└── data/                   # Persistencia local de MongoDB (ignorado en git)
```

## 🚀 Fase 1: Infraestructura y Simulación (P0)
- [ ] **Tarea 1.1:** Crear `docker-compose.yml` en `.devops/` para MongoDB v6.0 y Mongo Express.
- [ ] **Tarea 1.2:** Refactorizar `backend/server.py` extrayendo routers a `backend/app/routers/`.
- [ ] **Tarea 1.3:** Crear un `MockEngine` para simulación de precios sin API Keys reales.

**Checklist:**
- [ ] `docker-compose up -d` funcional.
- [ ] Swagger UI accesible en `localhost:8000/docs`.
- [ ] Validación de `.env` con `pydantic-settings`.

## 🧠 Fase 2: El Motor de Replicación
- [ ] **Tarea 2.1:** Implementar `ReplicationService` (polling 60s ROI).
- [ ] **Tarea 2.2:** Lógica de Herencia con `mutate_strategy`.
- [ ] **Tarea 2.3:** Sistema de Logs de Auditoría en colección `audit_logs`.

## 🎨 Fase 3: Frontend "Live" y UX Cyberpunk
- [ ] **Tarea 3.1:** Implementar WebSockets/Polling para actualización en tiempo real.
- [ ] **Tarea 3.2:** Crear componente `FamilyTree` (visualización de linaje).
- [ ] **Tarea 3.3:** Pantalla y lógica de "Emergency Stop" global.

## 🛠️ Fase 4: Orquestación Local (One-Click)
- [ ] **Tarea 4.1:** Crear `launcher.ps1` para inicio automatizado.
- [ ] **Tarea 4.2:** Script de `Seed` con agentes iniciales (Adán, Eva, Lilith).

---
## 🔍 Estrategia de Debugging
1. **Logging Middleware:** Trazabilidad de cada request/response.
2. **Strict Pydantic:** Fallo temprano ante cambios de APIs externas.
3. **Frontend Error Boundaries:** Aislamiento de fallos en widgets.
