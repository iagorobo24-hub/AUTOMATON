import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Bot, Plus, Copy, Trash2, Activity,
  MoreVertical, RefreshCw, Search, X, ChevronDown,
} from "lucide-react";
import { toast } from "sonner";
import { agentsAPI } from "@/lib/api";
import { normalizeAgents } from "@/lib/agentContract";

const CYAN = "#00F3FF";
const GRAY = "#6B7280";

const statusConfig = {
  active: { badge: "evo-badge-success", dot: "bg-blue-500", label: "Activo" },
  replicated: { badge: "evo-badge-cyan", dot: "bg-cyan-400", label: "Replicado" },
  dead: { badge: "evo-badge bg-white/5 text-muted-foreground ring-white/10", dot: "bg-gray-500", label: "Muerto" },
  unknown: { badge: "evo-badge-warning", dot: "bg-amber-400", label: "Desconocido" },
};

function HealthBar({ value }) {
  const pct = Math.max(0, Math.min(100, value));
  const color = pct > 60 ? "bg-blue-500" : pct > 30 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
      <div className={`h-full rounded-full transition-all duration-500 ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

function AgentCard({ agent, onReplicate, onDestroy, onDeposit }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const finances = agent.finances || {};
  const performance = agent.performance || {};
  const tradingStats = agent.trading_stats || {};
  const lineage = agent.lineage || {};
  const balance = finances.current_balance ?? 0;
  const initialBalance = finances.initial_capital ?? 0;
  const childrenCount = lineage.children_ids?.length ?? 0;
  const sc = statusConfig[agent.status] || statusConfig.unknown;
  const healthPercent = initialBalance > 0 ? Math.max(0, Math.min(100, (balance / initialBalance) * 100)) : 0;
  const isActive = agent.status === "active";
  const isDead = agent.status === "dead";
  const roiLabel = performance.evidence_valid && performance.roi_percent != null
    ? `${performance.roi_percent >= 0 ? "+" : ""}${performance.roi_percent.toFixed(1)}%`
    : "N/D";

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="relative glass-card rounded-xl p-5 transition-all duration-200 hover:border-cyan-500/20">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center"><Bot className="w-5 h-5 text-cyan-400" /></div>
          <div>
            <h3 className="font-semibold text-sm text-foreground">{agent.name}</h3>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">{agent.strategy}</p>
          </div>
        </div>
        <div className="relative">
          <button onClick={() => setMenuOpen(!menuOpen)} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/10 transition-colors" aria-label="Opciones del agente"><MoreVertical className="w-4 h-4 text-muted-foreground" /></button>
          {menuOpen && (
            <div className="absolute right-0 top-10 z-30 w-52 glass-card rounded-lg overflow-hidden shadow-xl shadow-black/40">
              <button disabled={!isActive} onClick={() => { onDeposit(agent.id); setMenuOpen(false); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-white/5 disabled:opacity-40 disabled:cursor-not-allowed text-foreground"><Activity className="w-4 h-4 text-blue-400" /> Fondear +€100</button>
              <div className="h-px bg-white/5 mx-2" />
              <button disabled={!isActive} onClick={() => { onReplicate(agent.id); setMenuOpen(false); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-white/5 disabled:opacity-40 disabled:cursor-not-allowed text-foreground"><Copy className="w-4 h-4 text-cyan-400" /> Replicar manualmente</button>
              <button disabled={isDead} onClick={() => { onDestroy(agent.id); setMenuOpen(false); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-white/5 disabled:opacity-40 disabled:cursor-not-allowed text-red-400"><Trash2 className="w-4 h-4" /> Eliminar</button>
            </div>
          )}
        </div>
      </div>
      {menuOpen && <div className="fixed inset-0 z-20" onClick={() => setMenuOpen(false)} />}
      <div className={`mb-4 ${sc.badge}`}><span className="inline-flex items-center gap-1.5"><span className={`w-1.5 h-1.5 rounded-full ${sc.dot}`} />{sc.label}</span></div>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div><p className="text-[11px] text-muted-foreground uppercase tracking-wide mb-0.5">Saldo</p><p className="font-bold text-lg text-foreground font-mono">€{balance.toFixed(2)}</p></div>
        <div><p className="text-[11px] text-muted-foreground uppercase tracking-wide mb-0.5">ROI verificable</p><p className="font-bold text-lg font-mono text-muted-foreground">{roiLabel}</p></div>
      </div>
      <div className="mb-4"><div className="flex justify-between text-[11px] text-muted-foreground mb-1.5"><span className="uppercase tracking-wide">Capital disponible/fondeado</span><span>{healthPercent.toFixed(0)}%</span></div><HealthBar value={healthPercent} /></div>
      <div className="grid grid-cols-3 gap-3 pt-4 border-t border-white/5">
        {[
          { label: "Trades válidos", value: tradingStats.total_trades ?? "N/D" },
          { label: "Ganados", value: tradingStats.winning_trades ?? "N/D" },
          { label: "Clones", value: childrenCount },
        ].map((s) => <div key={s.label} className="text-center"><p className="text-[10px] text-muted-foreground uppercase tracking-wide">{s.label}</p><p className="text-sm font-semibold text-foreground">{s.value}</p></div>)}
      </div>
      {tradingStats.legacy_records > 0 && <p className="mt-3 text-[10px] text-muted-foreground">{tradingStats.legacy_records} registros históricos sin procedencia verificable excluidos de métricas.</p>}
    </motion.div>
  );
}

function CreateDialog({ open, onClose, onCreate }) {
  const [name, setName] = useState("");
  const [strategy, setStrategy] = useState("S1");
  const [balance, setBalance] = useState(1000);
  const [strategyOpen, setStrategyOpen] = useState(false);
  const strategies = [
    { value: "S1", label: "S1 · Momentum" },
    { value: "S2", label: "S2 · Mean Reversion" },
    { value: "S3", label: "S3 · Breakout" },
    { value: "S4", label: "S4 · Hybrid" },
  ];

  const handleSubmit = () => {
    if (!name.trim()) { toast.error("El nombre es obligatorio"); return; }
    if (!(balance > 0)) { toast.error("El saldo inicial debe ser positivo"); return; }
    onCreate({ nombre: name.trim(), estrategia: strategy, presupuesto: balance, umbral: 0.15 });
    setName(""); setStrategy("S1"); setBalance(1000); onClose();
  };

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose} role="dialog" aria-modal="true" aria-label="Crear nuevo agente">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <motion.div initial={{ opacity: 0, scale: 0.95, y: 10 }} animate={{ opacity: 1, scale: 1, y: 0 }} className="relative glass-card rounded-xl w-full max-w-md mx-4 p-7" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-6"><h2 className="font-heading text-lg font-bold uppercase tracking-wide text-foreground">Nuevo Agente</h2><button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/10 transition-colors" aria-label="Cerrar"><X className="w-4 h-4 text-muted-foreground" /></button></div>
        <div className="space-y-5">
          <div><label className="evo-section-title mb-1.5 block">Nombre</label><input value={name} onChange={(e) => setName(e.target.value)} placeholder="ADAN-002" className="evo-input" data-testid="agent-name-input" aria-label="Nombre del agente" /></div>
          <div className="relative"><label className="evo-section-title mb-1.5 block">Estrategia</label><button onClick={() => setStrategyOpen(!strategyOpen)} className="evo-input w-full flex items-center justify-between text-left" aria-expanded={strategyOpen} aria-haspopup="listbox"><span>{strategies.find((item) => item.value === strategy)?.label}</span><ChevronDown className="w-4 h-4 text-muted-foreground" /></button>{strategyOpen && <div className="absolute z-20 w-full mt-1 glass-card rounded-lg overflow-hidden shadow-xl shadow-black/40" role="listbox">{strategies.map((item) => <button key={item.value} onClick={() => { setStrategy(item.value); setStrategyOpen(false); }} className={`w-full text-left px-4 py-2.5 text-sm transition-colors hover:bg-white/5 ${item.value === strategy ? "text-cyan-400 font-medium" : "text-muted-foreground"}`}>{item.label}</button>)}</div>}</div>
          <div><label className="evo-section-title mb-1.5 block">Saldo inicial (€)</label><input type="number" min="10" step="10" value={balance} onChange={(e) => setBalance(parseFloat(e.target.value) || 0)} className="evo-input" aria-label="Saldo inicial" /></div>
        </div>
        <div className="flex gap-2.5 mt-7"><button onClick={onClose} className="evo-button-outline flex-1 py-2.5 text-sm">Cancelar</button><button onClick={handleSubmit} className="evo-button-primary flex-1 py-2.5 text-sm">Desplegar</button></div>
      </motion.div>
    </div>
  );
}

export default function AgentsPage() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [refreshing, setRefreshing] = useState(false);

  const fetchAgents = useCallback(async () => {
    try {
      const res = await agentsAPI.list();
      setAgents(normalizeAgents(Array.isArray(res.data) ? res.data : []));
    } catch (err) {
      toast.error(err?.message || "Error al cargar agentes");
    } finally {
      setLoading(false); setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  const handleCreate = async (data) => { try { await agentsAPI.create(data); toast.success("Agente desplegado"); fetchAgents(); } catch (err) { toast.error(err?.message || "Error al crear agente"); } };
  const handleReplicate = async (id) => { try { await agentsAPI.replicate(id); toast.success("Agente replicado manualmente"); fetchAgents(); } catch (err) { toast.error(err?.message || "Error al replicar"); } };
  const handleDestroy = async (id) => { try { await agentsAPI.delete(id); toast.success("Agente eliminado"); fetchAgents(); } catch (err) { toast.error(err?.message || "Error al eliminar"); } };
  const handleDeposit = async (id) => { try { await agentsAPI.deposit(id, 100); toast.success("Capital añadido: +€100"); fetchAgents(); } catch (err) { toast.error(err?.message || "Error al fondear"); } };

  const counts = {
    active: agents.filter((a) => a.status === "active").length,
    replicated: agents.filter((a) => a.status === "replicated").length,
    dead: agents.filter((a) => a.status === "dead").length,
  };
  const filtered = agents.filter((a) => {
    const query = search.toLowerCase();
    const matchSearch = a.name.toLowerCase().includes(query) || (a.strategy || "").toLowerCase().includes(query);
    return matchSearch && (statusFilter === "all" || a.status === statusFilter);
  });
  const statusFilters = [
    { key: "all", label: "Todos", color: CYAN },
    { key: "active", label: "Activos", color: CYAN },
    { key: "replicated", label: "Replicados", color: CYAN },
    { key: "dead", label: "Muertos", color: GRAY },
  ];

  return (
    <div className="min-h-screen bg-background" data-testid="agents-page"><div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8"><div><h1 className="font-heading text-3xl font-bold uppercase tracking-wide text-foreground">Agentes</h1><p className="text-sm text-muted-foreground mt-1">Gestión de agentes · rendimiento financiero pendiente de Paper verificable</p></div><div className="flex items-center gap-2"><button onClick={() => { setRefreshing(true); fetchAgents(); }} className="evo-button-outline px-4 py-2.5 text-sm" aria-label="Actualizar agentes"><RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} /><span className="ml-1.5 hidden sm:inline">Actualizar</span></button><button onClick={() => setCreateOpen(true)} className="evo-button-primary px-5 py-2.5 text-sm"><Plus className="w-4 h-4" /><span className="ml-1.5">Nuevo Agente</span></button></div></div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">{Object.entries(counts).map(([key, count]) => { const sc = statusConfig[key]; return <div key={key} className="glass-card rounded-xl px-5 py-4"><div className="flex items-center gap-2 mb-1"><span className={`w-2 h-2 rounded-full ${sc?.dot || "bg-gray-500"}`} /><span className="text-xs text-muted-foreground uppercase tracking-wide">{sc?.label || key}</span></div><p className="text-2xl font-bold text-foreground font-mono">{count}</p></div>; })}</div>
      <div className="flex flex-col sm:flex-row gap-3 mb-6"><div className="relative flex-1"><Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" aria-hidden="true" /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar agentes…" className="evo-input pl-10" aria-label="Buscar agentes" data-testid="agents-search-input" /></div><div className="flex gap-1.5 flex-wrap">{statusFilters.map((s) => <button key={s.key} onClick={() => setStatusFilter(s.key)} className={`px-4 py-2 rounded-lg text-xs font-medium uppercase tracking-wide transition-all ${statusFilter === s.key ? "bg-cyan-500/15 text-cyan-400 ring-1 ring-cyan-500/20" : "glass-card text-muted-foreground hover:text-foreground hover:bg-white/[0.06]"}`}>{s.label}</button>)}</div></div>
      {loading ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">{[...Array(3)].map((_, i) => <div key={i} className="glass-card rounded-xl h-72 animate-pulse" />)}</div> : filtered.length > 0 ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">{filtered.map((agent) => <AgentCard key={agent.id} agent={agent} onReplicate={handleReplicate} onDestroy={handleDestroy} onDeposit={handleDeposit} />)}</div> : <div className="glass-card rounded-xl py-20 text-center"><div className="w-14 h-14 mx-auto mb-4 rounded-lg bg-cyan-500/10 flex items-center justify-center"><Activity className="w-6 h-6 text-cyan-400 opacity-50" /></div><h3 className="text-lg font-semibold text-foreground mb-1">{search || statusFilter !== "all" ? "Sin resultados" : "No hay agentes desplegados"}</h3><p className="text-sm text-muted-foreground mb-6">{search || statusFilter !== "all" ? "Prueba a ajustar la búsqueda o los filtros" : "Crea un agente para preparar futuros experimentos Paper"}</p>{!search && statusFilter === "all" && <button onClick={() => setCreateOpen(true)} className="evo-button-primary px-5 py-2.5 text-sm"><Plus className="w-4 h-4" /> Desplegar Agente</button>}</div>}
    </div><CreateDialog open={createOpen} onClose={() => setCreateOpen(false)} onCreate={handleCreate} /></div>
  );
}
