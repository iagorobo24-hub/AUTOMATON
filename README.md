# 🤖 AUTOMATON v2

> **Agentes de trading crypto autónomos con estrategias de replicación.**

AUTOMATON v2 es un ecosistema de agentes de trading que operan de forma autónoma, ejecutan estrategias y se replican cuando alcanzan umbrales de profit.

👉 **[Ver Análisis Completo del Sistema y Documentación Visual](docs/ANALYSIS.md)**

---

## 🖼️ Visual Preview

<p align="center">
  <img src="docs/screenshots/dashboard_overview.png" width="45%" alt="Dashboard Overview" />
  <img src="docs/screenshots/agents_management.png" width="45%" alt="Agents Management" />
</p>
<p align="center">
  <img src="docs/screenshots/trades_history.png" width="91%" alt="Trades History" />
</p>

---

## 🚀 Quick Start

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-repo/automaton-v2.git
cd automaton-v2

# 2. Instalar todas las dependencias (Node + Python)
npm run setup

# 3. Iniciar el sistema completo
npm run dev
```

El comando `npm run dev` inicia:
- 🟡 **BACKEND** (FastAPI) en http://127.0.0.1:8000
- 🔵 **FRONTEND** (Vite) en http://localhost:5173  
- 🟣 **ELECTRON** (Desktop app) - espera a que backend y frontend estén listos

---

## �️ Arquitectura

```
AUTOMATON/
├── electron/           # Electron main process
│   ├── main.js
│   ├── preload.js
│   └── package.json
├── frontend/           # React 18 + Vite
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   └── services/api.js
│   └── package.json
├── backend/            # FastAPI + SQLModel + SQLite
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── services/
│   │   │   ├── strategies.py
│   │   │   └── agent_engine.py
│   │   └── routers/
│   │       ├── agents.py
│   │       └── trades.py
│   └── requirements.txt
├── package.json        # Orquestador raíz
└── .env.example
```

### Stack
- **Electron 31** - Desktop shell
- **React 18** + **Vite** - Frontend
- **FastAPI** + **SQLModel** + **SQLite** - Backend
- **Concurrently** + **wait-on** - Orquestación

---

## 📝 Comandos

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Inicia backend + frontend + electron |
| `npm run dev:backend` | Solo FastAPI en :8000 |
| `npm run dev:frontend` | Solo Vite en :5173 |
| `npm run dev:electron` | Solo Electron (espera servicios) |
| `npm run install:all` | Instala deps de npm en todos los dirs |
| `npm run setup` | Instala todo (npm + pip) |

---

## ⚙️ Configuración

Copiar `.env.example` a `.env` y ajustar:

```bash
cp .env.example .env
```

Variables disponibles:
- `FRONTEND_URL` - URL del frontend (default: http://localhost:5173)
- `BACKEND_URL` - URL del backend (default: http://127.0.0.1:8000)

---

## 🧠 Cómo Funciona

1. **Agentes** tienen: nombre, estrategia (S1/S2/S3), presupuesto, umbral de réplica
2. **Estrategias**:
   - **S1** - Momentum: compra si últimos 3 precios suben
   - **S2** - Mean Reversion: compra si precio < media * 0.98
   - **S3** - Breakout: compra si rompe máximo de 10 velas
3. **Ciclo de vida**: cada 5 segundos el engine evalúa señales y actualiza presupuestos
4. **Muerte**: si presupuesto ≤ 0, agente pasa a estado MUERTO
5. **Réplica**: si profit ≥ umbral, agente se replica (crea hijo con presupuesto fresco)
---

## 📁 Estructura del Proyecto

```
AUTOMATON/
├── electron/           # Electron main process
├── frontend/           # React 18 + Vite
├── backend/            # FastAPI + SQLModel
├── package.json        # Orquestador raíz
├── .gitignore
└── README.md
```

---

## �️ Requisitos

- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **npm** >= 9.0.0

---

© 2024 AUTOMATON Team | *Autonomous trading agents*
