import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Activity, Bot, TrendingUp, TrendingDown, Copy, AlertTriangle, Target, DollarSign, Zap, RefreshCw, Calendar, Search, Skull } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { notificationsAPI } from "@/lib/api";

const eventIcons = {
  agent_created: Bot, agent_replicated: Copy, agent_dying: AlertTriangle, agent_dead: Skull,
  trade_opened: TrendingUp, trade_closed: TrendingUp, trade_win: TrendingUp, trade_loss: TrendingDown,
  payment_received: DollarSign, alert_low_balance: AlertTriangle, alert_high_drawdown: AlertTriangle,
  alert_replication_ready: Zap, opportunity_detected: Target, system_info: Activity,
  simulation_started: Zap, simulation_stopped: Activity,
  default: Activity
};

const ActivityEventCard = ({ event, onClick }) => {
  const Icon = eventIcons[event.type] || eventIcons.default;
  const colorMap = {
    agent_created: "text-cyan-400 bg-cyan-500/10", agent_replicated: "text-green-400 bg-green-500/10",
    agent_dying: "text-red-400 bg-red-500/10", agent_dead: "text-red-400 bg-red-500/10",
    trade_opened: "text-cyan-400 bg-cyan-500/10", trade_win: "text-green-400 bg-green-500/10", trade_loss: "text-red-400 bg-red-500/10",
    payment_received: "text-green-400 bg-green-500/10", alert_low_balance: "text-yellow-400 bg-yellow-500/10",
    alert_replication_ready: "text-cyan-400 bg-cyan-500/10", opportunity_detected: "text-yellow-400 bg-yellow-500/10",
    simulation_started: "text-green-400 bg-green-500/10", simulation_stopped: "text-yellow-400 bg-yellow-500/10",
    default: "text-cyan-400 bg-cyan-500/10"
  };
  const colorClass = colorMap[event.type] || colorMap.default;

  const timeAgo = (dateString) => {
    const seconds = Math.floor((Date.now() - new Date(dateString)) / 1000);
    if (seconds < 60) return 'Ahora';
    if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)}h`;
    return `Hace ${Math.floor(seconds / 86400)}d`;
  };

  return (
    <div className="flex items-start gap-4 p-4 hover:bg-white/[0.02] transition-colors cursor-pointer rounded-lg" onClick={() => event.link && onClick(event.link)}>
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${colorClass}`}>
        <Icon className="w-5 h-5" aria-hidden="true" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h3 className="text-sm font-medium text-foreground leading-snug">{event.title}</h3>
            <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{event.description}</p>
          </div>
          {event.amount != null && (
            <span className={`text-sm font-semibold shrink-0 font-mono ${event.amount >= 0 ? "text-green-400" : "text-red-400"}`}>
              {event.amount >= 0 ? "+" : "-"}${Math.abs(event.amount).toFixed(2)}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 mt-2">
          {event.agent_name && (<div className="flex items-center gap-1.5"><Bot className="w-3.5 h-3.5 text-muted-foreground" /><span className="text-xs text-muted-foreground">{event.agent_name}</span></div>)}
          <span className="text-xs text-muted-foreground font-mono">{timeAgo(event.created_at)}</span>
        </div>
      </div>
    </div>
  );
};

const ActivityStats = ({ events }) => {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const todayEvents = events.filter(e => new Date(e.created_at) >= today);
  const trades = events.filter(e => e.type.includes('trade'));
  const wins = events.filter(e => e.type === 'trade_win');
  const replications = events.filter(e => e.type === 'agent_replicated');

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[
        { label: "Hoy", value: todayEvents.length, color: "text-cyan-400" },
        { label: "Operaciones", value: trades.length, color: "text-foreground" },
        { label: "Ganancias", value: wins.length, color: "text-green-400" },
        { label: "Replicaciones", value: replications.length, color: "text-green-400" }
      ].map((stat) => (
        <div key={stat.label} className="glass-card rounded-xl p-5">
          <p className="evo-section-title">{stat.label}</p>
          <p className={`text-2xl font-semibold mt-1 tracking-tight font-mono ${stat.color}`}>{stat.value}</p>
        </div>
      ))}
    </div>
  );
};

const TimelineView = ({ events, onNavigate }) => {
  const groupedEvents = events.reduce((groups, event) => {
    const date = new Date(event.created_at).toLocaleDateString('es-ES', { weekday: 'long', month: 'long', day: 'numeric' });
    if (!groups[date]) groups[date] = [];
    groups[date].push(event);
    return groups;
  }, {});

  return (
    <div className="space-y-6">
      {Object.entries(groupedEvents).map(([date, dateEvents]) => (
        <div key={date}>
          <div className="flex items-center gap-3 mb-3 px-1">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass-card">
              <Calendar className="w-3.5 h-3.5 text-muted-foreground" /><span className="text-xs font-medium text-foreground capitalize">{date}</span>
            </div>
            <div className="flex-1 h-px bg-white/5" />
            <span className="text-xs text-muted-foreground">{dateEvents.length} eventos</span>
          </div>
          <div className="glass-card rounded-xl divide-y divide-white/5">
            {dateEvents.map((event) => <ActivityEventCard key={event.id} event={event} onClick={onNavigate} />)}
          </div>
        </div>
      ))}
    </div>
  );
};

