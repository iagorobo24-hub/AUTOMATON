import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Bot, Plus, Copy, Trash2, Activity, TrendingUp, TrendingDown,
  MoreVertical, RefreshCw, Search, X, ChevronDown,
} from "lucide-react";
import { toast } from "sonner";
import { agentsAPI } from "@/lib/api";
import { useAppMode } from "@/hooks/useAppMode";

const GREEN = "#00FF88";
const RED = "#FF003C";
const YELLOW = "#FFD600";
const CYAN = "#00F3FF";
const PURPLE = "#7000FF";
const GRAY = "#6B7280";

const statusConfig = {
  active: { badge: "evo-badge-success", dot: "bg-green-500", label: "Activo" },
  replicating: { badge: "evo-badge-cyan", dot: "bg-cyan-400", label: "Replicando" },
  dying: { badge: "evo-badge-danger", dot: "bg-red-500", label: "En riesgo" },
  dead: { badge: "evo-badge bg-white/5 text-muted-foreground ring-white/10", dot: "bg-gray-500", label: "Muerto" },
  paused: { badge: "evo-badge-warning", dot: "bg-amber-400", label: "Pausado" },
  hibernating: { badge: "evo-badge-info", dot: "bg-blue-400", label: "Hibernando" },
};

/* ─── Health Bar ─── */
function HealthBar({ value }) {
  const pct = Math.max(0, Math.min(100, value));
  const color = pct > 60 ? "bg-green-500" : pct > 30 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
      <div className={`h-full rounded-full transition-all duration-500 ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

/* ─── Agent Card ─── */
function AgentCard({ agent, onReplicate, onDestroy, onSimulate, onDeposit }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const finances = agent.finances || {};
  const performance = agent.performance || {};
  const tradingStats = agent.trading_stats || {};
  const lineage = agent.lineage || {};

  const balance = finances.current_balance ?? agent.balance ?? 0;
  const initialBalance = finances.initial_capital ?? agent.initial_balance ?? 100;
  const roi = performance.roi_percent ?? agent.roi ?? 0;
  const tradesCount = tradingStats.total_trades ?? agent.trades_count ?? 0;
  const successfulTrades = tradingStats.winning_trades ?? agent.successful_trades ?? 0;
  const childrenCount = lineage.children_ids?.length ?? 0;
  const generation = agent.generation ?? 1;

  const sc = statusConfig[agent.status] || statusConfig.active;
  const healthPercent = Math.max(0, Math.min(100, (balance / initialBalance) * 100));

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="relative glass-card rounded-xl p-5 transition-all duration-200 hover:border-cyan-500/20"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
            <Bot className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-foreground">{agent.name}</h3>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">{agent.agent_type || agent.type}</p>
          </div>
        </div>
        <div className="relative">
          <button onClick={() => setMenuOpen(!menuOpen)} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/10 transition-colors" aria-label="Opciones del agente">
            <MoreVertical className="w-4 h-4 text-muted-foreground" />
          </button>
          {menuOpen && (
            <div className="absolute right-0 top-10 z-30 w-52 glass-card rounded-lg overflow-hidden shadow-xl shadow-black/40">
              <button onClick={() => { onDeposit(agent.id); setMenuOpen(false); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-white/5 text-foreground">
                <Activity className="w-4 h-4 text-blue-400" /> Fondear +€100
              </button>
              <div className="h-px bg-white/5 mx-2" />
              <button onClick={() => { onSimulate(agent.id, 10); setMenuOpen(false); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-white/5 text-foreground">
                <TrendingUp className="w-4 h-4 text-green-400" /> Simular +€10
              </button>
              <button onClick={() => { onSimulate(agent.id, -10); setMenuOpen(false); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-white/5 text-foreground">
                <TrendingDown className="w-4 h-4 text-red-400" /> Simular −€10
              </button>
              <div className="h-px bg-white/5 mx-2" />
              <button onClick={() => { onReplicate(agent.id); setMenuOpen(false); }} disabled={balance < 50 || agent.status === "dead"} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-white/5 disabled:opacity-40 disabled:cursor-not-allowed text-foreground">
                <Copy className="w-4 h-4 text-cyan-400" /> Replicar
              </button>
              <button onClick={() => { onDestroy(agent.id); setMenuOpen(false); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-white/5 text-red-400">
                <Trash2 className="w-4 h-4" /> Eliminar
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Close menu on outside click */}
      {menuOpen && <div className="fixed inset-0 z-20" onClick={() => setMenuOpen(false)} />}

      {/* Status */}
      <div className={`mb-4 ${sc.badge}`}>
        <span className="inline-flex items-center gap-1.5">
          <span className={`w-1.5 h-1.5 rounded-full ${sc.dot}`} />
          {sc.label}
        </span>
      </div>

      {/* Balance + ROI */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-[11px] text-muted-foreground uppercase tracking-wide mb-0.5">Saldo</p>
          <p className="font-bold text-lg text-foreground font-mono">€{balance.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-[11px] text-muted-foreground uppercase tracking-wide mb-0.5">ROI</p>
          <p className="font-bold text-lg font-mono" style={{ color: roi >= 0 ? GREEN : RED }}>
            {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Health bar */}
      <div className="mb-4">
        <div className="flex justify-between text-[11px] text-muted-foreground mb-1.5">
          <span className="uppercase tracking-wide">Salud</span>
          <span>{healthPercent.toFixed(0)}%</span>
        </div>
        <HealthBar value={healthPercent} />
      </div>

      {/* Footer stats */}
      <div className="grid grid-cols-4 gap-3 pt-4 border-t border-white/5">
        {[
          { label: "Gen", value: generation },
          { label: "Trades", value: tradesCount },
          { label: "Ganados", value: successfulTrades, cls: "text-green-400" },
          { label: "Clones", value: childrenCount },
        ].map((s) => (
          <div key={s.label} className="text-center">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{s.label}</p>
            <p className={`text-sm font-semibold ${s.cls || "text-foreground"}`}>{s.value}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

/* ─── Create Dialog ─── */
function CreateDialog({ open, onClose, onCreate }) {
  const [name, setName] = useState("");
  const [type, setType] = useState("crypto_trader");
  const [balance, setBalance] = useState(1000);
  const [typeOpen, setTypeOpen] = useState(false);

  const handleSubmit = () => {
    if (!name.trim()) { toast.error("El nombre es obligatorio"); return; }
    onCreate({ name: name.trim(), agent_type: type, initial_capital: balance });
    setName(""); setType("crypto_trader"); setBalance(1000);
    onClose();
  };

  if (!open) return null;

  const types = [
    { value: "crypto_trader", label: "Crypto Trader" },
    { value: "business_scout", label: "Business Scout" },
    { value: "market_analyzer", label: "Market Analyzer" },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose} role="dialog" aria-modal="true" aria-label="Crear nuevo agente">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="relative glass-card rounded-xl w-full max-w-md mx-4 p-7"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-heading text-lg font-bold uppercase tracking-wide text-foreground">Nuevo Agente</h2>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/10 transition-colors" aria-label="Cerrar">
            <X className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>

        <div className="space-y-5">
          <div>
            <label className="evo-section-title mb-1.5 block">Nombre</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="ADAN-002" className="evo-input" data-testid="agent-name-input" aria-label="Nombre del agente" />
          </div>
          <div className="relative">
            <label className="evo-section-title mb-1.5 block">Tipo</label>
            <button onClick={() => setTypeOpen(!typeOpen)} className="evo-input w-full flex items-center justify-between text-left" aria-expanded={typeOpen} aria-haspopup="listbox">
              <span>{types.find((t) => t.value === type)?.label}</span>
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            </button>
            {typeOpen && (
              <div className="absolute z-20 w-full mt-1 glass-card rounded-lg overflow-hidden shadow-xl shadow-black/40" role="listbox">
                {types.map((t) => (
                  <button key={t.value} onClick={() => { setType(t.value); setTypeOpen(false); }} className={`w-full text-left px-4 py-2.5 text-sm transition-colors hover:bg-white/5 ${t.value === type ? "text-cyan-400 font-medium" : "text-muted-foreground"}`}>
                    {t.label}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div>
            <label className="evo-section-title mb-1.5 block">Saldo inicial (€)</label>
            <input type="number" min="10" step="10" value={balance} onChange={(e) => setBalance(parseFloat(e.target.value) || 0)} className="evo-input" aria-label="Saldo inicial" />
          </div>
        </div>

        <div className="flex gap-2.5 mt-7">
          <button onClick={onClose} className="evo-button-outline flex-1 py-2.5 text-sm">Cancelar</button>
          <button onClick={handleSubmit} className="evo-button-primary flex-1 py-2.5 text-sm">Desplegar</button>
        </div>
      </motion.div>
    </div>
  );
}

/* ─── Main Page ─── */
export default function AgentsPage() {
  const { isSimulation } = useAppMode();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [refreshing, setRefreshing] = useState(false);

  const fetchAgents = useCallback(async () => {
    try {
      const res = await agentsAPI.list({ simulation: isSimulation });
      setAgents(res.data.agents || []);
    } catch { toast.error("Error al cargar agentes"); }
    finally { setLoading(false); setRefreshing(false); }
  }, [isSimulation]);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  const handleCreate = async (data) => {
    try {
      await agentsAPI.create({ ...data, metadata: { simulation: isSimulation } });
      toast.success("Agente desplegado");
      fetchAgents();
    } catch { toast.error("Error al crear agente"); }
  };

  const handleReplicate = async (id) => {
    try { await agentsAPI.replicate(id, {}); toast.success("Agente replicado"); fetchAgents(); }
    catch (err) { toast.error(err?.message || "Error al replicar"); }
  };

  const handleDestroy = async (id) => {
    try { await agentsAPI.delete(id); toast.success("Agente eliminado"); fetchAgents(); }
    catch { toast.error("Error al eliminar"); }
  };

  const handleSimulate = async (id, profit) => {
    try { await agentsAPI.simulateTrade(id, profit); toast.success(`Trade simulado: ${profit >= 0 ? "+" : ""}€${profit}`); fetchAgents(); }
    catch { toast.error("Error al simular trade"); }
  };

  const handleDeposit = async (id) => {
    try { await agentsAPI.deposit(id, 100); toast.success("Fondeado: +€100"); fetchAgents(); }
    catch { toast.error("Error al fondear"); }
  };

  const counts = {
    active: agents.filter(a => a.status === "active").length,
    replicating: agents.filter(a => a.status === "replicating").length,
    dying: agents.filter(a => a.status === "dying").length,
    dead: agents.filter(a => a.status === "dead").length,
  };

  const filtered = agents.filter(a => {
    const matchSearch = a.name.toLowerCase().includes(search.toLowerCase()) || (a.agent_type || a.type || "").toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "all" || a.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const statusFilters = [
    { key: "all", label: "Todos", color: CYAN },
    { key: "active", label: "Activos", color: GREEN },
    { key: "replicating", label: "Replicando", color: CYAN },
    { key: "dying", label: "En riesgo", color: RED },
    { key: "dead", label: "Muertos", color: GRAY },
  ];

  return (
    <div className="min-h-screen bg-background" data-testid="agents-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="font-heading text-3xl font-bold uppercase tracking-wide text-foreground">Agentes</h1>
            <p className="text-sm text-muted-foreground mt-1">Despliega, replica y gestiona agentes autónomos</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => { setRefreshing(true); fetchAgents(); }} className="evo-button-outline px-4 py-2.5 text-sm" aria-label="Actualizar agentes">
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
              <span className="ml-1.5 hidden sm:inline">Actualizar</span>
            </button>
            <button onClick={() => setCreateOpen(true)} className="evo-button-primary px-5 py-2.5 text-sm">
              <Plus className="w-4 h-4" />
              <span className="ml-1.5">Nuevo Agente</span>
            </button>
          </div>
        </div>

        {/* Status counts */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {Object.entries(counts).map(([key, count]) => {
            const sc = statusConfig[key];
            return (
              <div key={key} className="glass-card rounded-xl px-5 py-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`w-2 h-2 rounded-full ${sc?.dot || "bg-gray-500"}`} />
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">{sc?.label || key}</span>
                </div>
                <p className="text-2xl font-bold text-foreground font-mono">{count}</p>
              </div>
            );
          })}
        </div>

        {/* Search + filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" aria-hidden="true" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar agentes…" className="evo-input pl-10" aria-label="Buscar agentes" data-testid="agents-search-input" />
          </div>
          <div className="flex gap-1.5 flex-wrap">
            {statusFilters.map((s) => {
              const isActive = statusFilter === s.key;
              return (
                <button key={s.key} onClick={() => setStatusFilter(s.key)}
                  className={`px-4 py-2 rounded-lg text-xs font-medium uppercase tracking-wide transition-all ${
                    isActive ? "bg-cyan-500/15 text-cyan-400 ring-1 ring-cyan-500/20" : "glass-card text-muted-foreground hover:text-foreground hover:bg-white/[0.06]"
                  }`}>
                  {s.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="glass-card rounded-xl h-72 animate-pulse" />
            ))}
          </div>
        ) : filtered.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((agent) => (
              <AgentCard key={agent.id} agent={agent} onReplicate={handleReplicate} onDestroy={handleDestroy} onSimulate={handleSimulate} onDeposit={handleDeposit} />
            ))}
          </div>
        ) : (
          <div className="glass-card rounded-xl py-20 text-center">
            <div className="w-14 h-14 mx-auto mb-4 rounded-lg bg-cyan-500/10 flex items-center justify-center">
              <Activity className="w-6 h-6 text-cyan-400 opacity-50" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-1">
              {search || statusFilter !== "all" ? "Sin resultados" : "No hay agentes desplegados"}
            </h3>
            <p className="text-sm text-muted-foreground mb-6">
              {search || statusFilter !== "all" ? "Prueba a ajustar la búsqueda o los filtros" : "Despliega tu primer agente autónomo"}
            </p>
            {!search && statusFilter === "all" && (
              <button onClick={() => setCreateOpen(true)} className="evo-button-primary px-5 py-2.5 text-sm">
                <Plus className="w-4 h-4" /> Desplegar Agente
              </button>
            )}
          </div>
        )}
      </div>

      <CreateDialog open={createOpen} onClose={() => setCreateOpen(false)} onCreate={handleCreate} />
    </div>
  );
}
