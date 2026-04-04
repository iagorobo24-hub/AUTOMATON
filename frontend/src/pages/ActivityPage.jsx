import { useState, useEffect, useCallback } from "react";
import {
  Activity,
  Bot,
  TrendingUp,
  TrendingDown,
  Copy,
  AlertTriangle,
  Target,
  DollarSign,
  Zap,
  RefreshCw,
  Calendar,
  Search,
  Skull
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const eventIcons = {
  agent_created: Bot,
  agent_replicated: Copy,
  agent_dying: AlertTriangle,
  agent_dead: Skull,
  trade_opened: TrendingUp,
  trade_closed: TrendingUp,
  trade_win: TrendingUp,
  trade_loss: TrendingDown,
  payment_received: DollarSign,
  alert_low_balance: AlertTriangle,
  alert_high_drawdown: AlertTriangle,
  alert_replication_ready: Zap,
  opportunity_detected: Target,
  system_info: Activity,
  default: Activity
};

const eventColors = {
  agent_created: "coral",
  agent_replicated: "green",
  agent_dying: "red",
  agent_dead: "red",
  trade_win: "green",
  trade_loss: "red",
  trade_opened: "coral",
  trade_closed: "coral",
  payment_received: "green",
  alert_low_balance: "orange",
  alert_replication_ready: "coral",
  opportunity_detected: "orange",
  default: "coral"
};

const colorClasses = {
  coral: "text-[#D97757] bg-[#D97757]/10",
  green: "text-[#34C759] bg-[#34C759]/10",
  red: "text-[#FF3B30] bg-[#FF3B30]/10",
  orange: "text-[#FF9500] bg-[#FF9500]/10"
};

const ActivityEventCard = ({ event, onClick }) => {
  const Icon = eventIcons[event.type] || eventIcons.default;
  const color = eventColors[event.type] || eventColors.default;
  const colorClass = colorClasses[color];

  const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'Ahora mismo';
    if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)}h`;
    if (seconds < 604800) return `Hace ${Math.floor(seconds / 86400)}d`;
    return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' });
  };

  return (
    <div
      className={`flex items-start gap-4 p-4 rounded-xl hover:bg-[#F5F3EF] transition-colors cursor-pointer ${event.link ? "" : ""}`}
      onClick={() => event.link && onClick(event.link)}
    >
      <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${colorClass}`}>
        <Icon className="w-5 h-5" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h3 className="text-[15px] font-medium text-[#1a1a1a] leading-snug">{event.title}</h3>
            <p className="text-[13px] text-[#86868b] mt-0.5 line-clamp-2">
              {event.description}
            </p>
          </div>
          {event.amount !== null && event.amount !== undefined && (
            <span className={`text-[15px] font-semibold shrink-0 ${event.amount >= 0 ? "text-[#34C759]" : "text-[#FF3B30]"}`}>
              {event.amount >= 0 ? "+" : ""}${Math.abs(event.amount).toFixed(2)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 mt-2">
          {event.agent_name && (
            <div className="flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5 text-[#86868b]" />
              <span className="text-[12px] text-[#86868b]">{event.agent_name}</span>
            </div>
          )}
          <span className="text-[12px] text-[#86868b]">
            {timeAgo(event.created_at)}
          </span>
        </div>
      </div>
    </div>
  );
};

const ActivityStats = ({ events }) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const todayEvents = events.filter(e => new Date(e.created_at) >= today);
  const trades = events.filter(e => e.type.includes('trade'));
  const wins = events.filter(e => e.type === 'trade_win');
  const replications = events.filter(e => e.type === 'agent_replicated');

  const stats = [
    { label: "Hoy", value: todayEvents.length, color: "text-[#D97757]" },
    { label: "Total Operaciones", value: trades.length, color: "text-[#1a1a1a]" },
    { label: "Ganancias", value: wins.length, color: "text-[#34C759]" },
    { label: "Replicaciones", value: replications.length, color: "text-[#34C759]" }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-white rounded-2xl p-5 shadow-sm border border-black/5">
          <p className="text-[12px] font-medium text-[#86868b] uppercase tracking-wide">
            {stat.label}
          </p>
          <p className={`text-[28px] font-semibold mt-1 tracking-tight ${stat.color}`}>
            {stat.value}
          </p>
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
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-black/5">
              <Calendar className="w-3.5 h-3.5 text-[#86868b]" />
              <span className="text-[13px] font-medium text-[#1a1a1a]">{date}</span>
            </div>
            <div className="flex-1 h-px bg-black/5" />
            <span className="text-[12px] text-[#86868b]">
              {dateEvents.length} eventos
            </span>
          </div>
          <div className="bg-white rounded-2xl shadow-sm border border-black/5 divide-y divide-black/5">
            {dateEvents.map((event) => (
              <ActivityEventCard
                key={event.id}
                event={event}
                onClick={onNavigate}
              />
            ))}
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
      if (filter !== "all") {
        params.type_filter = filter;
      }
      const res = await axios.get(`${API}/activity`, { params });
      setEvents(res.data.events || []);
    } catch (error) {
      console.error("Error al obtener actividad:", error);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchActivity();
  }, [fetchActivity]);

  const filteredEvents = events.filter(event => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      event.title?.toLowerCase().includes(query) ||
      event.description?.toLowerCase().includes(query) ||
      event.agent_name?.toLowerCase().includes(query)
    );
  });

  const filterTabs = [
    { value: "all", label: "Todo" },
    { value: "agent", label: "Agentes" },
    { value: "trade", label: "Operaciones" },
    { value: "alert", label: "Alertas" }
  ];

  const getFilteredByTab = (events, tab) => {
    if (tab === "all") return events;
    if (tab === "agent") return events.filter(e => e.type.startsWith('agent_'));
    if (tab === "trade") return events.filter(e => e.type.startsWith('trade_'));
    if (tab === "alert") return events.filter(e => e.type.startsWith('alert_'));
    return events;
  };

  return (
    <div className="min-h-screen bg-[#F5F3EF]" data-testid="activity-page">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-[28px] font-semibold text-[#1a1a1a] tracking-tight">
              Actividad
            </h1>
            <p className="text-[15px] text-[#86868b] mt-1">
              Eventos del sistema y feed de notificaciones
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#86868b]" />
              <input
                type="text"
                placeholder="Buscar eventos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2.5 rounded-full border border-black/10 text-[14px] text-[#1a1a1a] bg-white focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all w-52"
              />
            </div>

            <div className="flex bg-white rounded-full border border-black/5 p-1">
              <button
                onClick={() => setViewMode("list")}
                className={`px-3 py-1.5 rounded-full text-[13px] font-medium transition-all ${viewMode === "list" ? "bg-[#D97757] text-white shadow-sm" : "text-[#86868b] hover:text-[#1a1a1a]"}`}
              >
                Lista
              </button>
              <button
                onClick={() => setViewMode("timeline")}
                className={`px-3 py-1.5 rounded-full text-[13px] font-medium transition-all ${viewMode === "timeline" ? "bg-[#D97757] text-white shadow-sm" : "text-[#86868b] hover:text-[#1a1a1a]"}`}
              >
                Cronología
              </button>
            </div>

            <button
              onClick={fetchActivity}
              className="p-2.5 rounded-full bg-white border border-black/5 hover:bg-[#F5F3EF] transition-colors"
            >
              <RefreshCw className={`w-4 h-4 text-[#86868b] ${loading && "animate-spin"}`} />
            </button>
          </div>
        </div>

        {/* Stats */}
        <ActivityStats events={events} />

        {/* Filter Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {filterTabs.map((tab) => {
            const count = getFilteredByTab(filteredEvents, tab.value).length;
            const isActive = filter === tab.value;
            return (
              <button
                key={tab.value}
                onClick={() => setFilter(tab.value)}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-[14px] font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? "bg-[#D97757] text-white shadow-sm shadow-[#D97757]/20"
                    : "bg-white text-[#86868b] border border-black/5 hover:text-[#1a1a1a] hover:border-black/10"
                }`}
              >
                {tab.label}
                <span className={`text-[12px] ${isActive ? "text-white/70" : "text-[#86868b]"}`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Content */}
        {loading ? (
          <div className="bg-white rounded-2xl shadow-sm border border-black/5 p-6 space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-20 bg-[#F5F3EF] rounded-xl animate-pulse" />
            ))}
          </div>
        ) : getFilteredByTab(filteredEvents, filter).length > 0 ? (
          viewMode === "timeline" ? (
            <TimelineView
              events={getFilteredByTab(filteredEvents, filter)}
              onNavigate={navigate}
            />
          ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-black/5 divide-y divide-black/5">
              {getFilteredByTab(filteredEvents, filter).map((event) => (
                <ActivityEventCard
                  key={event.id}
                  event={event}
                  onClick={navigate}
                />
              ))}
            </div>
          )
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-black/5 text-center py-16 px-6">
            <div className="w-16 h-16 rounded-full bg-[#F5F3EF] flex items-center justify-center mx-auto mb-4">
              <Activity className="w-8 h-8 text-[#86868b]" />
            </div>
            <h3 className="text-[17px] font-semibold text-[#1a1a1a] mb-1">Sin Actividad</h3>
            <p className="text-[15px] text-[#86868b]">
              {filter === "all"
                ? "Los eventos aparecerán aquí cuando tus agentes estén operando"
                : `No se encontraron eventos de ${filter.toLowerCase()}`
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
