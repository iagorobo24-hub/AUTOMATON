import { useState, useEffect } from "react";
import {
  Bot,
  Plus,
  Copy,
  Trash2,
  Activity,
  TrendingUp,
  TrendingDown,
  MoreVertical,
  RefreshCw,
  Search,
  X,
  ChevronDown,
  Wallet,
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CORAL = "#D97757";

const statusConfig = {
  active: { label: "Activo", dot: "bg-emerald-500", text: "text-emerald-600", bg: "bg-emerald-50", border: "border-emerald-200" },
  replicating: { label: "Replicando", dot: "bg-orange-400", text: "text-orange-500", bg: "bg-orange-50", border: "border-orange-200" },
  dying: { label: "Muriendo", dot: "bg-red-500", text: "text-red-500", bg: "bg-red-50", border: "border-red-200" },
  dead: { label: "Muerto", dot: "bg-gray-400", text: "text-gray-500", bg: "bg-gray-100", border: "border-gray-200" },
  paused: { label: "Pausado", dot: "bg-amber-400", text: "text-amber-500", bg: "bg-amber-50", border: "border-amber-200" },
  hibernating: { label: "Hibernando", dot: "bg-blue-400", text: "text-blue-500", bg: "bg-blue-50", border: "border-blue-200" },
};

/* ─── Apple-style progress bar ─── */
function HealthBar({ value }) {
  const pct = Math.max(0, Math.min(100, value));
  const color = pct > 60 ? "bg-emerald-500" : pct > 30 ? "bg-amber-400" : "bg-red-500";
  return (
    <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
      <div
        className={`h-full rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

/* ─── Apple-style dropdown ─── */
function Dropdown({ open, onToggle, children }) {
  if (!open) return null;
  return (
    <div className="absolute right-0 top-10 z-30 w-52 rounded-2xl bg-white shadow-xl border border-gray-100 overflow-hidden">
      {children}
    </div>
  );
}

function DropdownItem({ onClick, disabled, accent, children }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors
        ${disabled ? "opacity-40 cursor-not-allowed" : "hover:bg-gray-50 cursor-pointer"}
        ${accent || "text-gray-700"}`}
    >
      {children}
    </button>
  );
}

/* ─── Single Agent Card ─── */
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
  const childrenCount = lineage.children_ids?.length ?? agent.children_ids?.length ?? 0;
  const generation = agent.generation ?? 1;

  const sc = statusConfig[agent.status] || statusConfig.active;
  const healthPercent = Math.max(0, Math.min(100, (balance / initialBalance) * 100));

  return (
    <div className="relative bg-white rounded-2xl shadow-sm border border-gray-100 p-6 transition-all duration-200 hover:shadow-md">
      {/* Header row */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${CORAL}18` }}>
            <Bot className="w-5 h-5" style={{ color: CORAL }} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">{agent.name}</h3>
            <p className="text-xs text-gray-400 uppercase tracking-wide">{agent.type}</p>
          </div>
        </div>

        {/* Dropdown trigger */}
        <div className="relative">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors"
          >
            <MoreVertical className="w-4 h-4 text-gray-400" />
          </button>
          <Dropdown open={menuOpen} onToggle={() => setMenuOpen(false)}>
            <DropdownItem onClick={() => { onDeposit(agent.id); setMenuOpen(false); }}>
              <Activity className="w-4 h-4 text-blue-500" />
              <span>Fondear +€100</span>
            </DropdownItem>
            <div className="h-px bg-gray-100 mx-2" />
            <DropdownItem onClick={() => { onSimulate(agent.id, 10); setMenuOpen(false); }}>
              <TrendingUp className="w-4 h-4 text-emerald-500" />
              <span>Simular +€10</span>
            </DropdownItem>
            <DropdownItem onClick={() => { onSimulate(agent.id, -10); setMenuOpen(false); }}>
              <TrendingDown className="w-4 h-4 text-red-500" />
              <span>Simular −€10</span>
            </DropdownItem>
            <div className="h-px bg-gray-100 mx-2" />
            <DropdownItem
              onClick={() => { onReplicate(agent.id); setMenuOpen(false); }}
              disabled={balance < 50 || agent.status === "dead"}
              accent="text-gray-700"
            >
              <Copy className="w-4 h-4" style={{ color: CORAL }} />
              <span>Replicar</span>
            </DropdownItem>
            <DropdownItem
              onClick={() => { onDestroy(agent.id); setMenuOpen(false); }}
              disabled={agent.status === "dead"}
              accent="text-red-500"
            >
              <Trash2 className="w-4 h-4" />
              <span>Eliminar</span>
            </DropdownItem>
          </Dropdown>
        </div>
      </div>

      {/* Status badge */}
      <div className="mb-4">
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-semibold rounded-full ${sc.bg} ${sc.text} ${sc.border} border`}>
          <span className={`w-1.5 h-1.5 rounded-full ${sc.dot}`} />
          {sc.label}
        </span>
      </div>

      {/* Balance + ROI */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-[11px] text-gray-400 uppercase tracking-wide mb-0.5">Saldo</p>
          <p className="font-bold text-lg text-gray-900">€{balance.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-[11px] text-gray-400 uppercase tracking-wide mb-0.5">ROI</p>
          <p className={`font-bold text-lg ${roi >= 0 ? "text-emerald-600" : "text-red-500"}`}>
            {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Health bar */}
      <div className="mb-4">
        <div className="flex justify-between text-[11px] text-gray-400 mb-1.5">
          <span className="uppercase tracking-wide">Salud</span>
          <span>{healthPercent.toFixed(0)}%</span>
        </div>
        <HealthBar value={healthPercent} />
      </div>

      {/* Footer stats */}
      <div className="grid grid-cols-4 gap-3 pt-4 border-t border-gray-100">
        {[
          { label: "Gen", value: generation },
          { label: "Trades", value: tradesCount },
          { label: "Ganados", value: successfulTrades, cls: "text-emerald-600" },
          { label: "Clones", value: childrenCount },
        ].map((s) => (
          <div key={s.label} className="text-center">
            <p className="text-[10px] text-gray-400 uppercase tracking-wide">{s.label}</p>
            <p className={`text-sm font-semibold text-gray-700 ${s.cls || ""}`}>{s.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Create Agent Dialog ─── */
function CreateDialog({ open, onClose, onCreate }) {
  const [name, setName] = useState("");
  const [type, setType] = useState("crypto_analyzer");
  const [balance, setBalance] = useState(100);
  const [typeOpen, setTypeOpen] = useState(false);

  const handleSubmit = () => {
    if (!name.trim()) {
      toast.error("El nombre del agente es obligatorio");
      return;
    }
    onCreate({ name: name.trim(), type, initial_balance: balance });
    setName("");
    setType("crypto_analyzer");
    setBalance(100);
    onClose();
  };

  if (!open) return null;

    const types = [
    { value: "crypto_analyzer", label: "Analista Crypto" },
    { value: "business_scout", label: "Explorador de Negocios" },
    { value: "trader", label: "Trader" },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />

      {/* Panel */}
      <div className="relative bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Nuevo Agente</h2>
          <button onClick={onClose} className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        <div className="space-y-5">
          {/* Name */}
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1.5">Nombre</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Alpha-001"
              className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 text-sm placeholder-gray-300 focus:outline-none focus:ring-2 focus:border-transparent transition-all"
              style={{ focusRingColor: CORAL }}
              onFocus={(e) => { e.target.style.boxShadow = `0 0 0 3px ${CORAL}25`; e.target.style.borderColor = CORAL; }}
              onBlur={(e) => { e.target.style.boxShadow = "none"; e.target.style.borderColor = "#e5e7eb"; }}
            />
          </div>

          {/* Type */}
          <div className="relative">
            <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1.5">Tipo</label>
            <button
              onClick={() => setTypeOpen(!typeOpen)}
              className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-900 hover:bg-gray-100 transition-colors"
            >
              <span>{types.find((t) => t.value === type)?.label}</span>
              <ChevronDown className="w-4 h-4 text-gray-400" />
            </button>
            {typeOpen && (
              <div className="absolute z-20 w-full mt-1 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
                {types.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => { setType(t.value); setTypeOpen(false); }}
                    className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${t.value === type ? "font-medium" : "text-gray-600"} hover:bg-gray-50`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Balance */}
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1.5">Saldo inicial (€)</label>
            <input
              type="number"
              min="10"
              step="10"
              value={balance}
              onChange={(e) => setBalance(parseFloat(e.target.value) || 0)}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:border-transparent transition-all"
              onFocus={(e) => { e.target.style.boxShadow = `0 0 0 3px ${CORAL}25`; e.target.style.borderColor = CORAL; }}
              onBlur={(e) => { e.target.style.boxShadow = "none"; e.target.style.borderColor = "#e5e7eb"; }}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 mt-8">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            className="flex-1 py-3 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90 active:scale-[0.98]"
            style={{ backgroundColor: CORAL }}
          >
            Desplegar
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Status count bar ─── */
function StatusBar({ counts }) {
  const items = [
    { key: "active", label: "Activos", dot: "bg-emerald-500" },
    { key: "replicating", label: "Replicando", dot: "bg-orange-400" },
    { key: "dying", label: "Muriendo", dot: "bg-red-500" },
    { key: "dead", label: "Muertos", dot: "bg-gray-400" },
  ];
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {items.map((it) => (
        <div key={it.key} className="bg-white rounded-2xl border border-gray-100 px-5 py-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <span className={`w-2 h-2 rounded-full ${it.dot}`} />
            <span className="text-xs text-gray-400 uppercase tracking-wide">{it.label}</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{counts[it.key]}</p>
        </div>
      ))}
    </div>
  );
}

/* ─── Main Page ─── */
export default function AgentsPage() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [refreshing, setRefreshing] = useState(false);

  const fetchAgents = async () => {
    try {
      const res = await axios.get(`${API}/agents`);
      setAgents(res.data.agents || []);
    } catch {
      toast.error("Error al cargar agentes");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchAgents(); }, []);

  const handleCreate = async (data) => {
    try {
      await axios.post(`${API}/agents`, data);
      toast.success("Agente desplegado");
      fetchAgents();
    } catch {
      toast.error("Error al crear agente");
    }
  };

  const handleReplicate = async (id) => {
    try {
      await axios.post(`${API}/agents/${id}/replicate`);
      toast.success("Agente replicado");
      fetchAgents();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Error al replicar");
    }
  };

  const handleDestroy = async (id) => {
    try {
      await axios.delete(`${API}/agents/${id}`);
      toast.success("Agente eliminado");
      fetchAgents();
    } catch {
      toast.error("Error al eliminar agente");
    }
  };

  const handleSimulate = async (id, profit) => {
    try {
      await axios.post(`${API}/agents/${id}/simulate-trade?profit=${profit}`);
      toast.success(`Trade simulado: ${profit >= 0 ? "+" : ""}€${profit}`);
      fetchAgents();
    } catch {
      toast.error("Error al simular trade");
    }
  };

  const handleDeposit = async (id) => {
    try {
      await axios.post(`${API}/agents/${id}/deposit?amount=100`);
      toast.success("Fondeado: +€100");
      fetchAgents();
    } catch {
      toast.error("Error al fondear");
    }
  };

  const counts = {
    active: agents.filter((a) => a.status === "active").length,
    replicating: agents.filter((a) => a.status === "replicating").length,
    dying: agents.filter((a) => a.status === "dying").length,
    dead: agents.filter((a) => a.status === "dead").length,
  };

  const filtered = agents.filter((a) => {
    const matchSearch = a.name.toLowerCase().includes(search.toLowerCase()) || a.type.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "all" || a.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAgents();
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#F5F3EF" }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Agentes</h1>
            <p className="text-sm text-gray-400 mt-0.5">Despliega, replica y gestiona agentes autónomos</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleRefresh}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm font-medium text-gray-600 hover:bg-gray-50 transition-all shadow-sm"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
              Actualizar
            </button>
            <button
              onClick={() => setCreateOpen(true)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90 active:scale-[0.98] shadow-sm"
              style={{ backgroundColor: CORAL }}
            >
              <Plus className="w-4 h-4" />
              Nuevo Agente
            </button>
          </div>
        </div>

        {/* Status counts */}
        <div className="mb-6">
          <StatusBar counts={counts} />
        </div>

        {/* Search + filter bar */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar agentes…"
              className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 bg-white text-sm text-gray-900 placeholder-gray-300 focus:outline-none focus:ring-2 focus:border-transparent transition-all shadow-sm"
              onFocus={(e) => { e.target.style.boxShadow = `0 0 0 3px ${CORAL}25, 0 1px 2px rgba(0,0,0,0.04)`; e.target.style.borderColor = CORAL; }}
              onBlur={(e) => { e.target.style.boxShadow = "0 1px 2px rgba(0,0,0,0.04)"; e.target.style.borderColor = "#e5e7eb"; }}
            />
          </div>
          <div className="flex gap-2 flex-wrap">
            {["all", "active", "replicating", "dying", "dead"].map((s) => {
              const sc = s === "all" ? null : statusConfig[s];
              const isActive = statusFilter === s;
              return (
                <button
                  key={s}
                  onClick={() => setStatusFilter(s)}
                  className={`px-4 py-2.5 rounded-xl text-xs font-medium uppercase tracking-wide transition-all shadow-sm
                    ${isActive
                      ? "text-white"
                      : "bg-white border border-gray-200 text-gray-500 hover:bg-gray-50"
                    }`}
                  style={isActive ? { backgroundColor: s === "all" ? CORAL : undefined } : {}}
                >
                  {isActive && s !== "all" && sc && (
                    <span className="inline-flex items-center gap-1.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${sc.dot}`} />
                      {sc.label}
                    </span>
                  )}
                  {isActive && s === "all" && "Todos"}
                  {!isActive && s === "all" && "Todos"}
                  {!isActive && s !== "all" && sc?.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Agent grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white rounded-2xl h-72 animate-pulse shadow-sm border border-gray-100" />
            ))}
          </div>
        ) : filtered.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                onReplicate={handleReplicate}
                onDestroy={handleDestroy}
                onSimulate={handleSimulate}
                onDeposit={handleDeposit}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm py-20 text-center">
            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl flex items-center justify-center" style={{ backgroundColor: `${CORAL}12` }}>
              <Activity className="w-6 h-6" style={{ color: CORAL, opacity: 0.5 }} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {search || statusFilter !== "all" ? "Sin resultados" : "No hay agentes desplegados"}
            </h3>
            <p className="text-sm text-gray-400 mb-6">
              {search || statusFilter !== "all"
                ? "Prueba a ajustar la búsqueda o los filtros"
                : "Despliega tu primer agente autónomo para empezar"}
            </p>
            {!search && statusFilter === "all" && (
              <button
                onClick={() => setCreateOpen(true)}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90 active:scale-[0.98]"
                style={{ backgroundColor: CORAL }}
              >
                <Plus className="w-4 h-4" />
                Desplegar Agente
              </button>
            )}
          </div>
        )}
      </div>

      {/* Create dialog */}
      <CreateDialog open={createOpen} onClose={() => setCreateOpen(false)} onCreate={handleCreate} />
    </div>
  );
}
