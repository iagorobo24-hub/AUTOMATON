# AUTOMATON Architecture

## Estructura del Proyecto

```
AUTOMATON/
├── electron/               # Proceso main de Electron (PURO)
│   ├── main.js            # Entry point de Electron
│   ├── preload.js         # Context bridge seguro
│   └── package.json       # Deps de Electron
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── App.jsx        # Componente raíz con routing
│   │   ├── main.jsx       # Entry point Vite
│   │   ├── pages/         # Páginas de la aplicación
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── AgentsPage.jsx
│   │   │   ├── SimulationPage.jsx
│   │   │   └── ...
│   │   ├── components/    # Componentes reutilizables
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # Servicios de API
│   │   │   └── api.js     # Único punto de contacto con backend
│   │   └── lib/           # Utilidades
│   ├── index.html         # HTML entry point (Vite)
│   ├── vite.config.js     # Configuración Vite
│   └── package.json       # Deps de frontend
├── backend/               # FastAPI + SQLModel
│   ├── app/
│   │   ├── main.py        # Entry point FastAPI
│   │   ├── database.py    # Configuración SQLModel + SQLite
│   │   ├── core/
│   │   │   └── config.py  # Settings de la aplicación
│   │   ├── models/
│   │   │   ├── sql_models.py  # Modelos SQLModel (NUEVO)
│   │   │   ├── agent.py   # Modelos Pydantic legacy
│   │   │   ├── trading.py
│   │   │   └── ...
│   │   ├── api/
│   │   │   ├── deps.py    # Deps MongoDB (legacy)
│   │   │   ├── deps_sql.py # Deps SQLModel (NUEVO)
│   │   │   └── api.py     # Router aggregation
│   │   └── routers/       # API endpoints
│   ├── requirements.txt   # Python dependencies
│   └── automaton.db       # SQLite database (auto-generado)
├── package.json           # ROOT: orquesta todo (workspaces)
└── ARCHITECTURE.md        # Este documento
```

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                     ELECTRON (Desktop Shell)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   main.js    │  │  preload.js  │  │   Tray/UI    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│                    FRONTEND (React + Vite)                 │
│  ┌──────────────────────────────────────────────────┐     │
│  │  services/api.js  ←  ÚNICO punto de contacto     │     │
│  └────────────────────────┬───────────────────────────┘     │
│                           │                               │
│  ┌────────────────────────▼───────────────────────────┐   │
│  │  React Components  →  React Router  →  Pages        │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬───────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼───────────────────────────────┐
│                    BACKEND (FastAPI)                       │
│  ┌──────────────────────────────────────────────────┐     │
│  │  API Routers  →  Services  →  SQLModel ORM       │     │
│  └────────────────────────┬───────────────────────────┘     │
│                           │                               │
│  ┌────────────────────────▼───────────────────────────┐   │
│  │  SQLite  +  (Legacy MongoDB support)               │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

## Tecnologías

| Capa | Tecnología | Rol |
|------|-----------|-----|
| Desktop | Electron | Shell nativo, tray, shortcuts |
| Frontend | React 19 + Vite | UI interactiva, SPA |
| Backend | FastAPI | API REST, WebSocket opcional |
| ORM | SQLModel | Type-safe models, migrations |
| Database | SQLite (aiosqlite) | Embeddable, file-based |
| Styling | TailwindCSS | Utility-first CSS |
| Components | Radix UI + shadcn | Accessible headless UI |

## Scripts de Desarrollo

```bash
# Instalar todas las dependencias
npm run install:all

# Desarrollo completo (backend + frontend + electron)
npm run dev

# Individual
npm run dev:backend    # FastAPI en localhost:8000
npm run dev:frontend   # Vite en localhost:3001
npm run dev:electron   # Electron (espera a que suban los otros)

# Construcción
npm run build          # Build frontend + electron
npm run build:all      # Build completo para distribución

# Testing
npm run test           # Test frontend + backend
npm run test:frontend
npm run test:backend

# Database
npm run db:migrate     # Run migrations
npm run db:reset       # Reset SQLite database
```

## Convenciones de Código

### Frontend (React)
- **Componentes**: PascalCase, un componente por archivo
- **Hooks**: use[NombreDescriptivo]
- **Servicios**: api.js es el único punto de contacto con backend
- **Estilos**: Tailwind classes, evitar CSS modules
- **Imports**: Usar `@/` alias para rutas absolutas

### Backend (FastAPI)
- **Routers**: Agrupar por recurso (agents, trades, etc.)
- **Models**: SQLModel para DB, Pydantic para API schemas
- **Servicios**: Lógica de negocio, no en routers
- **Deps**: Inyección de dependencias para DB y auth

## Migración MongoDB → SQLModel

El proyecto está en transición de MongoDB a SQLModel+SQLite:

| MongoDB (Legacy) | SQLModel (Nuevo) |
|-----------------|------------------|
| `motor` async | `aiosqlite` async |
| Documentos JSON | Tablas relacionales + JSON columns |
| `deps.py` | `deps_sql.py` |
| Schemaless | Type-safe con migrations |

Para nuevas features, usar SQLModel. MongoDB permanece para compatibilidad durante la migración.

## Escalabilidad Futura

La arquitectura soporta:

1. **Multi-user**: Tablas User en SQLModel permiten auth multiusuario
2. **Cloud deployment**: Cambiar SQLite por PostgreSQL (misma SQLModel API)
3. **Microservices**: Separar routers en servicios independientes
4. **Real-time**: WebSocket support nativo en FastAPI
5. **Plugins**: Sistema de plugins en services/ con entry points definidos

## Seguridad

- **CORS**: Configurado en backend para localhost:dev ports
- **Auth**: JWT tokens, almacenados en localStorage (frontend)
- **Context Isolation**: Electron preload.js expone solo API necesaria
- **Rate Limiting**: SlowAPI en endpoints sensibles
