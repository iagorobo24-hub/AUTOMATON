import { useState, useEffect } from 'react';
import { getTrades } from '../services/api.js';

function Trades() {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTrades = async () => {
    try {
      setError(null);
      const data = await getTrades();
      // Tomar últimos 50
      setTrades(data.slice(0, 50));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
    const interval = setInterval(fetchTrades, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  if (loading) return <div style={styles.loading}>Cargando...</div>;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Trades</h1>

      {error && (
        <div style={styles.error}>
          {error}
          <button onClick={() => setError(null)} style={styles.closeError}>×</button>
        </div>
      )}

      <div style={styles.list}>
        {trades.map((trade) => {
          const isWin = trade.resultado > 0;
          const isLoss = trade.resultado < 0;
          const resultado = trade.resultado !== null && trade.resultado !== undefined
            ? `${trade.resultado >= 0 ? '+' : ''}${trade.resultado.toFixed(2)}`
            : 'Abierto';

          return (
            <div key={trade.id} style={styles.item}>
              <div style={styles.row}>
                <span style={styles.agente}>Agente #{trade.agente_id}</span>
                <span style={styles.tipo}>{trade.tipo}</span>
              </div>
              <div style={styles.row}>
                <span style={styles.precio}>
                  Entrada: ${trade.precio_entrada?.toFixed(2)}
                  {trade.precio_salida && ` → ${trade.precio_salida.toFixed(2)}`}
                </span>
                <span style={{
                  ...styles.resultado,
                  color: isWin ? '#00ff88' : isLoss ? '#ff4444' : '#888',
                }}>
                  {resultado}
                </span>
              </div>
              <div style={styles.timestamp}>
                {formatTimestamp(trade.timestamp)}
              </div>
            </div>
          );
        })}
      </div>

      {trades.length === 0 && (
        <div style={styles.empty}>No hay trades registrados.</div>
      )}
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
    color: '#00ff88',
    marginBottom: '24px',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  item: {
    backgroundColor: '#0a0a0a',
    border: '1px solid #222',
    borderRadius: '6px',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  agente: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#ffffff',
  },
  tipo: {
    fontSize: '12px',
    color: '#888',
    backgroundColor: '#222',
    padding: '4px 8px',
    borderRadius: '4px',
  },
  precio: {
    fontSize: '13px',
    color: '#aaa',
  },
  resultado: {
    fontSize: '16px',
    fontWeight: '700',
  },
  timestamp: {
    fontSize: '11px',
    color: '#666',
  },
  loading: {
    padding: '24px',
    fontFamily: 'JetBrains Mono, monospace',
    backgroundColor: '#050505',
    color: '#00ff88',
    minHeight: '100vh',
  },
  error: {
    backgroundColor: '#ff444422',
    color: '#ff4444',
    padding: '12px 16px',
    borderRadius: '6px',
    marginBottom: '16px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  closeError: {
    background: 'none',
    border: 'none',
    color: '#ff4444',
    fontSize: '20px',
    cursor: 'pointer',
  },
  empty: {
    textAlign: 'center',
    padding: '48px',
    color: '#666',
  },
};

export default Trades;
