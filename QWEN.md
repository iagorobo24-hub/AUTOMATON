# AUTOMATON-QwenCLI — Project Context

## Project Overview

**AUTOMATON** is a self-replicating AI agent orchestration framework with persistent memory, crypto trading capabilities, and emergent behavior. It is a full-stack application consisting of a FastAPI backend (Python), a React frontend (TypeScript), and an Electron desktop client. The system is designed to manage autonomous agents that can replicate based on performance, self-destruct when they reach zero funds, and inherit trading strategies across generations.

### Design Philosophy
- **Theme**: "Electric Void" — Cyberpunk Trading Terminal meets AI Hive Mind
- **Aesthetic**: Neon-on-black, glassmorphism, HUD-style widgets, pulsing glows for active agents
- **Typography**: Rajdhani (headings), JetBrains Mono (data/numbers), Inter (body text)
- **Key Colors**: Primary `#00F3FF` (cyan), Secondary `#7000FF` (purple), Destructive `#FF003C` (red)

---

## Architecture

```
User → Frontend (React/CRACO, Port 3001)
         ↓
       Backend API (FastAPI, Port 8001)
         ↓
  ┌──────┼──────────────┐
  ↓      ↓              ↓
MongoDB  Trading      Replication
(Port    Engine        Service
 27018)  (Binance)    (Paper Trading)
```

> **Port map (QwenCLI)**: Backend `8001`, Frontend `3001`, MongoDB `27018`, Mongo Express `8082`.
> These differ from AUTOMATON-opencode (8000/3000/27017/8081) so both projects can coexist.

### Backend (`backend/`)
- **Framework**: FastAPI (Python)
- **Database**: MongoDB 6.0 (via Docker)
- **Key Services**: Mock Engine, Replication Service, Trading Engine, Portfolio Snapshot Service
- **Integrations**: CoinGecko API, Stripe, Binance (paper trading), OpenAI GPT-4o
- **Main Entry**: `backend/app/main.py`

### Frontend (`frontend/`)
- **Framework**: React 19 + Create React App (via CRACO)
- **Styling**: Tailwind CSS with custom design tokens (Electric Void theme)
- **UI Components**: shadcn/ui (Radix primitives), Recharts, Framer Motion, Lucide icons
- **Routing**: React Router v7
- **Main Entry**: `frontend/src/`

### Desktop (`desktop/`)
- **Framework**: Electron (native wrapper for the frontend)
- **Main Entry**: `desktop/main.js`

### Infrastructure (`.devops/`)
- **Docker Compose**: MongoDB + Mongo Express for local database management
- **Port Mapping**: MongoDB `27017`, Mongo Express `8081`

---

## Key Directories & Files

| Path | Description |
|---|---|
| `backend/app/main.py` | FastAPI app entry point with service startup/shutdown logic |
| `backend/app/api/` | API router definitions |
| `backend/app/services/` | Core services: trading engine, replication, mock engine, portfolio snapshots |
| `backend/app/models/` | MongoDB data models (agents, strategies, trades, wallets, etc.) |
| `backend/app/routers/` | API route handlers (agents, crypto, dashboard, chat, notifications, etc.) |
| `backend_test.py` | API test suite for all endpoints |
| `frontend/src/` | React application source code |
| `frontend/tailwind.config.js` | Tailwind configuration with Electric Void theme |
| `design_guidelines.json` | Complete design system specification (colors, typography, components, motion) |
| `memory/PRD.md` | Product Requirements Document with architecture and backlog |
| `launcher.ps1` | PowerShell script to start the full ecosystem |
| `AUTOMATON.bat` | Windows batch wrapper for the launcher |
| `.devops/docker-compose.yml` | Docker infrastructure (MongoDB + Mongo Express) |
| `.emergent/` | Emergent behavior logic and markers |
| `test_reports/` | Test report outputs in Markdown |

---

## Building & Running

### Full System Launch (Windows)
```powershell
# Using the batch launcher (recommended)
.\AUTOMATON.bat

# Or directly via PowerShell
powershell -ExecutionPolicy Bypass -File .\launcher.ps1
```

The launcher performs:
1. Checks for Docker Desktop
2. Starts MongoDB via `docker-compose`
3. Seeds the database (`backend/app/core/seed.py`)
4. Starts Backend API on **port 8001** (hidden window)
5. Starts Frontend on **port 3001** (hidden window, no browser auto-open)
6. Launches Desktop Electron app (**blocking** — when you close it, all services stop)

> **Note**: The launcher terminal remains occupied while Electron runs. Closing the Electron app
> automatically kills the backend, frontend, and all related processes. No browser tabs are opened.

### Individual Components

**Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\python -m uvicorn app.main:app --reload --port 8001
```

**Frontend:**
```bash
cd frontend
npm install
PORT=3001 npm start
```

**Database:**
```bash
docker-compose -f .devops/docker-compose.yml up -d
# MongoDB accessible at localhost:27018, Mongo Express at localhost:8082
```

**API Testing:**
```bash
python backend_test.py
```

---

## Development Conventions

### Backend (Python)
- FastAPI with async/await patterns
- MongoDB via motor driver
- Structured logging (`logging` module)
- Service registry pattern for shared state (`app/services/registry.py`)
- API versioning via `/api/v1/` prefix

### Frontend (React/TypeScript)
- Named exports for components (`export const ComponentName = ...`)
- Default exports for pages (`export default function PageName() {...}`)
- shadcn/ui component conventions (use existing components from `src/components/ui/`)
- `data-testid` attributes required on all interactive elements for accessibility
- Sonner for toast notifications (`src/components/ui/sonner.tsx`)
- Framer Motion for animations — avoid generic `transition: all`
- No centered `.App { text-align: center }` — disrupts natural reading flow

### Design Rules
- Follow the E1 "Electric Void" identity strictly
- No generic AI aesthetics ("AI slop")
- Use 2-3x more spacing than feels comfortable
- Micro-animations on every interaction (hover, transitions, entrance animations)
- Subtle grain textures, noise overlays for depth
- Glassmorphism with `backdrop-blur-xl` and `bg-black/60`

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| **Backend** | Python 3, FastAPI, Uvicorn, Motor (MongoDB driver) |
| **Database** | MongoDB 6.0 |
| **Frontend** | React 19, TypeScript, Tailwind CSS, CRACO |
| **UI Kit** | shadcn/ui, Radix UI, Recharts, Framer Motion, Lucide React |
| **Desktop** | Electron |
| **Infra** | Docker Compose |
| **External APIs** | CoinGecko, Binance, Stripe, OpenAI GPT-4o |

---

## Current State (as of April 4, 2026)

- **Backend v2.0**: Stable — Full CRUD, trading engine, replication, notifications, LLM integration
- **Frontend**: Stable — Dashboard, agents, crypto, wallet, chat, activity, settings pages complete
- **Memory System**: Stable — Context retention between sessions
- **Emergent Engine**: Experimental — Adaptive behavior logic

### Completed Features
- Agent lifecycle management (deploy, pause, resume, emergency stop)
- Self-replication based on ROI performance
- Paper trading with Binance testnet data
- Market regime detection (trending, ranging, compression)
- Three trading strategies: Momentum Rider, Range Scalper, Breakout Hunter
- Centralized risk manager with circuit breaker
- Portfolio snapshots every 15 minutes
- Notification system
- Command palette (⌘K navigation)
- Full Spanish translation of the UI
