import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { motion } from "framer-motion";
import {
  Bot, TrendingUp, TrendingDown, Wallet, Activity, Zap,
  ArrowUpRight, ArrowDownRight, Target, Percent, Hash, Cpu,
  Pause, ShieldAlert, ChevronRight, Trophy, RotateCcw
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart as RePieChart, Pie, Cell
} from "recharts";
import { dashboardAPI, agentsAPI, cryptoAPI } from "@/lib/api";
import { useAppMode } from "@/hooks/useAppMode";

const CYAN = "#00F3FF";
const PURPLE = "#7000FF";
const GREEN = "#00FF88";
const RED = "#FF003C";
const YELLOW = "#FFD600";
const GRAY = "#6B7280";

const PIE_COLORS = [CYAN, GREEN, YELLOW, GRAY];

/* ═══════════════ CONFETTI ═══════════════ */
const Confetti = ({ active }) => {
  if (!active) return null;
  const particles = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    delay: Math.random() * 0.5,
    color: [CYAN, GREEN, "#FF6B6B", YELLOW, "#6BCB77"][Math.floor(Math.random() * 5)]
  }));

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          initial={{ y: -20, opacity: 1 }}
          animate={{ y: "100vh", opacity: 0, rotate: 720 }}
          transition={{ duration: 2.5, delay: p.delay, ease: "easeOut" }}
          className="absolute w-2 h-2 rounded-full"
          style={{ left: `${p.x}%`, backgroundColor: p.color }}
        />
      ))}
    </div>
  );
};

