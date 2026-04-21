// API service for AUTOMATON v2
// Uses backend at localhost:8000 (or from Electron's window.api.getBackendUrl())

const DEFAULT_BACKEND_URL = 'http://localhost:8000';

// Get backend URL - from Electron API if available, else default
function getBackendUrl() {
  if (typeof window !== 'undefined' && window.api && window.api.getBackendUrl) {
    return window.api.getBackendUrl();
  }
  return DEFAULT_BACKEND_URL;
}

/**
 * Base fetch function with error handling
 * @param {string} endpoint - API endpoint (e.g., '/api/agents')
 * @param {object} options - Fetch options
 * @returns {Promise<any>}
 */
async function fetchApi(endpoint, options = {}) {
  const baseUrl = getBackendUrl();
  const url = `${baseUrl}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`HTTP ${response.status}: ${error}`);
    }
    
    return await response.json();
  } catch (err) {
    console.error(`[API] Error fetching ${endpoint}:`, err);
    throw err;
  }
}

// Agents API
export const getAgents = async () => {
  return fetchApi('/api/agents');
};

export const createAgent = async (data) => {
  const queryParams = new URLSearchParams({
    nombre: data.nombre,
    estrategia: data.estrategia,
    presupuesto: data.presupuesto.toString(),
    umbral: (data.umbral || 0.15).toString(),
  });
  
  return fetchApi(`/api/agents?${queryParams}`, {
    method: 'POST',
  });
};

export const deleteAgent = async (id) => {
  return fetchApi(`/api/agents/${id}`, {
    method: 'DELETE',
  });
};

// Trades API
export const getTrades = async (agentId) => {
  const queryParams = agentId ? `?agente_id=${agentId}` : '';
  return fetchApi(`/api/trades${queryParams}`);
};

export const getStats = async () => {
  return fetchApi('/api/trades/stats');
};

// System API
export const getEstado = async () => {
  return fetchApi('/api/estado');
};

// Export default object with all methods
const api = {
  fetchApi,
  getAgents,
  createAgent,
  deleteAgent,
  getTrades,
  getStats,
  getEstado,
};

export default api;