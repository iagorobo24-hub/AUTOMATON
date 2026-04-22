# GEMINI.md - Project Context & Instructions

## Project Overview
**AUTOMATON v2** is an autonomous cryptocurrency trading framework designed for self-replicating AI agents. The system enables agents to execute various trading strategies (Momentum, Mean Reversion, Breakout) and "replicate" (spawn new agents) when profit thresholds are met.

### Core Technologies
- **Desktop Shell**: Electron (v31+)
- **Frontend**: React (v18+) with Vite, TailwindCSS, and shadcn/ui.
- **Backend**: FastAPI (Python 3.11+)
- **Database**: Transitioning from **MongoDB** (legacy) to **SQLite** using **SQLModel** (ORM).
- **Trading Engine**: Custom `AgentEngine` with support for Paper and Live trading (Binance API).

---

## Architecture & Structure
The project is organized as a monorepo with three main components:

- `backend/`: FastAPI application.
  - `app/main.py`: Entry point and API definition.
  - `app/routers/`: API endpoints grouped by resource (agents, trades, auth).
  - `app/models/`: SQLModel (SQLite) and Pydantic (API) models.
  - `app/services/`: Core business logic (AgentEngine, Strategy definitions).
  - `app/database.py`: Database connection and session management.
- `frontend/`: React single-page application.
  - `src/services/api.js`: Unified service for all backend communication.
  - `src/pages/`: Main application views (Dashboard, Agents, Simulation).
  - `src/components/ui/`: Reusable UI components (shadcn/ui).
- `electron/`: Desktop integration layer.
  - `main.js`: Main process orchestration.
  - `preload.js`: Secure context bridge.

---

## Building and Running

### Prerequisites
- Node.js >= 18.0.0
- Python >= 3.11
- Docker Desktop (Required for legacy MongoDB container)

### Setup
```bash
# Automated setup for all components
npm run setup
```

### Development
```bash
# Recommended: Run full stack (Backend + Frontend + Electron)
npm run dev

# Alternative: Use Makefile for specific components
make run-backend
make run-frontend
```

### Windows Launcher
For a native experience on Windows, use the provided batch script:
- `AUTOMATON.bat`: Checks prerequisites (Docker) and launches the PowerShell `launcher.ps1`.

---

## Testing
Comprehensive testing is implemented for both layers:

- **Backend**: Uses `pytest`.
  ```bash
  make test-backend
  # or
  cd backend && pytest tests/ -v
  ```
- **Frontend**: Uses `jest` or `vitest`.
  ```bash
  make test-frontend
  ```

---

## Development Conventions

### Backend (Python/FastAPI)
- **Routing**: Always use `APIRouter` in `app/routers/` and include them in `app/api/api.py`.
- **Database**: For new features, strictly use **SQLModel** with SQLite. Avoid direct MongoDB calls unless maintaining legacy code.
- **Dependency Injection**: Use `app/api/deps_sql.py` for database sessions.
- **Logic**: Keep routers lean; encapsulate complex logic within `app/services/`.

### Frontend (React)
- **Styling**: Use **TailwindCSS** utility classes. Avoid custom CSS files where possible.
- **Paths**: Use the `@/` alias to reference the `src/` directory.
- **State**: Prefer React Hooks and Context API for global state.
- **Communication**: All API calls must pass through `src/services/api.js`.

---

## Key Files for Reference
- `ARCHITECTURE.md`: Detailed architectural design and data flow.
- `IMPLEMENTATION_PLAN.md`: Project roadmap and current status.
- `backend/app/main.py`: API entry point.
- `backend/app/services/agent_engine.py`: Core trading logic.
- `frontend/src/App.jsx`: Frontend routing and root component.
- `package.json` (root): Orchestration scripts for the entire project.
