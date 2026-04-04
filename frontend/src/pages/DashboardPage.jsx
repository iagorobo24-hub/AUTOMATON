import { useState, useEffect, useCallback, useRef } from "react";
import {
  Bot,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Copy,
  Target,
  Percent,
  Trophy,
  Hash,
  Cpu,
  AlertTriangle,
  Play,
  Pause,
  RotateCcw,
  ChevronRight,
  PartyPopper,
  ShieldAlert,
  Wallet,
  BarChart3,
  PieChart,
  Layers,
  Sparkle
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import axios from "axios";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie,
  Cell
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CORAL = "#D97757";
const CORAL_LIGHT = "#F0B8A0";
const CORAL_BG = "#FDF3ED";
const BG_WARM = "#F5F3EF";
const GREEN = "#34C759";
const RED = "#FF3B30";
const YELLOW = "#FF9500";
const GRAY = "#8E8E93";
const TEXT_PRIMARY = "#1D1D1F";
const TEXT_SECONDARY = "#6E6E73";
const TEXT_TERTIARY = "#AEAEB2";
const CARD_BG = "#FFFFFF";
const CARD_SHADOW = "0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04)";
const CARD_SHADOW_HOVER = "0 2px 6px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.06)";

const PIE_COLORS = [CORAL, GREEN, YELLOW, GRAY];

// ==================== ANIMATED NUMBER ====================
const AnimatedNumber = ({ value, prefix = "", suffix = "", decimals = 0, duration = 800 }) => {
  const [displayValue, setDisplayValue] = useState(0);
  const prevValue = useRef(0);

  useEffect(() => {
    const startValue = prevValue.current;
    const endValue = typeof value === 'number' ? value : parseFloat(value) || 0;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = startValue + (endValue - startValue) * eased;
      setDisplayValue(current);
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        prevValue.current = endValue;
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return (
    <span style={{ fontVariantNumeric: "tabular-nums" }}>
      {prefix}{displayValue.toFixed(decimals)}{suffix}
    </span>
  );
};

// ==================== CONFETTI ====================
const Confetti = ({ active }) => {
  if (!active) return null;

  const particles = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    delay: Math.random() * 0.5,
    color: [CORAL, GREEN, "#FF6B6B", "#FFD93D", "#6BCB77"][Math.floor(Math.random() * 5)]
  }));

  return (
    <div style={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 50, overflow: "hidden" }}>
      {particles.map((p) => (
        <div
          key={p.id}
          style={{
            position: "absolute",
            width: 8,
            height: 8,
            borderRadius: "50%",
            left: `${p.x}%`,
            backgroundColor: p.color,
            animationDelay: `${p.delay}s`,
            animation: "confetti-fall 2.5s ease-out forwards"
          }}
        />
      ))}
      <style>{`
        @keyframes confetti-fall {
          0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
          100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
        }
      `}</style>
    </div>
  );
};

