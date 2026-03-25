import { useState, useEffect, useCallback, useRef } from "react";
import { 
  Bot, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  Zap,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Skull,
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
  Sparkles,
  OctagonX,
  PartyPopper
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { cn } from "@/lib/utils";
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
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
  Legend
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ==================== ANIMATED NUMBER COMPONENT ====================
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
      
      // Easing function (ease-out-cubic)
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
    <span className="tabular-nums">
      {prefix}{displayValue.toFixed(decimals)}{suffix}
    </span>
  );
};

// ==================== CONFETTI COMPONENT ====================
const Confetti = ({ active }) => {
  if (!active) return null;
  
  const particles = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    delay: Math.random() * 0.5,
    color: ['#00F3FF', '#39FF14', '#FF003C', '#FAFF00', '#BC13FE'][Math.floor(Math.random() * 5)]
  }));
  
  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute w-2 h-2 rounded-full animate-confetti"
          style={{
            left: `${p.x}%`,
            backgroundColor: p.color,
            animationDelay: `${p.delay}s`,
            boxShadow: `0 0 6px ${p.color}`
          }}
        />
      ))}
    </div>
  );
};

// ==================== METRIC CARD COMPONENT ====================
const MetricCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  color = "primary",
  subtitle,
  sparkline,
  size = "default", // default, small, large
  animate = false,
  isShaking = false
}) => {
  const colorClasses = {
    primary: "text-primary",
    green: "text-cyber-green",
    red: "text-destructive",
    purple: "text-secondary",
    yellow: "text-yellow-400"
  };

  const bgClasses = {
    primary: "bg-primary/10",
    green: "bg-cyber-green/10",
    red: "bg-destructive/10",
    purple: "bg-secondary/10",
    yellow: "bg-yellow-400/10"
  };

  const isPositive = change >= 0;

  // Parse numeric value for animation
  const numericValue = typeof value === 'string' 
    ? parseFloat(value.replace(/[^0-9.-]/g, '')) || 0 
    : value;
  const prefix = typeof value === 'string' && value.startsWith('$') ? '$' : '';
  const suffix = typeof value === 'string' && value.endsWith('%') ? '%' : 
                 typeof value === 'string' && value.endsWith('K') ? 'K' : '';

  return (
    <Card className={cn(
      "glass border-white/10 card-hover metric-card h-full transition-all",
      isShaking && "animate-shake"
    )}>
      <CardContent className={cn("p-4", size === "small" && "p-3")}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-[10px] font-heading font-semibold tracking-wider text-muted-foreground uppercase">
              {title}
            </p>
            <p className={cn(
              "font-mono font-bold mt-1",
              size === "large" ? "text-4xl" : size === "small" ? "text-xl" : "text-2xl",
              colorClasses[color]
            )}>
              {animate ? (
                <AnimatedNumber 
                  value={numericValue} 
                  prefix={prefix} 
                  suffix={suffix}
                  decimals={suffix === 'K' ? 1 : 0}
                />
              ) : value}
            </p>
            {change !== undefined && (
              <div className={cn(
                "flex items-center gap-1 mt-1 text-xs font-mono",
                isPositive ? "text-cyber-green" : "text-destructive"
              )}>
                {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                <span>{isPositive ? "+" : ""}{typeof change === 'number' ? change.toFixed(2) : change}%</span>
              </div>
            )}
            {subtitle && (
              <p className="text-[10px] text-muted-foreground mt-1">{subtitle}</p>
            )}
          </div>
          <div className={cn("p-2 rounded-sm", bgClasses[color])}>
            <Icon className={cn(
              size === "small" ? "w-4 h-4" : "w-5 h-5",
              colorClasses[color]
            )} />
          </div>
        </div>
        {sparkline && (
          <div className="h-8 mt-2 -mx-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sparkline}>
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke={color === 'green' ? '#39FF14' : '#00F3FF'} 
                  fill={color === 'green' ? 'rgba(57,255,20,0.2)' : 'rgba(0,243,255,0.2)'} 
                  strokeWidth={1.5}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ==================== AGENT STATUS BADGE ====================
const AgentStatusBadge = ({ status }) => {
  const statusConfig = {
    active: { color: "bg-primary/20 text-primary border-primary/30", label: "ACTIVO" },
    paused: { color: "bg-yellow-400/20 text-yellow-400 border-yellow-400/30", label: "PAUSADO" },
    replicating: { color: "bg-cyber-green/20 text-cyber-green border-cyber-green/30", label: "REPLICANDO" },
    dying: { color: "bg-destructive/20 text-destructive border-destructive/30", label: "MURIENDO" },
    dead: { color: "bg-white/10 text-muted-foreground border-white/10", label: "MUERTO" }
  };
  const config = statusConfig[status] || statusConfig.active;
  
  return (
    <span className={cn("px-2 py-0.5 text-[9px] font-mono font-semibold rounded-sm border", config.color)}>
      {config.label}
    </span>
  );
};

// ==================== MINI AGENT CARD ====================
const MiniAgentCard = ({ agent, onAction, isShaking = false }) => {
  const finances = agent.finances || {};
  const performance = agent.performance || {};
  const balance = finances.current_balance ?? agent.balance ?? 0;
  const roi = performance.roi_percent ?? agent.roi ?? 0;
  const generation = agent.generation ?? 1;

  return (
    <div className={cn(
      "p-3 rounded-sm border border-white/10 hover:border-primary/30 transition-all cursor-pointer group",
      agent.status === 'dying' && "border-destructive/30 bg-destructive/5 animate-shake",
      agent.status === 'replicating' && "border-cyber-green/30 bg-cyber-green/5 animate-pulse-slow",
      isShaking && "animate-shake"
    )}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Bot className={cn(
            "w-3.5 h-3.5 text-primary",
            agent.status === 'replicating' && "animate-bounce"
          )} />
          <span className="font-mono text-xs truncate max-w-[100px]">{agent.name}</span>
          <span className="text-[9px] text-secondary font-mono">G{generation}</span>
        </div>
        <AgentStatusBadge status={agent.status} />
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="font-mono">${balance.toFixed(0)}</span>
        <span className={cn(
          "font-mono",
          roi >= 0 ? "text-cyber-green" : "text-destructive"
        )}>
          {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
        </span>
      </div>
    </div>
  );
};

// ==================== QUICK ACTION BUTTON ====================
const QuickActionButton = ({ icon: Icon, label, onClick, color = "primary", disabled }) => {
  const colorClasses = {
    primary: "hover:bg-primary/20 hover:border-primary/50 hover:text-primary",
    green: "hover:bg-cyber-green/20 hover:border-cyber-green/50 hover:text-cyber-green",
    red: "hover:bg-destructive/20 hover:border-destructive/50 hover:text-destructive",
    yellow: "hover:bg-yellow-400/20 hover:border-yellow-400/50 hover:text-yellow-400"
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "flex flex-col items-center gap-2 p-4 rounded-sm border border-white/10 bg-white/5",
        "transition-all duration-200",
        colorClasses[color],
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <Icon className="w-5 h-5" />
      <span className="text-[10px] font-heading uppercase tracking-wider">{label}</span>
    </button>
  );
};

// ==================== SYSTEM HEALTH GAUGE ====================
const SystemHealthGauge = ({ health = 95 }) => {
  const getColor = (value) => {
    if (value >= 80) return "#39FF14";
    if (value >= 50) return "#FAFF00";
    return "#FF003C";
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke={getColor(health)}
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${(health / 100) * 352} 352`}
            strokeLinecap="round"
            style={{
              filter: `drop-shadow(0 0 10px ${getColor(health)})`
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-mono font-bold" style={{ color: getColor(health) }}>
            {health}%
          </span>
          <span className="text-[10px] text-muted-foreground uppercase">Salud</span>
        </div>
      </div>
    </div>
  );
};

// ==================== TOP PERFORMER CARD ====================
const TopPerformerCard = ({ agent, rank }) => {
  const roi = agent.roi ?? agent.performance?.roi_percent ?? 0;
  const balance = agent.balance ?? agent.finances?.current_balance ?? 0;
  
  return (
    <div className="flex items-center gap-3 p-3 rounded-sm bg-white/5 border border-white/10">
      <div className={cn(
        "w-8 h-8 rounded-sm flex items-center justify-center font-mono font-bold text-sm",
        rank === 1 && "bg-yellow-400/20 text-yellow-400",
        rank === 2 && "bg-gray-400/20 text-gray-400",
        rank === 3 && "bg-amber-600/20 text-amber-600",
        rank > 3 && "bg-white/10 text-muted-foreground"
      )}>
        #{rank}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-mono text-sm truncate">{agent.name}</p>
        <p className="text-[10px] text-muted-foreground">${balance.toFixed(0)} saldo</p>
      </div>
      <div className={cn(
        "font-mono font-bold",
        roi >= 0 ? "text-cyber-green" : "text-destructive"
      )}>
        {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
      </div>
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
      
      // Check for new replications to trigger confetti
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

  // ==================== BULK ACTIONS ====================
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

  // Check if there are paused agents
  const hasPausedAgents = agents.some(a => a.status === 'paused');
  const hasActiveAgents = agents.some(a => a.status === 'active' || a.status === 'replicating');
  const hasDyingAgents = agents.some(a => a.status === 'dying');

  // Generate sparkline data
  const generateSparkline = (base, variance, trend = 0) => 
    Array.from({ length: 12 }, (_, i) => ({
      value: base + (Math.random() - 0.5) * variance + (i * trend)
    }));

  // Agent distribution for pie chart
  const agentDistribution = [
    { name: 'Activos', value: stats?.agents?.active || 0, color: '#00F3FF' },
    { name: 'Replicando', value: stats?.agents?.replicating || 0, color: '#39FF14' },
    { name: 'Muriendo', value: stats?.agents?.dying || 0, color: '#FF003C' },
    { name: 'Muertos', value: stats?.agents?.dead || 0, color: '#666666' }
  ].filter(d => d.value > 0);

  // Filter agents by tab
  const filteredAgents = agents.filter(agent => {
    if (agentTab === 'all') return true;
    if (agentTab === 'active') return agent.status === 'active';
    if (agentTab === 'best') return (agent.performance?.roi_percent ?? agent.roi ?? 0) > 0;
    if (agentTab === 'risk') return agent.status === 'dying' || (agent.finances?.current_balance ?? agent.balance ?? 0) < 20;
    return true;
  });

  // Top performers
  const topPerformers = [...agents]
    .sort((a, b) => (b.performance?.roi_percent ?? b.roi ?? 0) - (a.performance?.roi_percent ?? a.roi ?? 0))
    .slice(0, 5);

  // Calculate system health
  const systemHealth = stats ? Math.round(
    ((stats.agents?.active || 0) / Math.max(stats.agents?.total || 1, 1)) * 100
  ) : 95;

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-24 bg-white/5 rounded-sm animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 h-80 bg-white/5 rounded-sm animate-pulse" />
          <div className="h-80 bg-white/5 rounded-sm animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="dashboard-page">
      {/* Confetti for replication celebrations */}
      <Confetti active={showConfetti} />
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide uppercase">
            Vista General
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Métricas del orquestador en tiempo real
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-sm bg-cyber-green/10 border border-cyber-green/30">
            <Activity className="w-3.5 h-3.5 text-cyber-green animate-pulse" />
            <span className="text-[10px] font-mono text-cyber-green uppercase">EN VIVO</span>
          </div>
        </div>
      </div>

      {/* ==================== BENTO GRID ==================== */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-12 gap-4">
        
        {/* Row 1: Main Metrics */}
        <div className="col-span-2 lg:col-span-2 xl:col-span-2">
          <MetricCard
            title="Agentes Activos"
            value={stats?.agents?.active || 0}
            change={12.5}
            icon={Bot}
            color="primary"
            subtitle={`${stats?.agents?.total || 0} en total`}
            sparkline={generateSparkline(3, 2, 0.1)}
            animate
          />
        </div>

        <div className="col-span-2 lg:col-span-2 xl:col-span-2">
          <MetricCard
            title="Balance Total"
            value={`$${(stats?.finances?.total_balance || 0).toFixed(0)}`}
            change={stats?.finances?.avg_roi || 0}
            icon={DollarSign}
            color="green"
            sparkline={generateSparkline(200, 50, 5)}
            animate
          />
        </div>

        <div className="col-span-1 lg:col-span-1 xl:col-span-2">
          <MetricCard
            title="Tasa de Éxito"
            value={`${((stats?.trading?.win_rate || 0) * 100).toFixed(0)}%`}
            icon={Target}
            color="primary"
            size="small"
            animate
          />
        </div>

        <div className="col-span-1 lg:col-span-1 xl:col-span-2">
          <MetricCard
            title="Total Trades"
            value={stats?.trading?.total_trades || 0}
            icon={Hash}
            color="purple"
            size="small"
            animate
          />
        </div>

        <div className="col-span-1 lg:col-span-1 xl:col-span-2">
          <MetricCard
            title="PnL 24h"
            value={`$${(stats?.trading?.pnl_24h || 0).toFixed(0)}`}
            change={(stats?.trading?.pnl_24h || 0) > 0 ? 5.2 : -3.1}
            icon={TrendingUp}
            color={(stats?.trading?.pnl_24h || 0) >= 0 ? "green" : "red"}
            size="small"
            animate
          />
        </div>

        <div className="col-span-1 lg:col-span-1 xl:col-span-2">
          <MetricCard
            title="Tokens Usados"
            value={`${((stats?.llm?.total_tokens || 0) / 1000).toFixed(1)}K`}
            icon={Cpu}
            color="yellow"
            size="small"
            subtitle={`~$${(stats?.llm?.cost_estimate || 0).toFixed(3)}`}
            animate
          />
        </div>

        {/* Row 2: Charts and Agents */}
        {/* Portfolio Chart - Large */}
        <Card className="glass border-white/10 col-span-2 md:col-span-4 lg:col-span-4 xl:col-span-8 row-span-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
                  Rendimiento del Portfolio
                </CardTitle>
                {portfolioStats && (
                  <span className={cn(
                    "text-xs font-mono",
                    portfolioStats.totalPnl >= 0 ? "text-cyber-green" : "text-destructive"
                  )}>
                    {portfolioStats.totalPnl >= 0 ? "+" : ""}${portfolioStats.totalPnl.toFixed(2)} ({portfolioStats.pnlPercent.toFixed(1)}%)
                  </span>
                )}
              </div>
              <div className="flex gap-1">
                {['1d', '7d', '1m', 'all'].map((period) => (
                  <button
                    key={period}
                    onClick={() => setPortfolioPeriod(period)}
                    className={cn(
                      "px-2 py-1 text-[10px] font-mono rounded-sm transition-colors uppercase",
                      period === portfolioPeriod ? "bg-primary/20 text-primary" : "text-muted-foreground hover:text-white"
                    )}
                  >
                    {period === '1d' ? '1D' : period === '7d' ? '7D' : period === '1m' ? '1M' : 'TODO'}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="pb-4">
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={portfolioData}>
                  <defs>
                    <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={portfolioStats?.totalPnl >= 0 ? "#39FF14" : "#FF003C"} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={portfolioStats?.totalPnl >= 0 ? "#39FF14" : "#FF003C"} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis 
                    dataKey="time" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#666', fontSize: 9 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#666', fontSize: 9 }}
                    tickFormatter={(v) => `$${v.toFixed(0)}`}
                    width={50}
                    domain={['dataMin - 10', 'dataMax + 10']}
                  />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(0,0,0,0.95)',
                      border: '1px solid rgba(0,243,255,0.3)',
                      borderRadius: '4px',
                      fontSize: '11px'
                    }}
                    formatter={(value) => [`$${value.toFixed(2)}`, 'Valor del Portfolio']}
                    labelFormatter={(label) => `Hora: ${label}`}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke={portfolioStats?.totalPnl >= 0 ? "#39FF14" : "#FF003C"}
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorPortfolio)"
                    name="Portfolio"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* System Health Gauge */}
        <Card className="glass border-white/10 col-span-2 md:col-span-2 lg:col-span-2 xl:col-span-4">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
              Salud del Sistema
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center">
            <SystemHealthGauge health={systemHealth} />
            <div className="grid grid-cols-2 gap-4 mt-4 w-full">
              <div className="text-center">
                <p className={cn(
                  "text-lg font-mono font-bold text-cyber-green",
                  (stats?.agents?.replicating || 0) > 0 && "animate-pulse"
                )}>{stats?.agents?.replicating || 0}</p>
                <p className="text-[9px] text-muted-foreground uppercase">Replicando</p>
              </div>
              <div className="text-center">
                <p className={cn(
                  "text-lg font-mono font-bold text-destructive",
                  (stats?.agents?.dying || 0) > 0 && "animate-pulse"
                )}>{stats?.agents?.dying || 0}</p>
                <p className="text-[9px] text-muted-foreground uppercase">En Riesgo</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Agent Distribution Pie */}
        <Card className="glass border-white/10 col-span-2 md:col-span-2 lg:col-span-2 xl:col-span-4">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
              Distribución de Agentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[160px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={agentDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={60}
                    dataKey="value"
                    strokeWidth={0}
                  >
                    {agentDistribution.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(0,0,0,0.95)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '4px',
                      fontSize: '11px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-2">
              {agentDistribution.map((item) => (
                <div key={item.name} className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-[9px] text-muted-foreground">{item.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Agent Status Panel */}
        <Card className="glass border-white/10 col-span-2 md:col-span-4 lg:col-span-3 xl:col-span-4">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
                Agentes
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 text-[10px]"
                onClick={() => navigate('/agents')}
              >
                Ver Todos <ChevronRight className="w-3 h-3 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pb-3">
            <Tabs value={agentTab} onValueChange={setAgentTab} className="w-full">
              <TabsList className="w-full bg-white/5 mb-3">
                <TabsTrigger value="all" className="flex-1 text-[10px]">Todos</TabsTrigger>
                <TabsTrigger value="active" className="flex-1 text-[10px]">Activos</TabsTrigger>
                <TabsTrigger value="best" className="flex-1 text-[10px]">Mejores</TabsTrigger>
                <TabsTrigger value="risk" className="flex-1 text-[10px]">En Riesgo</TabsTrigger>
              </TabsList>
              <TabsContent value={agentTab} className="mt-0">
                <div className="space-y-2 max-h-[200px] overflow-y-auto">
                  {filteredAgents.length > 0 ? (
                    filteredAgents.slice(0, 5).map((agent) => (
                      <MiniAgentCard key={agent.id} agent={agent} isShaking={agent.status === 'dying'} />
                    ))
                  ) : (
                    <div className="text-center py-6 text-muted-foreground">
                      <Bot className="w-6 h-6 mx-auto mb-2 opacity-50" />
                      <p className="text-xs">No se encontraron agentes</p>
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Top Performers */}
        <Card className="glass border-white/10 col-span-2 md:col-span-4 lg:col-span-3 xl:col-span-4">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground flex items-center gap-2">
              <Trophy className="w-3.5 h-3.5 text-yellow-400" />
              Mejores Rendimientos
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="space-y-2 max-h-[240px] overflow-y-auto">
              {topPerformers.length > 0 ? (
                topPerformers.map((agent, index) => (
                  <TopPerformerCard key={agent.id} agent={agent} rank={index + 1} />
                ))
              ) : (
                <div className="text-center py-6 text-muted-foreground">
                  <Trophy className="w-6 h-6 mx-auto mb-2 opacity-50" />
                  <p className="text-xs">Sin datos aún</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="glass border-white/10 col-span-2 md:col-span-2 lg:col-span-2 xl:col-span-4">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
              Acciones Rápidas
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="grid grid-cols-3 gap-2">
              <QuickActionButton 
                icon={Bot} 
                label="Desplegar" 
                color="primary"
                onClick={() => navigate('/agents')}
              />
              {hasPausedAgents ? (
                <QuickActionButton 
                  icon={Play} 
                  label="Reanudar" 
                  color="green"
                  onClick={handleResumeAll}
                  disabled={actionLoading === 'resume'}
                />
              ) : (
                <QuickActionButton 
                  icon={Pause} 
                  label="Pausar" 
                  color="yellow"
                  onClick={handlePauseAll}
                  disabled={!hasActiveAgents || actionLoading === 'pause'}
                />
              )}
              <QuickActionButton 
                icon={OctagonX} 
                label="Emergencia" 
                color="red"
                onClick={() => setEmergencyDialogOpen(true)}
                disabled={!hasActiveAgents && !hasPausedAgents}
              />
            </div>
          </CardContent>
        </Card>

        {/* Emergency Stop Dialog */}
        <AlertDialog open={emergencyDialogOpen} onOpenChange={setEmergencyDialogOpen}>
          <AlertDialogContent className="glass border-destructive/50">
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="w-5 h-5" />
                Parada de Emergencia
              </AlertDialogTitle>
              <AlertDialogDescription className="space-y-2">
                <p>Esta acción <strong className="text-destructive">TERMINARÁ TODOS LOS AGENTES</strong> inmediatamente.</p>
                <p className="text-sm">• Todos los agentes activos y pausados serán eliminados</p>
                <p className="text-sm">• Los saldos de los agentes se establecerán en $0</p>
                <p className="text-sm">• Esta acción <strong>NO se puede deshacer</strong></p>
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="border-white/20">Cancelar</AlertDialogCancel>
              <AlertDialogAction 
                onClick={handleEmergencyStop}
                className="bg-destructive hover:bg-destructive/90"
                disabled={actionLoading === 'emergency'}
              >
                {actionLoading === 'emergency' ? (
                  <span className="flex items-center gap-2">
                    <RotateCcw className="w-4 h-4 animate-spin" />
                    Deteniendo...
                  </span>
                ) : (
                  "Confirmar Parada"
                )}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* Crypto Market */}
        <Card className="glass border-white/10 col-span-2 md:col-span-4 lg:col-span-6 xl:col-span-8">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
                Mercado Crypto
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 text-[10px]"
                onClick={() => navigate('/crypto')}
              >
                Ver Todo <ChevronRight className="w-3 h-3 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              {cryptoData.map((coin) => (
                <div 
                  key={coin.id}
                  className="flex items-center gap-2 p-2.5 rounded-sm bg-white/5 border border-white/10 hover:border-primary/30 transition-colors cursor-pointer"
                  onClick={() => navigate('/crypto')}
                >
                  <img src={coin.image} alt={coin.name} className="w-6 h-6 rounded-full" />
                  <div className="flex-1 min-w-0">
                    <p className="font-mono text-xs font-semibold">{coin.symbol}</p>
                    <p className="font-mono text-[10px] text-muted-foreground">
                      ${coin.current_price?.toLocaleString()}
                    </p>
                  </div>
                  <div className={cn(
                    "text-[10px] font-mono",
                    coin.price_change_24h >= 0 ? "text-cyber-green" : "text-destructive"
                  )}>
                    {coin.price_change_24h >= 0 ? "+" : ""}
                    {coin.price_change_24h?.toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
