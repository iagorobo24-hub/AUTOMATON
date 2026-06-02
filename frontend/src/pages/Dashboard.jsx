import { useState, useEffect } from 'react';
import { getEstado, getStats, getAgents, getTopCoins } from '../services/api.js';
import { Bot, Database, CheckCircle2, Activity, TrendingUp } from 'lucide-react';

import Layout from '../components/layout/Layout';
import StatCard from '../components/dashboard/StatCard';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import AgentOverview from '../components/dashboard/AgentOverview';
import EmptyState from '../components/shared/EmptyState';

import { mockActivityFeed, mockAgents } from '../lib/mockData.js';

console.log('[DASHBOARD] Module loaded')

// Custom hook for interval
function useInterval(callback, delay) {
  useEffect(() => {
    if (delay === null) return;
    const id = setInterval(callback, delay);
    return () => clearInterval(id);
  }, [callback, delay]);
}

function Dashboard() {
  const [estado, setEstado] = useState(null);
  const [stats, setStats] = useState(null);
  const [agents, setAgents] = useState([]);
  const [cryptoData, setCryptoData] = useState(null);
  const [cryptoError, setCryptoError] = useState(null);
  const [cryptoLoading, setCryptoLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setError(null);
      const [estadoData, statsData, agentsData] = await Promise.all([
        getEstado(),
        getStats(),
        getAgents().catch(() => []),
      ]);
      setEstado(estadoData);
      setStats(statsData);
      setAgents(agentsData || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCryptoData = async () => {
    try {
      setCryptoError(null);
      const data = await getTopCoins(5);
      setCryptoData(data);
    } catch (err) {
      console.error('[Dashboard] Crypto fetch error:', err);
      setCryptoError(err.message);
    } finally {
      setCryptoLoading(false);
    }
  };


  useEffect(() => {
    fetchData();
    fetchCryptoData();
  }, []);

  // Auto-refresh crypto data every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchCryptoData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Auto refresh every 5 seconds
  useInterval(() => {
    fetchData();
  }, 5000);

  // Calculate derived stats
  const totalAgents = agents.length;
  const activeAgents = agents.filter(a => a.estado === 'ACTIVO').length;
  const tasksCompleted = agents.reduce((sum, a) => sum + (a.tasks_completed || 0), 0);
  const uptime = `${Math.floor((stats?.uptime_hours || 0) / 24)}d ${(stats?.uptime_hours || 0) % 24}h`;
  const memoryUsage = Math.round(
    agents.reduce((sum, a) => sum + (a.memory_usage || 0), 0) / (agents.length || 1)
  );

  // Loading state within layout
  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-[var(--text-muted)]">Loading...</div>
        </div>
      </Layout>
    );
  }

  // Error state within layout
  if (error) {
    return (
      <Layout>
        <EmptyState 
          icon={Activity}
          title="Error loading dashboard"
          subtitle={error}
        />
        <button onClick={fetchData} className="btn-primary mt-4">
          Retry
        </button>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard 
          title="Total Agents" 
          value={totalAgents} 
          subtitle={`${activeAgents} active`}
          icon={Bot}
        />
        <StatCard 
          title="Memory Usage" 
          value={`${memoryUsage}%`}
          subtitle={`${agents.reduce((sum, a) => sum + (a.memory_usage || 0), 0)}MB total`}
          icon={Database}
        />
        <StatCard 
          title="Tasks Completed" 
          value={tasksCompleted.toLocaleString()}
          subtitle={`${stats?.win_rate_percent || 0}% win rate`}
          icon={CheckCircle2}
        />
        <StatCard 
          title="Uptime" 
          value={uptime}
          subtitle="System online"
          icon={Activity}
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityFeed items={mockActivityFeed.slice(0, 8)} />
        <AgentOverview agents={agents.length > 0 ? agents : mockAgents} />
      </div>

      {/* Crypto Market Section */}
      {cryptoData?.coins && cryptoData.coins.length > 0 && (
        <div className="app-card mt-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[var(--accent)]" />
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">Crypto Market</h3>
            </div>
            <button 
              onClick={fetchCryptoData}
              className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              disabled={cryptoLoading}
            >
              {cryptoLoading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {cryptoData.coins.map((coin) => {
              const isPositive = (coin.price_change_24h || 0) >= 0;
              return (
                <div key={coin.id} className="p-3 rounded-lg bg-[var(--bg-elevated)]">
                  <div className="flex items-center gap-2 mb-2">
                    {coin.image && (
                      <img src={coin.image} alt={coin.symbol} className="w-5 h-5 rounded-full" />
                    )}
                    <span className="text-xs font-medium text-[var(--text-secondary)]">{coin.symbol}</span>
                  </div>
                  <p className="text-sm font-mono font-bold text-[var(--accent)]">
                    ${coin.current_price >= 1 ? coin.current_price.toLocaleString() : coin.current_price.toFixed(4)}
                  </p>
                  <p className={`text-xs ${isPositive ? 'text-blue-500' : 'text-red-500'}`}>
                    {isPositive ? '+' : ''}{coin.price_change_24h?.toFixed(2)}%
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error State for Crypto */}
      {cryptoError && (
        <div className="app-card mt-6 border border-yellow-500/30">
          <div className="flex items-center gap-2 text-yellow-500">
            <TrendingUp className="w-4 h-4" />
            <p className="text-sm">Crypto data temporarily unavailable</p>
          </div>
        </div>
      )}

      {/* Prices Section */}
      {estado?.precios_actuales && (
        <div className="app-card mt-6">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Market Prices</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {Object.entries(estado.precios_actuales).map(([symbol, price]) => (
              <div key={symbol} className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-elevated)]">
                <span className="text-xs font-medium text-[var(--text-secondary)]">{symbol}</span>
                <span className="text-sm font-mono text-[var(--accent)]">${price?.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
}

export default Dashboard;
