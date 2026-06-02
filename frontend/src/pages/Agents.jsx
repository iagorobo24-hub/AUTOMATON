import { useState, useEffect } from 'react';
import { getAgents, createAgent, deleteAgent } from '../services/api.js';
import { Plus, Search } from 'lucide-react';

import Layout from '../components/layout/Layout';
import AgentTable from '../components/agents/AgentTable';
import AgentDetailPanel from '../components/agents/AgentDetailPanel';
import EmptyState from '../components/shared/EmptyState';
import { Bot } from 'lucide-react';

function Agents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
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
      setError(`Error creating agent: ${err.message}`);
    }
  };

  const handleDelete = async (agent) => {
    if (!confirm(`Delete agent ${agent.nombre}?`)) return;
    try {
      await deleteAgent(agent.id);
      if (selectedAgent?.id === agent.id) {
        setDetailOpen(false);
        setSelectedAgent(null);
      }
      fetchAgents();
    } catch (err) {
      setError(`Error deleting: ${err.message}`);
    }
  };

  const handleStop = (agent) => {
    // Placeholder for stop functionality
    console.log('Stop agent:', agent.id);
  };

  const handleSelectAgent = (agent) => {
    setSelectedAgent(agent);
    setDetailOpen(true);
  };

  const filteredAgents = agents.filter(agent => 
    agent.nombre.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.estrategia.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Loading state
  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-[var(--text-muted)]">Loading agents...</div>
        </div>
      </Layout>
    );
  }

  // Error state
  if (error) {
    return (
      <Layout>
        <EmptyState 
          icon={Bot}
          title="Error loading agents"
          subtitle={error}
        />
        <button onClick={fetchAgents} className="btn-primary mt-4">
          Retry
        </button>
      </Layout>
    );
  }

  const headerActions = (
    <button onClick={() => setModalOpen(true)} className="btn-primary">
      <Plus className="h-4 w-4 mr-2" />
      New Agent
    </button>
  );

  return (
    <Layout actions={headerActions}>
      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="app-input pl-10"
          />
        </div>
      </div>

      {/* Agent Table */}
      <AgentTable
        agents={filteredAgents}
        selectedAgent={selectedAgent}
        onSelect={handleSelectAgent}
        onStop={handleStop}
        onDelete={handleDelete}
      />

      {/* Detail Panel */}
      <AgentDetailPanel
        agent={selectedAgent}
        open={detailOpen}
        onClose={() => {
          setDetailOpen(false);
          setSelectedAgent(null);
        }}
      />

      {/* Create Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg p-6 w-full max-w-md">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-6">New Agent</h2>
            <form onSubmit={handleCreate}>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs text-[var(--text-muted)] uppercase mb-2">Name</label>
                  <input
                    type="text"
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    required
                    className="app-input"
                    placeholder="Agent Alpha"
                  />
                </div>

                <div>
                  <label className="block text-xs text-[var(--text-muted)] uppercase mb-2">Strategy</label>
                  <select
                    value={formData.estrategia}
                    onChange={(e) => setFormData({ ...formData, estrategia: e.target.value })}
                    className="app-input"
                  >
                    <option value="S1">S1 - Momentum</option>
                    <option value="S2">S2 - Mean Reversion</option>
                    <option value="S3">S3 - Breakout</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-[var(--text-muted)] uppercase mb-2">Initial Budget ($)</label>
                  <input
                    type="number"
                    value={formData.presupuesto}
                    onChange={(e) => setFormData({ ...formData, presupuesto: parseFloat(e.target.value) })}
                    required
                    min="100"
                    className="app-input"
                  />
                </div>

                <div>
                  <label className="block text-xs text-[var(--text-muted)] uppercase mb-2">Replication Threshold (0.15 = 15%)</label>
                  <input
                    type="number"
                    value={formData.umbral}
                    onChange={(e) => setFormData({ ...formData, umbral: parseFloat(e.target.value) })}
                    required
                    min="0.05"
                    max="1"
                    step="0.05"
                    className="app-input"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setModalOpen(false)} className="btn-ghost flex-1">
                  Cancel
                </button>
                <button type="submit" className="btn-primary flex-1">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
}

export default Agents;