/* ═══════════════ METRIC CARD ═══════════════ */
const MetricCard = ({ title, value, change, icon: Icon, color = "cyan", subtitle, sparkline, size = "default" }) => {
  const colorMap = {
    cyan: { text: CYAN, bg: "rgba(0,243,255,0.1)", border: "rgba(0,243,255,0.15)" },
    green: { text: GREEN, bg: "rgba(0,255,136,0.1)", border: "rgba(0,255,136,0.15)" },
    red: { text: RED, bg: "rgba(255,0,60,0.1)", border: "rgba(255,0,60,0.15)" },
    gray: { text: GRAY, bg: "rgba(107,114,128,0.1)", border: "rgba(107,114,128,0.15)" },
    yellow: { text: YELLOW, bg: "rgba(255,214,0,0.1)", border: "rgba(255,214,0,0.15)" },
    purple: { text: PURPLE, bg: "rgba(112,0,255,0.1)", border: "rgba(112,0,255,0.15)" },
  };

  const c = colorMap[color] || colorMap.cyan;
  const isPositive = change >= 0;
  const sizeMap = { large: "text-4xl", default: "text-3xl", small: "text-2xl" };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className="glass-card rounded-xl p-5 transition-all duration-200"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="evo-section-title mb-2">{title}</p>
          <p className={`${sizeMap[size]} font-semibold tracking-tight`} style={{ color: c.text }}>
            {value}
          </p>
          {change !== undefined && (
            <div className="flex items-center gap-1 mt-1.5 text-xs font-medium" style={{ color: isPositive ? GREEN : RED }}>
              {isPositive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
              <span>{isPositive ? "+" : ""}{typeof change === 'number' ? change.toFixed(2) : change}%</span>
            </div>
          )}
          {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
          style={{ background: c.bg }}
        >
          <Icon size={20} style={{ color: c.text }} aria-hidden="true" />
        </div>
      </div>
      {sparkline && (
        <div className="h-8 mt-3">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sparkline}>
              <Area type="monotone" dataKey="value" stroke={c.text} fill={c.text} fillOpacity={0.1} strokeWidth={1.5} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </motion.div>
  );
};

/* ═══════════════ AGENT BADGE ═══════════════ */
const AgentStatusBadge = ({ status }) => {
  const config = {
    active: { bg: "bg-green-500/15", text: "text-green-400", ring: "ring-green-500/30", label: "Activo" },
    paused: { bg: "bg-yellow-500/15", text: "text-yellow-400", ring: "ring-yellow-500/30", label: "Pausado" },
    replicating: { bg: "bg-cyan-500/15", text: "text-cyan-400", ring: "ring-cyan-500/30", label: "Replicando" },
    dying: { bg: "bg-red-500/15", text: "text-red-400", ring: "ring-red-500/30", label: "En riesgo" },
    dead: { bg: "bg-white/5", text: "text-muted-foreground", ring: "ring-white/10", label: "Muerto" }
  };
  const c = config[status] || config.active;

  return (
    <span className={`evo-badge ${c.bg} ${c.text} ring-1 ${c.ring}`}>{c.label}</span>
  );
};

/* ═══════════════ MINI AGENT CARD ═══════════════ */
const MiniAgentCard = ({ agent }) => {
  const finances = agent.finances || {};
  const performance = agent.performance || {};
  const balance = finances.current_balance ?? agent.balance ?? 0;
  const roi = performance.roi_percent ?? agent.roi ?? 0;
  const generation = agent.generation ?? 1;

  const isShaking = agent.status === 'dying';

  return (
    <motion.div
      animate={isShaking ? { x: [-4, 4, -4, 4, 0] } : {}}
      transition={{ duration: 0.4, repeat: 2 }}
      className={`p-3.5 rounded-lg border transition-all cursor-pointer ${
        agent.status === 'dying'
          ? "border-red-500/20 bg-red-500/5"
          : agent.status === 'replicating'
          ? "border-cyan-500/20 bg-cyan-500/5"
          : "border-white/5 bg-transparent hover:bg-white/[0.02]"
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Bot size={14} className="text-cyan-400" aria-hidden="true" />
          <span className="text-sm font-semibold truncate max-w-[120px]">{agent.name}</span>
          <span className="evo-badge-cyan text-[10px]">G{generation}</span>
        </div>
        <AgentStatusBadge status={agent.status} />
      </div>
      <div className="flex items-center justify-between text-sm">
        <span className="font-semibold font-mono">€{balance.toFixed(0)}</span>
        <span className="font-semibold font-mono" style={{ color: roi >= 0 ? GREEN : RED }}>
          {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
        </span>
      </div>
    </motion.div>
  );
};

/* ═══════════════ SYSTEM HEALTH GAUGE ═══════════════ */
const SystemHealthGauge = ({ health = 95 }) => {
  const getColor = (v) => v >= 80 ? GREEN : v >= 50 ? YELLOW : RED;
  const color = getColor(health);
  const circumference = 2 * Math.PI * 56;
  const offset = circumference - (health / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-[140px] h-[140px]">
        <svg width="140" height="140" className="rotate-[-90deg]">
          <circle cx="70" cy="70" r="56" stroke="rgba(255,255,255,0.05)" strokeWidth="8" fill="none" />
          <circle
            cx="70" cy="70" r="56" stroke={color} strokeWidth="8" fill="none"
            strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
            style={{ transition: "stroke-dashoffset 0.8s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color }}>{health}%</span>
          <span className="evo-section-title">Salud</span>
        </div>
      </div>
    </div>
  );
};

/* ═══════════════ TOP PERFORMER CARD ═══════════════ */
const TopPerformerCard = ({ agent, rank }) => {
  const roi = agent.roi ?? agent.performance?.roi_percent ?? 0;
  const balance = agent.balance ?? agent.finances?.current_balance ?? 0;
  const rankColors = {
    1: { bg: "bg-yellow-500/15", text: "#FFB800" },
    2: { bg: "bg-white/5", text: GRAY },
    3: { bg: "bg-cyan-500/10", text: "#CD7F32" }
  };
  const rc = rankColors[rank] || rankColors[2];

  return (
    <div className="flex items-center gap-3 p-3.5 rounded-lg bg-white/[0.02] border border-white/5">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm shrink-0 ${rc.bg}`} style={{ color: rc.text }}>
        #{rank}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold truncate">{agent.name}</p>
        <p className="text-xs text-muted-foreground font-mono">€{balance.toFixed(0)}</p>
      </div>
      <div className="text-sm font-bold font-mono" style={{ color: roi >= 0 ? GREEN : RED }}>
        {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
      </div>
    </div>
  );
};

/* ═══════════════ EMERGENCY DIALOG ═══════════════ */
const EmergencyDialog = ({ open, onClose, onConfirm, loading }) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="glass-card rounded-xl p-7 max-w-sm w-[90%]"
        onClick={(e) => e.stopPropagation()}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="emergency-title"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-11 h-11 rounded-lg bg-red-500/15 flex items-center justify-center">
            <ShieldAlert size={22} className="text-red-500" aria-hidden="true" />
          </div>
          <h3 id="emergency-title" className="text-lg font-bold text-red-500">Parada de Emergencia</h3>
        </div>
        <div className="text-sm text-muted-foreground leading-relaxed mb-6">
          <p className="mb-3">Esta acción <strong className="text-red-500">TERMINARÁ TODOS LOS AGENTES</strong> inmediatamente.</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Todos los agentes activos y pausados serán eliminados</li>
            <li>Los saldos de los agentes se establecerán en $0</li>
            <li>Esta acción <strong>NO se puede deshacer</strong></li>
          </ul>
        </div>
        <div className="flex gap-2.5">
          <button onClick={onClose} className="flex-1 evo-button-outline py-2.5 text-sm">Cancelar</button>
          <button onClick={onConfirm} disabled={loading} className="flex-1 evo-button-destructive py-2.5 text-sm disabled:opacity-50">
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <RotateCcw size={16} className="animate-spin" /> Deteniendo...
              </span>
            ) : "Confirmar Parada"}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

/* ═══════════════ MAIN DASHBOARD ═══════════════ */
export default function DashboardPage() {
  const navigate = useNavigate();
  const { isSimulation } = useAppMode();
  const [stats, setStats] = useState(null);
  const [agents, setAgents] = useState([]);
  const [cryptoData, setCryptoData] = useState([]);
  const [portfolioData, setPortfolioData] = useState([]);
  const [portfolioStats, setPortfolioStats] = useState(null);
  const [portfolioPeriod, setPortfolioPeriod] = useState("7d");
  const [loading, setLoading] = useState(true);
  const [agentTab, setAgentTab] = useState("all");
  const [actionLoading, setActionLoading] = useState(null);
  const [emergencyDialogOpen, setEmergencyDialogOpen] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const prevReplicating = useRef(0);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, agentsRes, cryptoRes] = await Promise.all([
        dashboardAPI.stats(),
        agentsAPI.list({ simulation: isSimulation }),
        cryptoAPI.topCoins(),
      ]);

      const newReplicating = statsRes.data.agents?.replicating || 0;
      if (newReplicating > prevReplicating.current && prevReplicating.current > 0) {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 3000);
      }
      prevReplicating.current = newReplicating;

      setStats(statsRes.data);
      setAgents(agentsRes.data.agents || []);
      setCryptoData(cryptoRes.data.coins || []);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  }, [isSimulation]);

  const fetchPortfolioHistory = useCallback(async () => {
    try {
      const res = await dashboardAPI.portfolioHistory(portfolioPeriod);
      setPortfolioData(res.data.history || []);
      setPortfolioStats({
        initialCapital: res.data.initial_capital,
        currentValue: res.data.current_value,
        totalPnl: res.data.total_pnl,
        pnlPercent: res.data.pnl_percent
      });
    } catch (error) {
      console.error("Error fetching portfolio history:", error);
    }
  }, [portfolioPeriod]);

  useEffect(() => { fetchData(); const i = setInterval(fetchData, 30000); return () => clearInterval(i); }, [fetchData, isSimulation]);
  useEffect(() => { fetchPortfolioHistory(); }, [fetchPortfolioHistory]);

  const handlePauseAll = async () => {
    setActionLoading('pause');
    try { const res = await agentsAPI.pauseAll(); toast.success(`${res.data.paused_count} agentes pausados`); fetchData(); }
    catch { toast.error("Error al pausar agentes"); }
    finally { setActionLoading(null); }
  };

  const handleResumeAll = async () => {
    setActionLoading('resume');
    try { const res = await agentsAPI.resumeAll(); toast.success(`${res.data.resumed_count} agentes reanudados`); fetchData(); }
    catch { toast.error("Error al reanudar agentes"); }
    finally { setActionLoading(null); }
  };

  const handleEmergencyStop = async () => {
    setActionLoading('emergency');
    try { const res = await agentsAPI.emergencyStop(); toast.error(`¡PARADA DE EMERGENCIA! ${res.data.terminated_count} agentes terminados`, { duration: 5000 }); setEmergencyDialogOpen(false); fetchData(); fetchPortfolioHistory(); }
    catch { toast.error("Error en parada de emergencia"); }
    finally { setActionLoading(null); }
  };

  const hasPausedAgents = useMemo(() => agents.some(a => a.status === 'paused'), [agents]);
  const hasActiveAgents = useMemo(() => agents.some(a => a.status === 'active' || a.status === 'replicating'), [agents]);

  const generateSparkline = useCallback((base, variance, trend = 0) =>
    Array.from({ length: 12 }, (_, i) => ({ value: base + (Math.random() - 0.5) * variance + (i * trend) })), []);

  const agentDistribution = useMemo(() => [
    { name: 'Activos', value: stats?.agents?.active || 0, color: CYAN },
    { name: 'Replicando', value: stats?.agents?.replicating || 0, color: GREEN },
    { name: 'En riesgo', value: stats?.agents?.dying || 0, color: YELLOW },
    { name: 'Muertos', value: stats?.agents?.dead || 0, color: GRAY }
  ].filter(d => d.value > 0), [stats]);

  const filteredAgents = useMemo(() => agents.filter(agent => {
    if (agentTab === 'all') return true;
    if (agentTab === 'active') return agent.status === 'active';
    if (agentTab === 'best') return (agent.performance?.roi_percent ?? agent.roi ?? 0) > 0;
    if (agentTab === 'risk') return agent.status === 'dying' || (agent.finances?.current_balance ?? agent.balance ?? 0) < 20;
    return true;
  }), [agents, agentTab]);

  const topPerformers = useMemo(() => [...agents]
    .sort((a, b) => (b.performance?.roi_percent ?? b.roi ?? 0) - (a.performance?.roi_percent ?? a.roi ?? 0))
    .slice(0, 5), [agents]);

  const systemHealth = useMemo(() => stats
    ? Math.round(((stats.agents?.active || 0) / Math.max(stats.agents?.total || 1, 1)) * 100)
    : 95, [stats]);

  const isPositive = portfolioStats?.totalPnl >= 0;
  const chartColor = isPositive ? GREEN : RED;
  const periodItems = ['1d', '7d', '1m', 'all'];
  const periodLabels = { '1d': '1D', '7d': '7D', '1m': '1M', 'all': 'Todo' };
  const tabItems = [
    { key: "all", label: "Todos" },
    { key: "active", label: "Activos" },
    { key: "best", label: "Mejores" },
    { key: "risk", label: "En riesgo" }
  ];

  /* ── Loading Skeleton ── */
  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.1 }}
              className="h-[110px] glass-card rounded-xl"
            />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 h-[320px] glass-card rounded-xl" />
          <div className="h-[320px] glass-card rounded-xl" />
        </div>
      </div>
    );
  }

  /* ── Main Render ── */
  return (
    <div className="min-h-screen bg-background">
      <Confetti active={showConfetti} />

      {/* Simulation Mode Banner */}
      {isSimulation && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="bg-purple-500/10 border-b border-purple-500/20 px-6 py-2"
        >
          <div className="max-w-[1400px] mx-auto flex items-center justify-center gap-2">
            <Zap className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-400 font-medium">Modo Simulación — Los datos mostrados son ficticios</span>
          </div>
        </motion.div>
      )}

      <div className="max-w-[1400px] mx-auto p-4 lg:p-6 space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="evo-metric-value !text-3xl font-bold tracking-wide uppercase">Vista General</h1>
            <p className="text-sm text-muted-foreground mt-1">Métricas del orquestador en tiempo real</p>
          </div>
          <div className="evo-badge-success flex items-center gap-2">
            <motion.div
              animate={{ opacity: [1, 0.4, 1], scale: [1, 0.7, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-2 h-2 rounded-full bg-green-500"
            />
            En vivo
          </div>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <MetricCard title="Agentes Activos" value={stats?.agents?.active || 0} change={12.5} icon={Bot} color="cyan" subtitle={`${stats?.agents?.total || 0} en total`} sparkline={generateSparkline(3, 2, 0.1)} />
          <MetricCard title="Balance Total" value={`€${(stats?.finances?.total_balance || 0).toFixed(0)}`} change={stats?.finances?.avg_roi || 0} icon={Wallet} color="green" sparkline={generateSparkline(200, 50, 5)} />
          <MetricCard title="Tasa de Éxito" value={`${((stats?.trading?.win_rate || 0) * 100).toFixed(0)}%`} icon={Target} color="cyan" size="small" />
          <MetricCard title="Total Trades" value={stats?.trading?.total_trades || 0} icon={Hash} color="gray" size="small" />
          <MetricCard title="PnL 24h" value={`€${(stats?.trading?.pnl_24h || 0).toFixed(0)}`} change={(stats?.trading?.pnl_24h || 0) > 0 ? 5.2 : -3.1} icon={(stats?.trading?.pnl_24h || 0) >= 0 ? TrendingUp : TrendingDown} color={(stats?.trading?.pnl_24h || 0) >= 0 ? "green" : "red"} size="small" />
          <MetricCard title="Tokens Usados" value={`${((stats?.llm?.total_tokens || 0) / 1000).toFixed(1)}K`} icon={Cpu} color="yellow" size="small" subtitle={`~€${(stats?.llm?.cost_estimate || 0).toFixed(3)}`} />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Portfolio Chart */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="lg:col-span-2 glass-card rounded-xl p-6">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <h2 className="text-base font-semibold text-foreground">Rendimiento del Portfolio</h2>
                {portfolioStats && (
                  <span className="text-sm font-semibold font-mono" style={{ color: chartColor }}>
                    {isPositive ? "+" : ""}€{portfolioStats.totalPnl.toFixed(2)} ({portfolioStats.pnlPercent.toFixed(1)}%)
                  </span>
                )}
              </div>
              <div className="flex gap-1">
                {periodItems.map((period) => (
                  <button key={period} onClick={() => setPortfolioPeriod(period)}
                    className={`px-2.5 py-1 text-xs font-medium rounded-md transition-all ${period === portfolioPeriod ? "bg-cyan-500/15 text-cyan-400" : "text-muted-foreground hover:text-foreground hover:bg-white/5"}`}>
                    {periodLabels[period]}
                  </button>
                ))}
              </div>
            </div>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={portfolioData}>
                  <defs>
                    <linearGradient id="portfolioGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={chartColor} stopOpacity={0.15} />
                      <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: GRAY, fontSize: 11 }} interval="preserveStartEnd" />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: GRAY, fontSize: 11 }} tickFormatter={(v) => `€${v}`} width={55} domain={['dataMin - 10', 'dataMax + 10']} />
                  <Tooltip contentStyle={{ background: "hsl(240 10% 6%)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10, boxShadow: "0 8px 24px rgba(0,0,0,0.4)", fontSize: 12 }} formatter={(value) => [`€${value.toFixed(2)}`, 'Portfolio']} labelFormatter={(label) => `Hora: ${label}`} />
                  <Area type="monotone" dataKey="value" stroke={chartColor} strokeWidth={2.5} fillOpacity={1} fill="url(#portfolioGrad)" name="Portfolio" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Right Column */}
          <div className="flex flex-col gap-4">
            {/* System Health */}
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-card rounded-xl p-6 flex flex-col items-center">
              <h3 className="evo-section-title mb-3">Salud del Sistema</h3>
              <SystemHealthGauge health={systemHealth} />
              <div className="grid grid-cols-2 gap-4 w-full mt-4">
                <div className="text-center">
                  <p className="text-xl font-bold text-green-500">{stats?.agents?.replicating || 0}</p>
                  <p className="evo-section-title mt-0.5">Replicando</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold" style={{ color: (stats?.agents?.dying || 0) > 0 ? YELLOW : GREEN }}>{stats?.agents?.dying || 0}</p>
                  <p className="evo-section-title mt-0.5">En riesgo</p>
                </div>
              </div>
            </motion.div>

            {/* Agent Distribution */}
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card rounded-xl p-6">
              <h3 className="evo-section-title mb-2">Distribución</h3>
              <div className="h-[140px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart>
                    <Pie data={agentDistribution} cx="50%" cy="50%" innerRadius={36} outerRadius={56} dataKey="value" strokeWidth={0}>
                      {agentDistribution.map((entry, index) => <Cell key={index} fill={entry.color} />)}
                    </Pie>
                  </RePieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-3 mt-1">
                {agentDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full" style={{ background: item.color }} />
                    <span className="text-xs text-muted-foreground">{item.name}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        {/* Agents + Top Performers */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Agents */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold">Agentes</h2>
              <button onClick={() => navigate('/agents')} className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 font-medium">
                Ver todos <ChevronRight size={14} aria-hidden="true" />
              </button>
            </div>
            <div className="flex gap-1 mb-4 p-0.5 bg-white/5 rounded-lg">
              {tabItems.map((tab) => (
                <button key={tab.key} onClick={() => setAgentTab(tab.key)}
                  className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${agentTab === tab.key ? "bg-black/60 text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"}`}>
                  {tab.label}
                </button>
              ))}
            </div>
            <div className="space-y-2 max-h-[220px] overflow-y-auto">
              {filteredAgents.length > 0 ? filteredAgents.slice(0, 5).map((agent) => (
                <MiniAgentCard key={agent.id} agent={agent} />
              )) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Bot size={28} className="mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No se encontraron agentes</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Top Performers */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="glass-card rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-yellow-500/15 flex items-center justify-center">
                <Trophy size={16} style={{ color: "#FFB800" }} aria-hidden="true" />
              </div>
              <h2 className="text-base font-semibold">Mejores Rendimientos</h2>
            </div>
            <div className="space-y-2 max-h-[260px] overflow-y-auto">
              {topPerformers.length > 0 ? topPerformers.map((agent, index) => (
                <TopPerformerCard key={agent.id} agent={agent} rank={index + 1} />
              )) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Trophy size={28} className="mx-auto mb-2 opacity-30" />
                  <p className="text-sm">Sin datos aún</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Quick Actions + Crypto */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Quick Actions */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card rounded-xl p-6">
            <h2 className="text-base font-semibold mb-4">Acciones Rápidas</h2>
            <div className="space-y-2.5">
              <button onClick={() => navigate('/agents')} className="evo-button-primary w-full py-3 text-sm">
                <Zap size={18} aria-hidden="true" /> <span className="ml-1">Desplegar Agente</span>
              </button>
              {hasPausedAgents ? (
                <button onClick={handleResumeAll} disabled={actionLoading === 'resume'} className="evo-button w-full py-3 text-sm bg-green-600 text-white hover:bg-green-500 disabled:opacity-50">
                  <Pause size={18} aria-hidden="true" className="rotate-180" /> <span className="ml-1">Reanudar Todos</span>
                </button>
              ) : (
                <button onClick={handlePauseAll} disabled={!hasActiveAgents || actionLoading === 'pause'} className="evo-button-outline w-full py-3 text-sm disabled:opacity-50">
                  <Pause size={18} aria-hidden="true" /> <span className="ml-1">Pausar Todos</span>
                </button>
              )}
              <button onClick={() => setEmergencyDialogOpen(true)} disabled={!hasActiveAgents && !hasPausedAgents} className="evo-button-destructive w-full py-3 text-sm disabled:opacity-50">
                <ShieldAlert size={18} aria-hidden="true" /> <span className="ml-1">Parada de Emergencia</span>
              </button>
            </div>
          </motion.div>

          {/* Crypto Market */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="lg:col-span-2 glass-card rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold">Mercado Crypto</h2>
              <button onClick={() => navigate('/crypto')} className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 font-medium">
                Ver todo <ChevronRight size={14} aria-hidden="true" />
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
              {cryptoData.map((coin) => (
                <motion.button
                  key={coin.id}
                  whileHover={{ borderColor: "rgba(0,243,255,0.3)", backgroundColor: "rgba(0,243,255,0.03)" }}
                  onClick={() => navigate('/crypto')}
                  className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/5 text-left transition-all"
                >
                  <img src={coin.image} alt={coin.name} className="w-7 h-7 rounded-full" loading="lazy" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">{coin.symbol.toUpperCase()}</p>
                    <p className="text-xs text-muted-foreground font-mono">€{coin.current_price?.toLocaleString()}</p>
                  </div>
                  <span className="text-xs font-semibold font-mono" style={{ color: coin.price_change_24h >= 0 ? GREEN : RED }}>
                    {coin.price_change_24h >= 0 ? "+" : ""}{coin.price_change_24h?.toFixed(1)}%
                  </span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      <EmergencyDialog open={emergencyDialogOpen} onClose={() => setEmergencyDialogOpen(false)} onConfirm={handleEmergencyStop} loading={actionLoading === 'emergency'} />
    </div>
  );
}
