/**
 * Centralized API client for AUTOMATON Orchestrator
 *
 * Single source of truth for backend communication used by the Dark Pro frontend.
 */
import axios from 'axios';

export function normalizeApiBase(value) {
  const raw = (value || 'http://127.0.0.1:8000').replace(/\/+$/, '');
  return raw.endsWith('/api') ? raw : `${raw}/api`;
}

const API_BASE = normalizeApiBase(import.meta.env.VITE_API_URL);
const BACKEND_BASE = API_BASE.replace(/\/api$/, '');

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Response interceptor for unified error handling ──
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      const message = data?.detail || data?.error || 'An unexpected error occurred';
      console.error(`[API ${status}]`, message);
      return Promise.reject({ status, message, data });
    }
    if (error.request) {
      console.error('[API] No response received — is the backend running?');
      return Promise.reject({ status: 0, message: 'Cannot connect to backend server' });
    }
    console.error('[API]', error.message);
    return Promise.reject({ status: -1, message: error.message });
  }
);

// ── Typed resource methods ──
export const agentsAPI = {
  list: (params = {}) => api.get('/agents/', { params }),
  statusSummary: () => api.get('/agents/status-summary'),
  create: (data) => api.post('/agents/', data),
  get: (id) => api.get(`/agents/${id}`),
  updateStatus: (id, status) => api.patch(`/agents/${id}/status`, { status }),
  replicate: (id, data) => api.post(`/agents/${id}/replicate`, data),
  delete: (id) => api.delete(`/agents/${id}`),
  deposit: (id, amount) => api.post(`/agents/${id}/deposit`, null, { params: { amount } }),
  simulateTrade: (id, profit) => api.post(`/agents/${id}/simulate-trade`, null, { params: { profit } }),
  getTrades: (id) => api.get(`/agents/${id}/trades`),
  getWallet: (id) => api.get(`/agents/${id}/wallet`),
  getLineage: (id) => api.get(`/agents/${id}/lineage`),
  pauseAll: () => api.post('/agents/pause-all'),
  resumeAll: () => api.post('/agents/resume-all'),
  emergencyStop: () => api.post('/agents/emergency-stop', null, { params: { confirm: true } }),
};

export const dashboardAPI = {
  stats: () => api.get('/dashboard/stats'),
  portfolioHistory: (period = '7d') => api.get('/dashboard/portfolio-history', { params: { period } }),
};

export const cryptoAPI = {
  topCoins: () => api.get('/crypto/top-coins'),
  trending: () => api.get('/crypto/trending'),
  price: (coinId) => api.get(`/crypto/price/${coinId}`),
  history: (coinId, days = 7) => api.get(`/crypto/history/${coinId}`, { params: { days } }),
};

export const tradingAPI = {
  engineStatus: () => api.get('/trading/engine/status'),
  start: () => api.post('/trading/engine/start'),
  stop: () => api.post('/trading/engine/stop'),
  regime: () => api.get('/trading/regime'),
  risk: () => api.get('/trading/risk'),
  positions: () => api.get('/trading/positions'),
};

export const paperTradingAPI = {
  setup: () => api.post('/paper-trading/setup'),
  status: () => api.get('/paper-trading/status'),
  positions: () => api.get('/paper-trading/positions'),
  reset: () => api.post('/paper-trading/reset'),
};

export const notificationsAPI = {
  list: (unreadOnly = false, limit = 50) =>
    api.get('/notifications/', { params: { unread_only: unreadOnly, limit } }),
  count: () => api.get('/notifications/count'),
  markRead: (id) => api.post(`/notifications/${id}/read`),
  markAllRead: () => api.post('/notifications/read-all'),
  dismiss: (id) => api.delete(`/notifications/${id}`),
  dismissAll: () => api.delete('/notifications/'),
  activity: (agentId, typeFilter, limit = 100) =>
    api.get('/notifications/activity', { params: { agent_id: agentId, type_filter: typeFilter, limit } }),
};

export const systemAPI = {
  mode: () => api.get('/system/mode'),
  setMode: (mode) => api.post('/system/mode', { mode }),
  resetAgents: (initialCapital = 1000) =>
    api.post('/system/reset-agents', null, { params: { initial_capital: initialCapital } }),
};

export const chatAPI = {
  send: (message, sessionId = 'default') =>
    api.post('/chat/', null, { params: { message, session_id: sessionId }, timeout: 30000 }),
};

export const strategiesAPI = {
  list: () => api.get('/strategies/'),
  create: (data) => api.post('/strategies/', null, { params: data }),
  get: (id) => api.get(`/strategies/${id}`),
};

export const riskAPI = {
  list: () => api.get('/risk/'),
  create: (data) => api.post('/risk/', null, { params: data }),
};

export const auditAPI = {
  logs: (agentId, eventType, limit = 100) =>
    api.get('/audit/', { params: { agent_id: agentId, event_type: eventType, limit } }),
  llmUsage: () => api.get('/audit/llm-usage'),
};

export const signalsAPI = {
  list: (symbol) => api.get('/signals/', { params: symbol ? { symbol } : {} }),
};

export const tradesAPI = {
  list: () => api.get('/trades/'),
  create: (data) => api.post('/trades/', data),
};

export const healthAPI = {
  health: () => axios.get(`${BACKEND_BASE}/health`, { timeout: 15000 }),
  root: () => axios.get(`${BACKEND_BASE}/`, { timeout: 15000 }),
};

export const paymentsAPI = {
  createSession: (amount, packageType) =>
    api.post('/payments/create-session', null, { params: { amount, package_type: packageType } }),
  status: (sessionId) => api.get(`/payments/status/${sessionId}`),
  transactions: () => api.get('/payments/transactions'),
};

export const simulationAPI = {
  status: () => api.get('/simulation/status'),
  start: (capital = 1000, agents = 3) =>
    api.post('/simulation/start', null, { params: { capital, agents } }),
  stop: () => api.post('/simulation/stop'),
  reset: (capital = 1000, agents = 3) =>
    api.post('/simulation/reset', null, { params: { capital, agents } }),
};

export default api;