export default function ActivityPage() {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState("list");

  const fetchActivity = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter !== "all") params.type_filter = filter;
      const res = await notificationsAPI.activity(null, filter !== "all" ? filter : null);
      setEvents(res.data.events || []);
    } catch (error) { console.error("Error al obtener actividad:", error); }
    finally { setLoading(false); }
  }, [filter]);

  useEffect(() => { fetchActivity(); }, [fetchActivity]);

  const filteredEvents = events.filter(event => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return event.title?.toLowerCase().includes(q) || event.description?.toLowerCase().includes(q) || event.agent_name?.toLowerCase().includes(q);
  });

  const filterTabs = [
    { value: "all", label: "Todo" },
    { value: "agent", label: "Agentes" },
    { value: "trade", label: "Operaciones" },
    { value: "alert", label: "Alertas" }
  ];

  const getFilteredByTab = (evts, tab) => {
    if (tab === "all") return evts;
    if (tab === "agent") return evts.filter(e => e.type.startsWith('agent_'));
    if (tab === "trade") return evts.filter(e => e.type.startsWith('trade_'));
    if (tab === "alert") return evts.filter(e => e.type.startsWith('alert_'));
    return evts;
  };

  const displayEvents = getFilteredByTab(filteredEvents, filter);

  return (
    <div className="min-h-screen bg-background" data-testid="activity-page">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl font-bold uppercase tracking-wide text-foreground">Actividad</h1>
            <p className="text-sm text-muted-foreground mt-1">Eventos del sistema y feed de notificaciones</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input type="text" placeholder="Buscar eventos..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="evo-input pl-10 py-2.5 rounded-full text-sm w-52" />
            </div>
            <div className="flex glass-card rounded-lg p-0.5">
              {["list", "timeline"].map((mode) => (
                <button key={mode} onClick={() => setViewMode(mode)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${viewMode === mode ? "bg-cyan-500/15 text-cyan-400" : "text-muted-foreground hover:text-foreground"}`}>
                  {mode === "list" ? "Lista" : "Cronología"}
                </button>
              ))}
            </div>
            <button onClick={fetchActivity} className="p-2.5 rounded-lg glass-card hover:bg-white/5 transition-colors" aria-label="Actualizar">
              <RefreshCw className={`w-4 h-4 text-muted-foreground ${loading && "animate-spin"}`} />
            </button>
          </div>
        </div>

        {/* Stats */}
        <ActivityStats events={events} />

        {/* Filter Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {filterTabs.map((tab) => {
            const count = getFilteredByTab(displayEvents, tab.value).length;
            const isActive = filter === tab.value;
            return (
              <button key={tab.value} onClick={() => setFilter(tab.value)}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${isActive ? "bg-cyan-500/15 text-cyan-400 ring-1 ring-cyan-500/20" : "glass-card text-muted-foreground hover:text-foreground"}`}>
                {tab.label}<span className={`text-xs ${isActive ? "text-cyan-400/70" : "text-muted-foreground"}`}>{count}</span>
              </button>
            );
          })}
        </div>

        {/* Content */}
        {loading ? (
          <div className="glass-card rounded-xl p-6 space-y-3">{[...Array(5)].map((_, i) => <div key={i} className="h-20 bg-white/5 rounded-lg animate-pulse" />)}</div>
        ) : displayEvents.length > 0 ? (
          viewMode === "timeline" ? (
            <TimelineView events={displayEvents} onNavigate={navigate} />
          ) : (
            <div className="glass-card rounded-xl divide-y divide-white/5">
              {displayEvents.map((event) => <ActivityEventCard key={event.id} event={event} onClick={navigate} />)}
            </div>
          )
        ) : (
          <div className="glass-card rounded-xl text-center py-16 px-6">
            <div className="w-16 h-16 rounded-lg bg-white/5 flex items-center justify-center mx-auto mb-4"><Activity className="w-8 h-8 text-muted-foreground" /></div>
            <h3 className="text-base font-semibold text-foreground mb-1">Sin Actividad</h3>
            <p className="text-sm text-muted-foreground">
              {filter === "all" ? "Los eventos aparecerán aquí cuando tus agentes estén operando" : `No se encontraron eventos de ${filter.toLowerCase()}`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
