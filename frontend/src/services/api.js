// API service for AUTOMATON v2
// Uses backend at localhost:8000 (or from Electron's window.api.getBackendUrl())

const DEFAULT_BACKEND_URL = '';

// Get backend URL - from Electron API if available, else default (empty for Vite proxy)
async function getBackendUrl() {
  if (typeof window !== 'undefined' && window.api && window.api.getBackendUrl) {
    return await window.api.getBackendUrl();
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
  const baseUrl = await getBackendUrl();
  const url = `${baseUrl}${endpoint}`;
  
  console.log(`[API] Fetching: ${url}`);
  
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

// ========== CRYPTO API ==========

/**
 * Get top cryptocurrencies by market cap
 * @param {number} limit - Number of coins to return (default 10)
 * @returns {Promise<{coins: Array}>}
 */
export const getTopCoins = async (limit = 10) => {
  return fetchApi(`/api/crypto/top-coins?limit=${limit}`);
};

/**
 * Get trending cryptocurrencies
 * @returns {Promise<{trending: Array}>}
 */
export const getTrending = async () => {
  return fetchApi('/api/crypto/trending');
};

/**
 * Get current price for a specific coin
 * @param {string} coinId - Coin ID (e.g., 'bitcoin', 'ethereum')
 * @returns {Promise<Object>}
 */
export const getCoinPrice = async (coinId) => {
  return fetchApi(`/api/crypto/price/${coinId}`);
};

/**
 * Get price history for a coin
 * @param {string} coinId - Coin ID
 * @param {number} days - Days of history (default 7)
 * @returns {Promise<{prices: Array}>}
 */
export const getCoinHistory = async (coinId, days = 7) => {
  return fetchApi(`/api/crypto/history/${coinId}?days=${days}`);
};

const api = {
  fetchApi,
  getAgents,
  createAgent,
  deleteAgent,
  getTrades,
  getStats,
  getEstado,
  getTopCoins,
  getTrending,
  getCoinPrice,
  getCoinHistory,
};

export default api;