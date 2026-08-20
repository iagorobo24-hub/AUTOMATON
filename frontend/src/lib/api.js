/**
 * Centralized API client for the active AUTOMATON SQLModel runtime.
 */
import axios from 'axios';

export function normalizeApiBase(value) {
  const raw = (value || 'http://127.0.0.1:8000').replace(/\/+$/, '');
  return raw.endsWith('/api') ? raw : `${raw}/api`;
}

export function buildPaperMarketOrderParams({ requestId, accountId, symbol, side, quantity }) {
  return { request_id: requestId, account_id: accountId, symbol, side, quantity };
}

const API_BASE = normalizeApiBase(import.meta.env.VITE_API_URL);
const BACKEND_BASE = API_BASE.replace(/\/api$/, '');

const api = axios.create({ baseURL: API_BASE, timeout: 15000, headers: { 'Content-Type': 'application/json' } });

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

export const agentsAPI = {
  list: () => api.get('/agents/'), create: (data) => api.post('/agents/', null, { params: data }), get: (id) => api.get(`/agents/${id}`),
  delete: (id, reason = 'operator_kill') => api.delete(`/agents/${id}`, { params: { reason } }),
  deposit: (id, amount) => api.post(`/agents/${id}/deposit`, null, { params: { amount } }), replicate: (id) => api.post(`/agents/${id}/replicate`),
};

export const cryptoAPI = { topCoins: () => api.get('/crypto/top-coins'), trending: () => api.get('/crypto/trending'), price: (coinId) => api.get(`/crypto/price/${coinId}`), history: (coinId, days = 7) => api.get(`/crypto/history/${coinId}`, { params: { days } }) };
export const tradesAPI = { list: (params = {}) => api.get('/trades/', { params }), stats: () => api.get('/trades/stats') };
export const paperAPI = { status: () => api.get('/paper/status'), executions: (params = {}) => api.get('/paper/executions', { params }), executeMarket: (order) => api.post('/paper/orders/market', null, { params: buildPaperMarketOrderParams(order) }) };
export const riskAPI = { status: () => api.get('/risk/status'), activeProfile: () => api.get('/risk/profiles/active'), decisions: (params = {}) => api.get('/risk/decisions', { params }), pause: () => api.post('/risk/pause'), resume: () => api.post('/risk/resume') };
export const backtestsAPI = { status: () => api.get('/backtests/status'), datasets: (params = {}) => api.get('/backtests/datasets', { params }), dataset: (id) => api.get(`/backtests/datasets/${id}`), createDataset: (params) => api.post('/backtests/datasets', null, { params }), runs: (params = {}) => api.get('/backtests/runs', { params }), run: (id) => api.get(`/backtests/runs/${id}`), createRun: (params) => api.post('/backtests/runs', null, { params }) };
export const evolutionAPI = { status: () => api.get('/evolution/status'), activePolicy: () => api.get('/evolution/policies/active'), evaluateFitness: (agentId) => api.post(`/evolution/agents/${agentId}/fitness`), fitness: (agentId, params = {}) => api.get(`/evolution/agents/${agentId}/fitness`, { params }), lineage: (agentId) => api.get(`/evolution/agents/${agentId}/lineage`) };

export const runtimeAPI = {
  status: () => api.get('/runtime/status'),
  sessions: (params = {}) => api.get('/runtime/sessions', { params }),
  session: (id) => api.get(`/runtime/sessions/${id}`),
  cycles: (id, params = {}) => api.get(`/runtime/sessions/${id}/cycles`, { params }),
  create: ({ name, symbol = 'BTC/USDT', interval = '1m', agentIds, pollSeconds = 15, maxConsecutiveFailures = 5 }) => api.post(
    '/runtime/sessions', null,
    {
      params: { name, symbol, interval, agent_ids: agentIds, poll_seconds: pollSeconds, max_consecutive_failures: maxConsecutiveFailures },
      paramsSerializer: { indexes: null },
    },
  ),
  start: (id) => api.post(`/runtime/sessions/${id}/start`), pause: (id) => api.post(`/runtime/sessions/${id}/pause`),
  resume: (id) => api.post(`/runtime/sessions/${id}/resume`), recover: (id) => api.post(`/runtime/sessions/${id}/recover`), stop: (id) => api.post(`/runtime/sessions/${id}/stop`),
};

export const researchAPI = {
  status: () => api.get('/research/status'),
  activePolicy: () => api.get('/research/policies/active'),
  studies: (params = {}) => api.get('/research/studies', { params }),
  study: (id) => api.get(`/research/studies/${id}`),
  createStudy: ({ name, strategyId, notes }) => api.post('/research/studies', null, { params: { name, strategy_id: strategyId, notes } }),
  windows: (id) => api.get(`/research/studies/${id}/windows`),
  addWindow: (id, role, backtestRunId) => api.post(`/research/studies/${id}/windows`, null, { params: { role, backtest_run_id: backtestRunId } }),
  evaluate: (id) => api.post(`/research/studies/${id}/evaluate`),
  evaluations: (id) => api.get(`/research/studies/${id}/evaluations`),
  promote: (id, note) => api.post(`/research/studies/${id}/promote`, null, { params: { note } }),
  candidates: (params = {}) => api.get('/research/candidates', { params }),
};

export const liveAPI = {
  status: () => api.get('/live/status'),
  policy: () => api.get('/live/policy'),
  readiness: (params = {}) => api.get('/live/readiness', { params }),
  evaluateReadiness: (candidateId) => api.post('/live/readiness/evaluate', null, { params: { candidate_id: candidateId } }),
  emergencyStop: (reason) => api.post('/live/emergency-stop', null, { params: { reason } }),
  clearEmergencyStop: (reason) => api.post('/live/emergency-stop/clear', null, { params: { reason } }),
  reconciliations: (params = {}) => api.get('/live/reconciliations', { params }),
  reconcile: () => api.post('/live/reconcile'),
};

export const stateAPI = { status: () => api.get('/estado') };
export const healthAPI = { health: () => axios.get(`${BACKEND_BASE}/health`, { timeout: 15000 }), root: () => axios.get(`${BACKEND_BASE}/`, { timeout: 15000 }) };

export default api;
