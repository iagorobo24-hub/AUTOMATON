const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = {
  // Auth endpoints
  auth: {
    login: async (username, password) => {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await fetch(`${API_BASE_URL}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      return data;
    },
    
    logout: () => {
      localStorage.removeItem('token');
    },
    
    getToken: () => localStorage.getItem('token'),
    
    register: async (userData) => {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      
      if (!response.ok) {
        throw new Error('Registration failed');
      }
      
      return response.json();
    },
  },
  
  // Agents endpoints
  agents: {
    list: async () => {
      const response = await fetch(`${API_BASE_URL}/agents`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    get: async (id) => {
      const response = await fetch(`${API_BASE_URL}/agents/${id}`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    create: async (agentData) => {
      const response = await fetch(`${API_BASE_URL}/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${api.auth.getToken()}`,
        },
        body: JSON.stringify(agentData),
      });
      return response.json();
    },
    
    update: async (id, agentData) => {
      const response = await fetch(`${API_BASE_URL}/agents/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${api.auth.getToken()}`,
        },
        body: JSON.stringify(agentData),
      });
      return response.json();
    },
    
    delete: async (id) => {
      const response = await fetch(`${API_BASE_URL}/agents/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.ok;
    },
  },
  
  // Trades endpoints
  trades: {
    list: async (params = {}) => {
      const query = new URLSearchParams(params).toString();
      const response = await fetch(`${API_BASE_URL}/trades?${query}`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    get: async (id) => {
      const response = await fetch(`${API_BASE_URL}/trades/${id}`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    close: async (id) => {
      const response = await fetch(`${API_BASE_URL}/trades/${id}/close`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
  },
  
  // Strategies endpoints
  strategies: {
    list: async () => {
      const response = await fetch(`${API_BASE_URL}/strategies`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    get: async (id) => {
      const response = await fetch(`${API_BASE_URL}/strategies/${id}`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    backtest: async (strategyId, params) => {
      const response = await fetch(`${API_BASE_URL}/strategies/${strategyId}/backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${api.auth.getToken()}`,
        },
        body: JSON.stringify(params),
      });
      return response.json();
    },
  },
  
  // Replication endpoints
  replication: {
    list: async () => {
      const response = await fetch(`${API_BASE_URL}/replication`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    get: async (id) => {
      const response = await fetch(`${API_BASE_URL}/replication/${id}`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    replicate: async (agentId) => {
      const response = await fetch(`${API_BASE_URL}/replication/replicate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${api.auth.getToken()}`,
        },
        body: JSON.stringify({ agent_id: agentId }),
      });
      return response.json();
    },
  },
  
  // Metrics endpoints
  metrics: {
    dashboard: async () => {
      const response = await fetch(`${API_BASE_URL}/metrics/dashboard`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    performance: async (agentId) => {
      const response = await fetch(`${API_BASE_URL}/metrics/performance/${agentId}`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
  },
  
  // Settings endpoints
  settings: {
    get: async () => {
      const response = await fetch(`${API_BASE_URL}/settings`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    update: async (settings) => {
      const response = await fetch(`${API_BASE_URL}/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${api.auth.getToken()}`,
        },
        body: JSON.stringify(settings),
      });
      return response.json();
    },
  },
  
  // Trading mode
  trading: {
    getMode: async () => {
      const response = await fetch(`${API_BASE_URL}/trading/mode`, {
        headers: { Authorization: `Bearer ${api.auth.getToken()}` },
      });
      return response.json();
    },
    
    setMode: async (mode) => {
      const response = await fetch(`${API_BASE_URL}/trading/mode`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${api.auth.getToken()}`,
        },
        body: JSON.stringify({ mode }),
      });
      return response.json();
    },
  },
};

export default api;