import { useState, useEffect } from 'react';
import { getAgents, createAgent, deleteAgent } from '../services/api.js';

function Agents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    estrategia: 'S1',
    presupuesto: 1000,
    umbral: 0.15,
  });

  const fetchAgents = async () => {
    try {
      setError(null);
      const data = await getAgents();
      setAgents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createAgent(formData);
      setModalOpen(false);
      setFormData({ nombre: '', estrategia: 'S1', presupuesto: 1000, umbral: 0.15 });
      fetchAgents();
    } catch (err) {
      setError(`Error creando agente: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar este agente?')) return;
    try {
      await deleteAgent(id);
      fetchAgents();
    } catch (err) {
      setError(`Error eliminando: ${err.message}`);
    }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'ACTIVO': return '#00ff88';
      case 'MUERTO': return '#ff4444';
      case 'REPLICADO': return '#4488ff';
      default: return '#888888';
    }
  };

  const calcularProfit = (agente) => {
    return agente.presupuesto_actual - agente.presupuesto_inicial;
  };

  const calcularProfitPercent = (agente) => {
    const profit = calcularProfit(agente);
    return ((profit / agente.presupuesto_inicial) * 100).toFixed(2);
  };

  if (loading) return <div style={styles.loading}>Cargando...</div>;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Agentes</h1>
        <button onClick={() => setModalOpen(true)} style={styles.button}>
          + Nuevo Agente
        </button>
      </div>

      {error && (
        <div style={styles.error}>
          {error}
          <button onClick={() => setError(null)} style={styles.closeError}>×</button>
        </div>
      )}

      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Nombre</th>
            <th style={styles.th}>Estrategia</th>
            <th style={styles.th}>Presupuesto</th>
            <th style={styles.th}>Profit %</th>
            <th style={styles.th}>Estado</th>
            <th style={styles.th}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {agents.map((agente) => (
            <tr key={agente.id} style={styles.tr}>
              <td style={styles.td}>{agente.nombre}</td>
              <td style={styles.td}>{agente.estrategia}</td>
              <td style={styles.td}>
                ${agente.presupuesto_actual?.toFixed(2)}
                <span style={styles.initial}> / ${agente.presupuesto_inicial?.toFixed(0)}</span>
              </td>
              <td style={styles.td}>
                <span style={{ 
                  color: calcularProfit(agente) >= 0 ? '#00ff88' : '#ff4444' 
                }}>
                  {calcularProfitPercent(agente)}%
                </span>
              </td>
              <td style={styles.td}>
                <span style={{ 
                  color: getEstadoColor(agente.estado),
                  fontWeight: '600',
                }}>
                  ● {agente.estado}
                </span>
              </td>
              <td style={styles.td}>
                <button 
                  onClick={() => handleDelete(agente.id)}
                  style={styles.deleteBtn}
                  disabled={agente.estado === 'MUERTO'}
                >
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {agents.length === 0 && (
        <div style={styles.empty}>No hay agentes. Crea uno nuevo.</div>
      )}

      {modalOpen && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <h2 style={styles.modalTitle}>Nuevo Agente</h2>
            <form onSubmit={handleCreate}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Nombre</label>
                <input
                  type="text"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  required
                  style={styles.input}
                  placeholder="Agente Alpha"
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Estrategia</label>
                <select
                  value={formData.estrategia}
                  onChange={(e) => setFormData({ ...formData, estrategia: e.target.value })}
                  style={styles.input}
                >
                  <option value="S1">S1 - Momentum</option>
                  <option value="S2">S2 - Mean Reversion</option>
                  <option value="S3">S3 - Breakout</option>
                </select>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Presupuesto Inicial ($)</label>
                <input
                  type="number"
                  value={formData.presupuesto}
                  onChange={(e) => setFormData({ ...formData, presupuesto: parseFloat(e.target.value) })}
                  required
                  min="100"
                  style={styles.input}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Umbral Réplica (0.15 = 15%)</label>
                <input
                  type="number"
                  value={formData.umbral}
                  onChange={(e) => setFormData({ ...formData, umbral: parseFloat(e.target.value) })}
                  required
                  min="0.05"
                  max="1"
                  step="0.05"
                  style={styles.input}
                />
              </div>

              <div style={styles.modalButtons}>
                <button type="button" onClick={() => setModalOpen(false)} style={styles.cancelBtn}>
                  Cancelar
                </button>
                <button type="submit" style={styles.submitBtn}>
                  Crear
                </button>
              </div>
            </form>
          </div>
        </div>
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  title: {
    fontSize: '28px',
    fontWeight: '600',
    color: '#00ff88',
    margin: 0,
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#00ff88',
    color: '#000',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontFamily: 'JetBrains Mono, monospace',
    fontWeight: '600',
    fontSize: '14px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    backgroundColor: '#0a0a0a',
    border: '1px solid #222',
    borderRadius: '8px',
    overflow: 'hidden',
  },
  th: {
    padding: '16px',
    textAlign: 'left',
    backgroundColor: '#111',
    color: '#888',
    fontSize: '12px',
    textTransform: 'uppercase',
    fontWeight: '500',
    borderBottom: '1px solid #222',
  },
  tr: {
    borderBottom: '1px solid #1a1a1a',
  },
  td: {
    padding: '16px',
    fontSize: '14px',
  },
  initial: {
    color: '#666',
    fontSize: '12px',
  },
  deleteBtn: {
    padding: '6px 12px',
    backgroundColor: '#ff4444',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    opacity: '0.8',
  },
  empty: {
    textAlign: 'center',
    padding: '48px',
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
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.8)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modal: {
    backgroundColor: '#0a0a0a',
    border: '1px solid #333',
    borderRadius: '8px',
    padding: '24px',
    width: '400px',
    maxWidth: '90vw',
  },
  modalTitle: {
    margin: '0 0 24px 0',
    color: '#00ff88',
    fontSize: '20px',
  },
  formGroup: {
    marginBottom: '16px',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    color: '#888',
    fontSize: '12px',
    textTransform: 'uppercase',
  },
  input: {
    width: '100%',
    padding: '10px',
    backgroundColor: '#111',
    border: '1px solid #333',
    borderRadius: '4px',
    color: '#fff',
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  modalButtons: {
    display: 'flex',
    gap: '12px',
    marginTop: '24px',
  },
  cancelBtn: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#222',
    color: '#fff',
    border: '1px solid #333',
    borderRadius: '4px',
    cursor: 'pointer',
    fontFamily: 'JetBrains Mono, monospace',
  },
  submitBtn: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#00ff88',
    color: '#000',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontFamily: 'JetBrains Mono, monospace',
    fontWeight: '600',
  },
};

export default Agents;
