/**
 * @fileoverview Mock data for AUTOMATON dashboard
 * Used for loading states, fallbacks, and development
 */

/** @typedef {import('./types.js').Agent} Agent */
/** @typedef {import('./types.js').MemoryEntry} MemoryEntry */
/** @typedef {import('./types.js').ActivityItem} ActivityItem */
/** @typedef {import('./types.js').AgentStats} AgentStats */

/** @type {Agent[]} */
export const mockAgents = [
  {
    id: 'agent_001',
    nombre: 'MemoryWatcher_01',
    type: 'monitor',
    estado: 'ACTIVO',
    presupuesto_inicial: 5000,
    presupuesto_actual: 5234.56,
    tasks_completed: 145,
    memory_usage: 45,
    last_active: '2024-01-15T14:32:00Z',
    created_at: '2024-01-01T10:00:00Z',
    estrategia: 'S1',
  },
  {
    id: 'agent_002',
    nombre: 'TaskOrchestrator_02',
    type: 'orchestrator',
    estado: 'ACTIVO',
    presupuesto_inicial: 10000,
    presupuesto_actual: 9876.43,
    tasks_completed: 892,
    memory_usage: 62,
    last_active: '2024-01-15T14:35:00Z',
    created_at: '2023-12-15T09:00:00Z',
    estrategia: 'S2',
  },
  {
    id: 'agent_003',
    nombre: 'TradeExecutor_01',
    type: 'executor',
    estado: 'IDLE',
    presupuesto_inicial: 3000,
    presupuesto_actual: 2845.20,
    tasks_completed: 67,
    memory_usage: 28,
    last_active: '2024-01-15T13:45:00Z',
    created_at: '2024-01-10T11:30:00Z',
    estrategia: 'S3',
  },
  {
    id: 'agent_004',
    nombre: 'DataScraper_03',
    type: 'scraper',
    estado: 'ERROR',
    presupuesto_inicial: 2000,
    presupuesto_actual: 0,
    tasks_completed: 23,
    memory_usage: 0,
    last_active: '2024-01-14T22:15:00Z',
    created_at: '2023-12-20T14:00:00Z',
    estrategia: 'S1',
  },
  {
    id: 'agent_005',
    nombre: 'AlertDispatcher_01',
    type: 'dispatcher',
    estado: 'ACTIVO',
    presupuesto_inicial: 1500,
    presupuesto_actual: 1567.89,
    tasks_completed: 2341,
    memory_usage: 15,
    last_active: '2024-01-15T14:36:00Z',
    created_at: '2024-01-05T08:00:00Z',
    estrategia: 'S2',
  },
];

/** @type {MemoryEntry[]} */
export const mockMemoryEntries = [
  {
    id: 'mem_001',
    key: 'market_data:bitcoin:price',
    value: JSON.stringify({ price: 43250.67, change_24h: 2.34, volume: 28500000000 }),
    agent_id: 'agent_001',
    session_id: 'sess_20240115_001',
    created_at: '2024-01-15T14:30:00Z',
    updated_at: '2024-01-15T14:35:00Z',
  },
  {
    id: 'mem_002',
    key: 'agent_state:TaskOrchestrator_02',
    value: JSON.stringify({ status: 'running', queue_length: 5, active_tasks: 3 }),
    agent_id: 'agent_002',
    session_id: 'sess_20240115_001',
    created_at: '2024-01-15T14:00:00Z',
    updated_at: '2024-01-15T14:35:00Z',
  },
  {
    id: 'mem_003',
    key: 'trade_log:last_execution',
    value: JSON.stringify({ symbol: 'BTC-USD', side: 'buy', amount: 0.5, price: 43250.67, timestamp: '2024-01-15T14:32:00Z' }),
    agent_id: 'agent_003',
    session_id: 'sess_20240115_001',
    created_at: '2024-01-15T14:32:00Z',
    updated_at: '2024-01-15T14:32:00Z',
  },
  {
    id: 'mem_004',
    key: 'config:alert_thresholds',
    value: JSON.stringify({ price_change: 5, volume_spike: 200, timeout_ms: 30000 }),
    agent_id: 'agent_005',
    session_id: 'sess_20240115_001',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T14:00:00Z',
  },
  {
    id: 'mem_005',
    key: 'error_log:DataScraper_03',
    value: 'Connection timeout after 30s. Retrying...',
    agent_id: 'agent_004',
    session_id: 'sess_20240115_001',
    created_at: '2024-01-15T14:15:00Z',
    updated_at: '2024-01-15T14:15:00Z',
  },
];

