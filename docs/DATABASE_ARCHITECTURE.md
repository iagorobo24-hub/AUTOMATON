# Base de datos efectiva

## Fuente de verdad activa

El runtime iniciado por `backend/app/main.py` usa `backend/app/database.py`, SQLModel y un fichero SQLite local (`automaton.db`, ignorado por Git).

Tablas activas principales:

- `Agent`: identidad, nombre, estrategia S1-S4, estado, capital inicial/actual, padre y umbral de réplica.
- `Trade`: agente, precios de entrada/salida, cantidad, tipo, resultado y timestamp.

Los routers `/api/agents` y `/api/trades` operan sobre esta sesión SQLModel. `AgentEngine` usa la misma base de datos mediante `SessionLocal`.

## Replicación

La replicación manual y automática comparten `backend/app/services/agent_replication.py`, evitando dos implementaciones distintas del mismo cambio de estado y creación de descendientes.

## MongoDB legacy

El árbol conserva modelos Pydantic ricos, `DatabaseService`, colecciones Mongo y servicios que fueron parte de una arquitectura anterior. `backend/app/main.py` no inicializa MongoDB ni inyecta `DatabaseService`, y sus routers no forman parte del API activo.

La infraestructura `.devops/docker-compose.yml` se conserva únicamente como soporte histórico mientras se decide si esa arquitectura se elimina o migra. Docker/Mongo no son requisitos de desarrollo del runtime efectivo.

## Regla para cambios nuevos

Cualquier cambio del producto activo debe usar SQLModel/SQLite y el contrato montado por `app.main`. No se debe añadir una segunda fuente de verdad Mongo para completar una feature.
