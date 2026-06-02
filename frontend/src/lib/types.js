/**
 * @fileoverview JSDoc type definitions for AUTOMATON
 */

/**
 * @typedef {Object} Agent
 * @property {string} id
 * @property {string} nombre
 * @property {'monitor'|'orchestrator'|'executor'|'scraper'|'dispatcher'|'other'} type
 * @property {'ACTIVO'|'IDLE'|'ERROR'|'MUERTO'|'REPLICADO'} estado
 * @property {number} presupuesto_inicial
 * @property {number} presupuesto_actual
 * @property {number} tasks_completed
 * @property {number} memory_usage
 * @property {string} last_active - ISO timestamp
 * @property {string} created_at - ISO timestamp
 * @property {string} estrategia
 */

/**
 * @typedef {Object} MemoryEntry
 * @property {string} id
 * @property {string} key
 * @property {string} value
 * @property {string} agent_id
 * @property {string} session_id
 * @property {string} created_at - ISO timestamp
 * @property {string} updated_at - ISO timestamp
 */

/**
 * @typedef {Object} ActivityItem
 * @property {string} id
 * @property {'agent_start'|'error'|'memory_write'|'task_complete'|'trade'} type
 * @property {string} message
 * @property {string} timestamp - ISO timestamp
 * @property {string} [agent_id]
 */

/**
 * @typedef {Object} AgentStats
 * @property {number} total_agents
 * @property {number} active_agents
 * @property {number} idle_agents
 * @property {number} error_agents
 * @property {number} total_tasks
 * @property {number} memory_usage_percent
 * @property {number} uptime_hours
 * @property {number} win_rate_percent
 * @property {number} total_trades
 * @property {number} profit_total
 */

/**
 * @typedef {Object} SystemState
 * @property {number} agentes_activos
 * @property {number} agentes_muertos
 * @property {number} agentes_replicados
 * @property {number} profit_total
 * @property {Record<string, number>} precios_actuales
 */

/**
 * @typedef {Object} Trade
 * @property {string} id
 * @property {string} agent_id
 * @property {string} symbol
 * @property {'buy'|'sell'} side
 * @property {number} amount
 * @property {number} price
 * @property {string} timestamp
 * @property {'pending'|'completed'|'failed'} status
 */

export {};