/** @type {ActivityItem[]} */
export const mockActivityFeed = [
  { id: 'act_001', type: 'agent_start', message: 'MemoryWatcher_01 started monitoring cycle', timestamp: '2024-01-15T14:36:00Z', agent_id: 'agent_001' },
  { id: 'act_002', type: 'task_complete', message: 'Trade executed: BTC-USD buy 0.5 @ $43,250.67', timestamp: '2024-01-15T14:35:00Z', agent_id: 'agent_003' },
  { id: 'act_003', type: 'memory_write', message: 'Updated market data cache (BTC, ETH, SOL)', timestamp: '2024-01-15T14:34:00Z', agent_id: 'agent_001' },
  { id: 'act_004', type: 'agent_start', message: 'TaskOrchestrator_02 dispatched 3 tasks', timestamp: '2024-01-15T14:33:00Z', agent_id: 'agent_002' },
  { id: 'act_005', type: 'error', message: 'DataScraper_03: Connection timeout', timestamp: '2024-01-15T14:32:00Z', agent_id: 'agent_004' },
  { id: 'act_006', type: 'task_complete', message: 'Alert sent to 5 subscribers', timestamp: '2024-01-15T14:30:00Z', agent_id: 'agent_005' },
  { id: 'act_007', type: 'memory_write', message: 'Agent state snapshot saved', timestamp: '2024-01-15T14:28:00Z', agent_id: 'agent_002' },
  { id: 'act_008', type: 'task_complete', message: 'Historical data analysis complete', timestamp: '2024-01-15T14:25:00Z', agent_id: 'agent_001' },
];

/** @type {AgentStats} */
export const mockStats = {
  total_agents: 5,
  active_agents: 3,
  idle_agents: 1,
  error_agents: 1,
  total_tasks: 3469,
  memory_usage_percent: 35,
  uptime_hours: 168,
  win_rate_percent: 67.5,
  total_trades: 145,
  profit_total: 2345.67,
};

/** @type {Record<string, number>} */
export const mockPrices = {
  'BTC-USD': 43250.67,
  'ETH-USD': 2580.45,
  'SOL-USD': 98.76,
  'ADA-USD': 0.52,
  'DOT-USD': 7.34,
};

/**
 * Generate agent logs for detail panel
 * @param {string} agentId
 * @returns {string[]}
 */
export function getMockAgentLogs(agentId) {
  const agent = mockAgents.find(a => a.id === agentId);
  if (!agent) return [];

  return [
    `[${new Date().toISOString()}] Agent ${agent.nombre} initialized`,
    `[${new Date().toISOString()}] Loading configuration from memory...`,
    `[${new Date().toISOString()}] Strategy ${agent.estrategia} loaded successfully`,
    `[${new Date().toISOString()}] Connected to data stream`,
    `[${new Date().toISOString()}] Budget allocated: $${agent.presupuesto_inicial.toFixed(2)}`,
    `[${new Date().toISOString()}] Starting main execution loop`,
    `[${new Date().toISOString()}] Task queue initialized with ${agent.tasks_completed} historical tasks`,
    `[${new Date().toISOString()}] Memory allocation: ${agent.memory_usage}MB`,
    `[${new Date().toISOString()}] Heartbeat registered with orchestrator`,
    `[${new Date().toISOString()}] Status: ${agent.estado}`,
  ];
}

/**
 * Get memory dump preview for agent
 * @param {string} agentId
 * @returns {string}
 */
export function getMockMemoryDump(agentId) {
  const agent = mockAgents.find(a => a.id === agentId);
  if (!agent) return '{}';

  return JSON.stringify({
    agent_id: agent.id,
    nombre: agent.nombre,
    estado: agent.estado,
    presupuesto: {
      inicial: agent.presupuesto_inicial,
      actual: agent.presupuesto_actual,
      delta: agent.presupuesto_actual - agent.presupuesto_inicial,
    },
    metrics: {
      tasks_completed: agent.tasks_completed,
      memory_usage_mb: agent.memory_usage,
      uptime_seconds: 604800,
    },
    last_active: agent.last_active,
  }, null, 2);
}