// ==================== METRIC CARD ====================
const MetricCard = ({ title, value, change, icon: Icon, color = "coral", subtitle, sparkline, size = "default", animate = false, isShaking = false }) => {
  const colorMap = {
    coral: { text: CORAL, bg: CORAL_BG, iconBg: CORAL_BG },
    green: { text: GREEN, bg: "#E8F9ED", iconBg: "#E8F9ED" },
    red: { text: RED, bg: "#FFECEC", iconBg: "#FFECEC" },
    gray: { text: GRAY, bg: "#F5F5F7", iconBg: "#F5F5F7" },
    yellow: { text: YELLOW, bg: "#FFF3E0", iconBg: "#FFF3E0" }
  };

  const c = colorMap[color] || colorMap.coral;
  const isPositive = change >= 0;
  const numericValue = typeof value === 'string'
    ? parseFloat(value.replace(/[^0-9.-]/g, '')) || 0
    : value;
  const prefix = typeof value === 'string' && value.startsWith('$') ? '$' :
                 typeof value === 'string' && value.startsWith('€') ? '€' : '';
  const suffix = typeof value === 'string' && value.endsWith('%') ? '%' :
                 typeof value === 'string' && value.endsWith('K') ? 'K' : '';

  const sizeMap = { large: 36, default: 28, small: 22 };
  const iconSizeMap = { large: 24, default: 20, small: 16 };

  return (
    <div
      style={{
        background: CARD_BG,
        borderRadius: 20,
        boxShadow: isShaking ? "0 0 0 2px rgba(255,59,48,0.3)" : CARD_SHADOW,
        padding: size === "small" ? 16 : 20,
        transition: "all 0.2s ease",
        animation: isShaking ? "shake 0.5s ease-in-out" : undefined
      }}
      onMouseEnter={(e) => { e.currentTarget.style.boxShadow = CARD_SHADOW_HOVER; e.currentTarget.style.transform = "translateY(-1px)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.boxShadow = CARD_SHADOW; e.currentTarget.style.transform = "translateY(0)"; }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div style={{ flex: 1 }}>
          <p style={{ fontSize: 11, fontWeight: 600, letterSpacing: 0.5, color: TEXT_TERTIARY, textTransform: "uppercase", marginBottom: 6 }}>
            {title}
          </p>
          <p style={{ fontSize: sizeMap[size], fontWeight: 700, color: c.text, lineHeight: 1.1 }}>
            {animate ? (
              <AnimatedNumber value={numericValue} prefix={prefix} suffix={suffix} decimals={suffix === 'K' ? 1 : suffix === '%' ? 0 : 0} />
            ) : value}
          </p>
          {change !== undefined && (
            <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 6, fontSize: 12, fontWeight: 500, color: isPositive ? GREEN : RED }}>
              {isPositive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
              <span>{isPositive ? "+" : ""}{typeof change === 'number' ? change.toFixed(2) : change}%</span>
            </div>
          )}
          {subtitle && (
            <p style={{ fontSize: 11, color: TEXT_TERTIARY, marginTop: 4 }}>{subtitle}</p>
          )}
        </div>
        <div style={{ width: 40, height: 40, borderRadius: 12, background: c.iconBg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <Icon size={iconSizeMap[size]} color={c.text} />
        </div>
      </div>
      {sparkline && (
        <div style={{ height: 32, marginTop: 12, marginLeft: -4, marginRight: -4 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sparkline}>
              <Area
                type="monotone"
                dataKey="value"
                stroke={c.text}
                fill={c.text}
                fillOpacity={0.1}
                strokeWidth={1.5}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-4px); }
          75% { transform: translateX(4px); }
        }
      `}</style>
    </div>
  );
};

// ==================== AGENT STATUS BADGE ====================
const AgentStatusBadge = ({ status }) => {
  const config = {
    active: { bg: "#E8F9ED", text: GREEN, label: "Activo" },
    paused: { bg: "#FFF3E0", text: YELLOW, label: "Pausado" },
    replicating: { bg: CORAL_BG, text: CORAL, label: "Replicando" },
    dying: { bg: "#FFECEC", text: RED, label: "En riesgo" },
    dead: { bg: "#F5F5F7", text: GRAY, label: "Muerto" }
  };
  const c = config[status] || config.active;

  return (
    <span style={{
      display: "inline-block",
      padding: "2px 8px",
      fontSize: 10,
      fontWeight: 600,
      borderRadius: 6,
      background: c.bg,
      color: c.text,
      letterSpacing: 0.3
    }}>
      {c.label}
    </span>
  );
};

// ==================== MINI AGENT CARD ====================
const MiniAgentCard = ({ agent, isShaking = false }) => {
  const finances = agent.finances || {};
  const performance = agent.performance || {};
  const balance = finances.current_balance ?? agent.balance ?? 0;
  const roi = performance.roi_percent ?? agent.roi ?? 0;
  const generation = agent.generation ?? 1;

  const borderColor = agent.status === 'dying' ? "rgba(255,59,48,0.2)" :
                      agent.status === 'replicating' ? "rgba(217,119,87,0.2)" :
                      "rgba(0,0,0,0.06)";
  const bgColor = agent.status === 'dying' ? "#FFF8F8" :
                  agent.status === 'replicating' ? CORAL_BG :
                  "transparent";

  return (
    <div style={{
      padding: 14,
      borderRadius: 14,
      border: `1px solid ${borderColor}`,
      background: bgColor,
      transition: "all 0.2s ease",
      cursor: "pointer",
      animation: isShaking ? "shake 0.5s ease-in-out" : undefined
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Bot size={14} color={CORAL} />
          <span style={{ fontSize: 13, fontWeight: 600, color: TEXT_PRIMARY, maxWidth: 120, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {agent.name}
          </span>
          <span style={{ fontSize: 10, fontWeight: 500, color: CORAL, background: CORAL_BG, padding: "1px 6px", borderRadius: 4 }}>
            G{generation}
          </span>
        </div>
        <AgentStatusBadge status={agent.status} />
      </div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 13 }}>
        <span style={{ fontWeight: 600, color: TEXT_PRIMARY }}>€{balance.toFixed(0)}</span>
        <span style={{ fontWeight: 600, color: roi >= 0 ? GREEN : RED }}>
          {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
        </span>
      </div>
    </div>
  );
};

// ==================== QUICK ACTION BUTTON ====================
const QuickActionButton = ({ icon: Icon, label, onClick, color = "coral", disabled }) => {
  const colorMap = {
    coral: { bg: CORAL, bgHover: "#C46A4B", text: "#FFFFFF" },
    green: { bg: GREEN, bgHover: "#2DB84E", text: "#FFFFFF" },
    red: { bg: RED, bgHover: "#E0342B", text: "#FFFFFF" },
    gray: { bg: "#F5F5F7", bgHover: "#E5E5EA", text: TEXT_PRIMARY }
  };
  const c = colorMap[color] || colorMap.coral;

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
        padding: "16px 12px",
        borderRadius: 14,
        border: "none",
        background: disabled ? "#F5F5F7" : c.bg,
        color: disabled ? GRAY : c.text,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.5 : 1,
        transition: "all 0.2s ease",
        fontWeight: 600,
        fontSize: 11,
        letterSpacing: 0.3
      }}
      onMouseEnter={(e) => { if (!disabled) e.currentTarget.style.background = c.bgHover; }}
      onMouseLeave={(e) => { if (!disabled) e.currentTarget.style.background = c.bg; }}
    >
      <Icon size={20} />
      <span>{label}</span>
    </button>
  );
};

// ==================== SYSTEM HEALTH GAUGE ====================
const SystemHealthGauge = ({ health = 95 }) => {
  const getColor = (value) => {
    if (value >= 80) return GREEN;
    if (value >= 50) return YELLOW;
    return RED;
  };

  const color = getColor(health);
  const circumference = 2 * Math.PI * 56;
  const offset = circumference - (health / 100) * circumference;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ position: "relative", width: 140, height: 140 }}>
        <svg width="140" height="140" style={{ transform: "rotate(-90deg)" }}>
          <circle cx="70" cy="70" r="56" stroke="#F5F5F7" strokeWidth="8" fill="none" />
          <circle
            cx="70"
            cy="70"
            r="56"
            stroke={color}
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: "stroke-dashoffset 0.8s ease" }}
          />
        </svg>
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <span style={{ fontSize: 32, fontWeight: 700, color: color }}>{health}%</span>
          <span style={{ fontSize: 10, color: TEXT_TERTIARY, textTransform: "uppercase", letterSpacing: 0.5 }}>Salud</span>
        </div>
      </div>
    </div>
  );
};

// ==================== TOP PERFORMER CARD ====================
const TopPerformerCard = ({ agent, rank }) => {
  const roi = agent.roi ?? agent.performance?.roi_percent ?? 0;
  const balance = agent.balance ?? agent.finances?.current_balance ?? 0;

  const rankColors = {
    1: { bg: "#FFF8E1", text: "#FFB800" },
    2: { bg: "#F5F5F7", text: "#8E8E93" },
    3: { bg: "#FDF3ED", text: "#CD7F32" }
  };
  const rc = rankColors[rank] || { bg: "#F5F5F7", text: GRAY };

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: 12,
      padding: 14,
      borderRadius: 14,
      background: "#FAFAFA",
      border: "1px solid rgba(0,0,0,0.04)"
    }}>
      <div style={{
        width: 32,
        height: 32,
        borderRadius: 10,
        background: rc.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: 700,
        fontSize: 13,
        color: rc.text,
        flexShrink: 0
      }}>
        #{rank}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{ fontSize: 13, fontWeight: 600, color: TEXT_PRIMARY, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {agent.name}
        </p>
        <p style={{ fontSize: 11, color: TEXT_TERTIARY }}>€{balance.toFixed(0)} saldo</p>
      </div>
      <div style={{ fontSize: 14, fontWeight: 700, color: roi >= 0 ? GREEN : RED }}>
        {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
      </div>
    </div>
  );
};

// ==================== EMERGENCY DIALOG ====================
const EmergencyDialog = ({ open, onClose, onConfirm, loading }) => {
  if (!open) return null;

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      zIndex: 100,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "rgba(0,0,0,0.3)",
      backdropFilter: "blur(8px)"
    }}
      onClick={onClose}
    >
      <div
        style={{
          background: CARD_BG,
          borderRadius: 20,
          padding: 28,
          maxWidth: 400,
          width: "90%",
          boxShadow: "0 20px 60px rgba(0,0,0,0.15)"
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, background: "#FFECEC", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <ShieldAlert size={22} color={RED} />
          </div>
          <h3 style={{ fontSize: 18, fontWeight: 700, color: RED, margin: 0 }}>Parada de Emergencia</h3>
        </div>
        <div style={{ color: TEXT_SECONDARY, fontSize: 14, lineHeight: 1.6, marginBottom: 24 }}>
          <p style={{ marginBottom: 12 }}>Esta acción <strong style={{ color: RED }}>TERMINARÁ TODOS LOS AGENTES</strong> inmediatamente.</p>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li style={{ marginBottom: 4 }}>Todos los agentes activos y pausados serán eliminados</li>
            <li style={{ marginBottom: 4 }}>Los saldos de los agentes se establecerán en $0</li>
            <li>Esta acción <strong>NO se puede deshacer</strong></li>
          </ul>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={onClose}
            style={{
              flex: 1,
              padding: "12px 16px",
              borderRadius: 12,
              border: "1px solid rgba(0,0,0,0.1)",
              background: CARD_BG,
              color: TEXT_PRIMARY,
              fontWeight: 600,
              fontSize: 14,
              cursor: "pointer",
              transition: "all 0.15s ease"
            }}
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            style={{
              flex: 1,
              padding: "12px 16px",
              borderRadius: 12,
              border: "none",
              background: loading ? "#F5F5F7" : RED,
              color: loading ? GRAY : "#FFFFFF",
              fontWeight: 600,
              fontSize: 14,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.15s ease",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 8
            }}
          >
            {loading ? (
              <>
                <RotateCcw size={16} style={{ animation: "spin 1s linear infinite" }} />
                Deteniendo...
              </>
            ) : (
              "Confirmar Parada"
            )}
          </button>
        </div>
      </div>
      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

// ==================== MAIN DASHBOARD ====================
export default function DashboardPage() {
  const navigate = useNavigate();
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
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/crypto/top-coins?limit=5`)
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
  }, []);

  const fetchPortfolioHistory = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/portfolio/history?period=${portfolioPeriod}`);
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

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  useEffect(() => {
    fetchPortfolioHistory();
  }, [fetchPortfolioHistory]);

  const handlePauseAll = async () => {
    setActionLoading('pause');
    try {
      const res = await axios.post(`${API}/agents/pause-all`);
      toast.success(`${res.data.paused_count} agentes pausados`);
      fetchData();
    } catch (error) {
      toast.error("Error al pausar agentes");
    } finally {
      setActionLoading(null);
    }
  };

  const handleResumeAll = async () => {
    setActionLoading('resume');
    try {
      const res = await axios.post(`${API}/agents/resume-all`);
      toast.success(`${res.data.resumed_count} agentes reanudados`);
      fetchData();
    } catch (error) {
      toast.error("Error al reanudar agentes");
    } finally {
      setActionLoading(null);
    }
  };

  const handleEmergencyStop = async () => {
    setActionLoading('emergency');
    try {
      const res = await axios.post(`${API}/agents/emergency-stop?confirm=true`);
      toast.error(`¡PARADA DE EMERGENCIA! ${res.data.terminated_count} agentes terminados`, { duration: 5000 });
      setEmergencyDialogOpen(false);
      fetchData();
      fetchPortfolioHistory();
    } catch (error) {
      toast.error("Error en parada de emergencia");
    } finally {
      setActionLoading(null);
    }
  };

  const hasPausedAgents = agents.some(a => a.status === 'paused');
  const hasActiveAgents = agents.some(a => a.status === 'active' || a.status === 'replicating');
  const hasDyingAgents = agents.some(a => a.status === 'dying');

  const generateSparkline = (base, variance, trend = 0) =>
    Array.from({ length: 12 }, (_, i) => ({
      value: base + (Math.random() - 0.5) * variance + (i * trend)
    }));

  const agentDistribution = [
    { name: 'Activos', value: stats?.agents?.active || 0, color: CORAL },
    { name: 'Replicando', value: stats?.agents?.replicating || 0, color: GREEN },
    { name: 'En riesgo', value: stats?.agents?.dying || 0, color: YELLOW },
    { name: 'Muertos', value: stats?.agents?.dead || 0, color: GRAY }
  ].filter(d => d.value > 0);

  const filteredAgents = agents.filter(agent => {
    if (agentTab === 'all') return true;
    if (agentTab === 'active') return agent.status === 'active';
    if (agentTab === 'best') return (agent.performance?.roi_percent ?? agent.roi ?? 0) > 0;
    if (agentTab === 'risk') return agent.status === 'dying' || (agent.finances?.current_balance ?? agent.balance ?? 0) < 20;
    return true;
  });

  const topPerformers = [...agents]
    .sort((a, b) => (b.performance?.roi_percent ?? b.roi ?? 0) - (a.performance?.roi_percent ?? a.roi ?? 0))
    .slice(0, 5);

  const systemHealth = stats ? Math.round(
    ((stats.agents?.active || 0) / Math.max(stats.agents?.total || 1, 1)) * 100
  ) : 95;

  // Loading skeleton
  if (loading) {
    return (
      <div style={{ background: BG_WARM, minHeight: "100vh", padding: "24px 24px 48px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 16, marginBottom: 24 }}>
          {[...Array(6)].map((_, i) => (
            <div key={i} style={{ height: 110, background: "#E5E5EA", borderRadius: 20, animation: "pulse 1.5s ease-in-out infinite", animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16 }}>
          <div style={{ height: 320, background: "#E5E5EA", borderRadius: 20, animation: "pulse 1.5s ease-in-out infinite" }} />
          <div style={{ height: 320, background: "#E5E5EA", borderRadius: 20, animation: "pulse 1.5s ease-in-out infinite" }} />
        </div>
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </div>
    );
  }

  const isPositive = portfolioStats?.totalPnl >= 0;
  const chartColor = isPositive ? GREEN : RED;

  const tabItems = [
    { key: "all", label: "Todos" },
    { key: "active", label: "Activos" },
    { key: "best", label: "Mejores" },
    { key: "risk", label: "En riesgo" }
  ];

  const periodItems = ['1d', '7d', '1m', 'all'];
  const periodLabels = { '1d': '1D', '7d': '7D', '1m': '1M', 'all': 'Todo' };

  return (
    <div style={{ background: BG_WARM, minHeight: "100vh" }}>
      <Confetti active={showConfetti} />

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 24px 48px" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28 }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 700, color: TEXT_PRIMARY, margin: 0, letterSpacing: -0.5 }}>
              Vista General
            </h1>
            <p style={{ fontSize: 14, color: TEXT_SECONDARY, marginTop: 4 }}>
              Métricas del orquestador en tiempo real
            </p>
          </div>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "8px 14px",
            borderRadius: 20,
            background: "#E8F9ED"
          }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: GREEN, animation: "pulse-dot 2s ease-in-out infinite" }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: GREEN }}>En vivo</span>
          </div>
        </div>

        {/* Metric Cards Row */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 16, marginBottom: 24 }}>
          <MetricCard
            title="Agentes Activos"
            value={stats?.agents?.active || 0}
            change={12.5}
            icon={Bot}
            color="coral"
            subtitle={`${stats?.agents?.total || 0} en total`}
            sparkline={generateSparkline(3, 2, 0.1)}
            animate
          />
          <MetricCard
            title="Balance Total"
            value={`€${(stats?.finances?.total_balance || 0).toFixed(0)}`}
            change={stats?.finances?.avg_roi || 0}
            icon={Wallet}
            color="green"
            sparkline={generateSparkline(200, 50, 5)}
            animate
          />
          <MetricCard
            title="Tasa de Éxito"
            value={`${((stats?.trading?.win_rate || 0) * 100).toFixed(0)}%`}
            icon={Target}
            color="coral"
            size="small"
            animate
          />
          <MetricCard
            title="Total Trades"
            value={stats?.trading?.total_trades || 0}
            icon={Hash}
            color="gray"
            size="small"
            animate
          />
          <MetricCard
            title="PnL 24h"
            value={`€${(stats?.trading?.pnl_24h || 0).toFixed(0)}`}
            change={(stats?.trading?.pnl_24h || 0) > 0 ? 5.2 : -3.1}
            icon={(stats?.trading?.pnl_24h || 0) >= 0 ? TrendingUp : TrendingDown}
            color={(stats?.trading?.pnl_24h || 0) >= 0 ? "green" : "red"}
            size="small"
            animate
          />
          <MetricCard
            title="Tokens Usados"
            value={`${((stats?.llm?.total_tokens || 0) / 1000).toFixed(1)}K`}
            icon={Cpu}
            color="yellow"
            size="small"
            subtitle={`~€${(stats?.llm?.cost_estimate || 0).toFixed(3)}`}
            animate
          />
        </div>

        {/* Charts Row */}
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16, marginBottom: 24 }}>

          {/* Portfolio Chart */}
          <div style={{
            background: CARD_BG,
            borderRadius: 20,
            boxShadow: CARD_SHADOW,
            padding: 24
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <h2 style={{ fontSize: 16, fontWeight: 600, color: TEXT_PRIMARY, margin: 0 }}>
                  Rendimiento del Portfolio
                </h2>
                {portfolioStats && (
                  <span style={{ fontSize: 14, fontWeight: 600, color: isPositive ? GREEN : RED }}>
                    {isPositive ? "+" : ""}€{portfolioStats.totalPnl.toFixed(2)} ({portfolioStats.pnlPercent.toFixed(1)}%)
                  </span>
                )}
              </div>
              <div style={{ display: "flex", gap: 4 }}>
                {periodItems.map((period) => (
                  <button
                    key={period}
                    onClick={() => setPortfolioPeriod(period)}
                    style={{
                      padding: "5px 10px",
                      fontSize: 12,
                      fontWeight: 500,
                      borderRadius: 8,
                      border: "none",
                      background: period === portfolioPeriod ? CORAL_BG : "transparent",
                      color: period === portfolioPeriod ? CORAL : TEXT_TERTIARY,
                      cursor: "pointer",
                      transition: "all 0.15s ease"
                    }}
                  >
                    {periodLabels[period]}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ height: 280 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={portfolioData}>
                  <defs>
                    <linearGradient id="portfolioGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={chartColor} stopOpacity={0.15} />
                      <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="time"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: TEXT_TERTIARY, fontSize: 11 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: TEXT_TERTIARY, fontSize: 11 }}
                    tickFormatter={(v) => `€${v}`}
                    width={55}
                    domain={['dataMin - 10', 'dataMax + 10']}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#FFFFFF",
                      border: "none",
                      borderRadius: 12,
                      boxShadow: "0 4px 16px rgba(0,0,0,0.1)",
                      fontSize: 12,
                      padding: "8px 12px"
                    }}
                    formatter={(value) => [`€${value.toFixed(2)}`, 'Portfolio']}
                    labelFormatter={(label) => `Hora: ${label}`}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke={chartColor}
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#portfolioGrad)"
                    name="Portfolio"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Right Column: Health + Distribution */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* System Health */}
            <div style={{
              background: CARD_BG,
              borderRadius: 20,
              boxShadow: CARD_SHADOW,
              padding: 24,
              display: "flex",
              flexDirection: "column",
              alignItems: "center"
            }}>
              <h3 style={{ fontSize: 13, fontWeight: 600, color: TEXT_TERTIARY, textTransform: "uppercase", letterSpacing: 0.5, margin: "0 0 12px 0" }}>
                Salud del Sistema
              </h3>
              <SystemHealthGauge health={systemHealth} />
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, width: "100%", marginTop: 16 }}>
                <div style={{ textAlign: "center" }}>
                  <p style={{ fontSize: 20, fontWeight: 700, color: GREEN, margin: 0 }}>
                    {stats?.agents?.replicating || 0}
                  </p>
                  <p style={{ fontSize: 10, color: TEXT_TERTIARY, textTransform: "uppercase", letterSpacing: 0.5, marginTop: 2 }}>
                    Replicando
                  </p>
                </div>
                <div style={{ textAlign: "center" }}>
                  <p style={{ fontSize: 20, fontWeight: 700, color: (stats?.agents?.dying || 0) > 0 ? YELLOW : GREEN, margin: 0 }}>
                    {stats?.agents?.dying || 0}
                  </p>
                  <p style={{ fontSize: 10, color: TEXT_TERTIARY, textTransform: "uppercase", letterSpacing: 0.5, marginTop: 2 }}>
                    En riesgo
                  </p>
                </div>
              </div>
            </div>

            {/* Agent Distribution */}
            <div style={{
              background: CARD_BG,
              borderRadius: 20,
              boxShadow: CARD_SHADOW,
              padding: 24
            }}>
              <h3 style={{ fontSize: 13, fontWeight: 600, color: TEXT_TERTIARY, textTransform: "uppercase", letterSpacing: 0.5, margin: "0 0 8px 0" }}>
                Distribución
              </h3>
              <div style={{ height: 140 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart>
                    <Pie
                      data={agentDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={36}
                      outerRadius={56}
                      dataKey="value"
                      strokeWidth={0}
                    >
                      {agentDistribution.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "#FFFFFF",
                        border: "none",
                        borderRadius: 10,
                        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                        fontSize: 12
                      }}
                    />
                  </RePieChart>
                </ResponsiveContainer>
              </div>
              <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 4 }}>
                {agentDistribution.map((item) => (
                  <div key={item.name} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: item.color }} />
                    <span style={{ fontSize: 11, color: TEXT_SECONDARY }}>{item.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Agents + Top Performers Row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>

          {/* Agents Panel */}
          <div style={{
            background: CARD_BG,
            borderRadius: 20,
            boxShadow: CARD_SHADOW,
            padding: 24
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
              <h2 style={{ fontSize: 16, fontWeight: 600, color: TEXT_PRIMARY, margin: 0 }}>
                Agentes
              </h2>
              <button
                onClick={() => navigate('/agents')}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                  background: "none",
                  border: "none",
                  color: CORAL,
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: "pointer"
                }}
              >
                Ver todos <ChevronRight size={14} />
              </button>
            </div>

            {/* Tabs */}
            <div style={{ display: "flex", gap: 4, marginBottom: 16, background: "#F5F5F7", borderRadius: 10, padding: 3 }}>
              {tabItems.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setAgentTab(tab.key)}
                  style={{
                    flex: 1,
                    padding: "7px 8px",
                    fontSize: 12,
                    fontWeight: 500,
                    borderRadius: 8,
                    border: "none",
                    background: agentTab === tab.key ? "#FFFFFF" : "transparent",
                    color: agentTab === tab.key ? TEXT_PRIMARY : TEXT_TERTIARY,
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                    boxShadow: agentTab === tab.key ? "0 1px 3px rgba(0,0,0,0.08)" : "none"
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div style={{ maxHeight: 220, overflowY: "auto" }}>
              {filteredAgents.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {filteredAgents.slice(0, 5).map((agent) => (
                    <MiniAgentCard key={agent.id} agent={agent} isShaking={agent.status === 'dying'} />
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: "center", padding: 32, color: TEXT_TERTIARY }}>
                  <Bot size={28} style={{ margin: "0 auto 8px", opacity: 0.3 }} />
                  <p style={{ fontSize: 13 }}>No se encontraron agentes</p>
                </div>
              )}
            </div>
          </div>

          {/* Top Performers */}
          <div style={{
            background: CARD_BG,
            borderRadius: 20,
            boxShadow: CARD_SHADOW,
            padding: 24
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
              <div style={{ width: 32, height: 32, borderRadius: 10, background: "#FFF8E1", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Trophy size={16} color="#FFB800" />
              </div>
              <h2 style={{ fontSize: 16, fontWeight: 600, color: TEXT_PRIMARY, margin: 0 }}>
                Mejores Rendimientos
              </h2>
            </div>
            <div style={{ maxHeight: 260, overflowY: "auto", display: "flex", flexDirection: "column", gap: 8 }}>
              {topPerformers.length > 0 ? (
                topPerformers.map((agent, index) => (
                  <TopPerformerCard key={agent.id} agent={agent} rank={index + 1} />
                ))
              ) : (
                <div style={{ textAlign: "center", padding: 32, color: TEXT_TERTIARY }}>
                  <Trophy size={28} style={{ margin: "0 auto 8px", opacity: 0.3 }} />
                  <p style={{ fontSize: 13 }}>Sin datos aún</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions + Crypto Row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 16 }}>

          {/* Quick Actions */}
          <div style={{
            background: CARD_BG,
            borderRadius: 20,
            boxShadow: CARD_SHADOW,
            padding: 24
          }}>
            <h2 style={{ fontSize: 16, fontWeight: 600, color: TEXT_PRIMARY, margin: "0 0 16px 0" }}>
              Acciones Rápidas
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <QuickActionButton
                icon={Zap}
                label="Desplegar Agente"
                color="coral"
                onClick={() => navigate('/agents')}
              />
              {hasPausedAgents ? (
                <QuickActionButton
                  icon={Play}
                  label="Reanudar Todos"
                  color="green"
                  onClick={handleResumeAll}
                  disabled={actionLoading === 'resume'}
                />
              ) : (
                <QuickActionButton
                  icon={Pause}
                  label="Pausar Todos"
                  color="gray"
                  onClick={handlePauseAll}
                  disabled={!hasActiveAgents || actionLoading === 'pause'}
                />
              )}
              <QuickActionButton
                icon={ShieldAlert}
                label="Parada de Emergencia"
                color="red"
                onClick={() => setEmergencyDialogOpen(true)}
                disabled={!hasActiveAgents && !hasPausedAgents}
              />
            </div>
          </div>

          {/* Crypto Market */}
          <div style={{
            background: CARD_BG,
            borderRadius: 20,
            boxShadow: CARD_SHADOW,
            padding: 24
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
              <h2 style={{ fontSize: 16, fontWeight: 600, color: TEXT_PRIMARY, margin: 0 }}>
                Mercado Crypto
              </h2>
              <button
                onClick={() => navigate('/crypto')}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                  background: "none",
                  border: "none",
                  color: CORAL,
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: "pointer"
                }}
              >
                Ver todo <ChevronRight size={14} />
              </button>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12 }}>
              {cryptoData.map((coin) => (
                <div
                  key={coin.id}
                  onClick={() => navigate('/crypto')}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: 12,
                    borderRadius: 14,
                    background: "#FAFAFA",
                    border: "1px solid rgba(0,0,0,0.04)",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(217,119,87,0.2)"; e.currentTarget.style.background = CORAL_BG; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(0,0,0,0.04)"; e.currentTarget.style.background = "#FAFAFA"; }}
                >
                  <img src={coin.image} alt={coin.name} style={{ width: 28, height: 28, borderRadius: "50%" }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 13, fontWeight: 600, color: TEXT_PRIMARY, margin: 0 }}>{coin.symbol}</p>
                    <p style={{ fontSize: 11, color: TEXT_TERTIARY, margin: 0 }}>
                      €{coin.current_price?.toLocaleString()}
                    </p>
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: coin.price_change_24h >= 0 ? GREEN : RED }}>
                    {coin.price_change_24h >= 0 ? "+" : ""}{coin.price_change_24h?.toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Emergency Dialog */}
      <EmergencyDialog
        open={emergencyDialogOpen}
        onClose={() => setEmergencyDialogOpen(false)}
        onConfirm={handleEmergencyStop}
        loading={actionLoading === 'emergency'}
      />

      <style>{`
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.8); }
        }
        * { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #D1D1D6; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #C7C7CC; }
      `}</style>
    </div>
  );
}
