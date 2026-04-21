import { useState, useEffect } from 'react';
import { getEstado, getStats } from '../services/api.js';

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
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setError(null);
      const [estadoData, statsData] = await Promise.all([
        getEstado(),
        getStats(),
      ]);
      setEstado(estadoData);
      setStats(statsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchData();
  }, []);

  // Auto refresh every 5 seconds
  useInterval(() => {
    fetchData();
  }, 5000);

  if (loading) {
    return <div style={styles.loading}>Cargando...</div>;
  }

  if (error) {
    return (
      <div style={styles.error}>
        <h3>Error</h3>
        <p>{error}</p>
        <button onClick={fetchData} style={styles.button}>Reintentar</button>
      </div>
    );
  }

  const activos = estado?.agentes_activos || 0;
  const muertos = estado?.agentes_muertos || 0;
  const replicados = estado?.agentes_replicados || 0;
  const profit = estado?.profit_total || 0;
  const winRate = stats?.win_rate_percent || 0;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Dashboard</h1>
      
      <div style={styles.grid}>
        <Card 
          title="Agentes Activos" 
          value={activos} 
          color="#00ff88" 
        />
        <Card 
          title="Agentes Muertos" 
          value={muertos} 
          color="#ff4444" 
        />
        <Card 
          title="Agentes Replicados" 
          value={replicados} 
          color="#4488ff" 
        />
        <Card 
          title="P&L Total" 
          value={`${profit >= 0 ? '+' : ''}${profit.toFixed(2)}`}
          color={profit >= 0 ? '#00ff88' : '#ff4444'}
        />
        <Card 
          title="Win Rate" 
          value={`${winRate}%`}
          color="#ffaa00"
        />
        <Card 
          title="Total Trades" 
          value={stats?.total_trades || 0}
          color="#ffffff"
        />
      </div>

      <div style={styles.prices}>
        <h3 style={styles.subtitle}>Precios Simulados</h3>
        <div style={styles.priceGrid}>
          {estado?.precios_actuales && Object.entries(estado.precios_actuales).map(([symbol, price]) => (
            <div key={symbol} style={styles.priceItem}>
              <span style={styles.priceSymbol}>{symbol}</span>
              <span style={styles.priceValue}>${price?.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Card({ title, value, color }) {
  return (
    <div style={{ ...styles.card, borderColor: color }}>
      <div style={styles.cardTitle}>{title}</div>
      <div style={{ ...styles.cardValue, color }}>{value}</div>
    </div>
  );
}

const styles = {
  container: {
    padding: '24px',
    fontFamily: 'JetBrains Mono, monospace',
    backgroundColor: '#050505',
    minHeight: '100vh',
    color: '#ffffff',
  },
  title: {
    fontSize: '28px',
    fontWeight: '600',
    marginBottom: '24px',
    color: '#00ff88',
  },
  subtitle: {
    fontSize: '18px',
    fontWeight: '500',
    marginBottom: '16px',
    color: '#888888',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginBottom: '32px',
  },
  card: {
    backgroundColor: '#0a0a0a',
    border: '1px solid',
    borderRadius: '8px',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  cardTitle: {
    fontSize: '14px',
    color: '#888888',
    textTransform: 'uppercase',
  },
  cardValue: {
    fontSize: '32px',
    fontWeight: '700',
  },
  prices: {
    backgroundColor: '#0a0a0a',
    border: '1px solid #222',
    borderRadius: '8px',
    padding: '20px',
  },
  priceGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '16px',
  },
  priceItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px',
    backgroundColor: '#111',
    borderRadius: '4px',
  },
  priceSymbol: {
    color: '#888',
    fontWeight: '500',
  },
  priceValue: {
    color: '#00ff88',
    fontWeight: '600',
  },
  loading: {
    padding: '24px',
    fontFamily: 'JetBrains Mono, monospace',
    backgroundColor: '#050505',
    color: '#00ff88',
    minHeight: '100vh',
  },
  error: {
    padding: '24px',
    fontFamily: 'JetBrains Mono, monospace',
    backgroundColor: '#050505',
    color: '#ff4444',
    minHeight: '100vh',
  },
  button: {
    marginTop: '16px',
    padding: '10px 20px',
    backgroundColor: '#00ff88',
    color: '#000',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontFamily: 'JetBrains Mono, monospace',
    fontWeight: '600',
  },
};

export default Dashboard;
