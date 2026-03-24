import { useState, useEffect, useCallback } from "react";
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
  Sparkles
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import { useNavigate } from "react-router-dom";
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

// ==================== METRIC CARD COMPONENT ====================
const MetricCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  color = "primary",
  subtitle,
  sparkline,
  size = "default" // default, small, large
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

  return (
    <Card className="glass border-white/10 card-hover metric-card h-full">
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
              {value}
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
    active: { color: "bg-primary/20 text-primary border-primary/30", label: "ACTIVE" },
    replicating: { color: "bg-cyber-green/20 text-cyber-green border-cyber-green/30", label: "REPLICATING" },
    dying: { color: "bg-destructive/20 text-destructive border-destructive/30", label: "DYING" },
    dead: { color: "bg-white/10 text-muted-foreground border-white/10", label: "DEAD" }
  };
  const config = statusConfig[status] || statusConfig.active;
  
  return (
    <span className={cn("px-2 py-0.5 text-[9px] font-mono font-semibold rounded-sm border", config.color)}>
      {config.label}
    </span>
  );
};

// ==================== MINI AGENT CARD ====================
const MiniAgentCard = ({ agent, onAction }) => {
  const finances = agent.finances || {};
  const performance = agent.performance || {};
  const balance = finances.current_balance ?? agent.balance ?? 0;
  const roi = performance.roi_percent ?? agent.roi ?? 0;
  const generation = agent.generation ?? 1;

  return (
    <div className={cn(
      "p-3 rounded-sm border border-white/10 hover:border-primary/30 transition-colors cursor-pointer group",
      agent.status === 'dying' && "border-destructive/30 bg-destructive/5",
      agent.status === 'replicating' && "border-cyber-green/30 bg-cyber-green/5"
    )}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Bot className="w-3.5 h-3.5 text-primary" />
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
          <span className="text-[10px] text-muted-foreground uppercase">Health</span>
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
        <p className="text-[10px] text-muted-foreground">${balance.toFixed(0)} balance</p>
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
  const [loading, setLoading] = useState(true);
  const [agentTab, setAgentTab] = useState("all");

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, agentsRes, cryptoRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/crypto/top-coins?limit=5`)
      ]);
      
      setStats(statsRes.data);
      setAgents(agentsRes.data.agents || []);
      setCryptoData(cryptoRes.data.coins || []);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Generate sparkline data
  const generateSparkline = (base, variance, trend = 0) => 
    Array.from({ length: 12 }, (_, i) => ({
      value: base + (Math.random() - 0.5) * variance + (i * trend)
    }));

  // Portfolio chart data
  const portfolioData = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    value: 1000 + Math.random() * 500 + (i * 20),
    agents: 800 + Math.random() * 400 + (i * 15)
  }));

  // Agent distribution for pie chart
  const agentDistribution = [
    { name: 'Active', value: stats?.agents?.active || 0, color: '#00F3FF' },
    { name: 'Replicating', value: stats?.agents?.replicating || 0, color: '#39FF14' },
    { name: 'Dying', value: stats?.agents?.dying || 0, color: '#FF003C' },
    { name: 'Dead', value: stats?.agents?.dead || 0, color: '#666666' }
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide uppercase">
            System Overview
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Real-time orchestrator metrics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-sm bg-cyber-green/10 border border-cyber-green/30">
            <Activity className="w-3.5 h-3.5 text-cyber-green animate-pulse" />
            <span className="text-[10px] font-mono text-cyber-green uppercase">Live</span>
          </div>
        </div>
      </div>

      {/* ==================== BENTO GRID ==================== */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-12 gap-4">
        
        {/* Row 1: Main Metrics */}
        <div className="col-span-2 lg:col-span-2 xl:col-span-2">
          <MetricCard
            title="Active Agents"
            value={stats?.agents?.active || 0}
            change={12.5}
            icon={Bot}
            color="primary"
            subtitle={`${stats?.agents?.total || 0} total`}
            sparkline={generateSparkline(3, 2, 0.1)}
          />
        </div>

        <div className="col-span-2 lg:col-span-2 xl:col-span-2">
          <MetricCard
            title="Total Balance"
            value={`$${(stats?.finances?.total_balance || 0).toFixed(0)}`}
            change={stats?.finances?.avg_roi || 0}
            icon={DollarSign}
            color="green"
            sparkline={generateSparkline(200, 50, 5)}
          />
        </div>

        <div className="col-span-1 lg:col-span-1 xl:col-span-2">
          <MetricCard
            title="Win Rate"
            value={`${((stats?.trading?.win_rate || 0) * 100).toFixed(0)}%`}
            icon={Target}
            color="primary"
            size="small"
          />
        </div>

        <div className="col-span-1 lg:col-span-1 xl:col-span-2">
          <MetricCard
            title="Total Trades"
            value={stats?.trading?.total_trades || 0}
            icon={Hash}
            color="purple"
            size="small"
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
          />
        </div>

        <div className="col-span-1 lg:col-span-1 xl:col-span-2">
          <MetricCard
            title="Tokens Used"
            value={`${((stats?.llm?.total_tokens || 0) / 1000).toFixed(1)}K`}
            icon={Cpu}
            color="yellow"
            size="small"
            subtitle={`~$${(stats?.llm?.cost_estimate || 0).toFixed(3)}`}
          />
        </div>

        {/* Row 2: Charts and Agents */}
        {/* Portfolio Chart - Large */}
        <Card className="glass border-white/10 col-span-2 md:col-span-4 lg:col-span-4 xl:col-span-8 row-span-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
                Portfolio Performance
              </CardTitle>
              <div className="flex gap-2">
                {['1D', '7D', '1M', 'ALL'].map((period) => (
                  <button
                    key={period}
                    className={cn(
                      "px-2 py-1 text-[10px] font-mono rounded-sm transition-colors",
                      period === '7D' ? "bg-primary/20 text-primary" : "text-muted-foreground hover:text-white"
                    )}
                  >
                    {period}
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
                      <stop offset="5%" stopColor="#00F3FF" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#00F3FF" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis 
                    dataKey="time" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#666', fontSize: 9 }}
                    interval={3}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#666', fontSize: 9 }}
                    tickFormatter={(v) => `$${v}`}
                    width={50}
                  />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(0,0,0,0.95)',
                      border: '1px solid rgba(0,243,255,0.3)',
                      borderRadius: '4px',
                      fontSize: '11px'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#00F3FF"
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
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center">
            <SystemHealthGauge health={systemHealth} />
            <div className="grid grid-cols-2 gap-4 mt-4 w-full">
              <div className="text-center">
                <p className="text-lg font-mono font-bold text-cyber-green">{stats?.agents?.replicating || 0}</p>
                <p className="text-[9px] text-muted-foreground uppercase">Replicating</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-mono font-bold text-destructive">{stats?.agents?.dying || 0}</p>
                <p className="text-[9px] text-muted-foreground uppercase">At Risk</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Agent Distribution Pie */}
        <Card className="glass border-white/10 col-span-2 md:col-span-2 lg:col-span-2 xl:col-span-4">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
              Agent Distribution
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
                Agents
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 text-[10px]"
                onClick={() => navigate('/agents')}
              >
                View All <ChevronRight className="w-3 h-3 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pb-3">
            <Tabs value={agentTab} onValueChange={setAgentTab} className="w-full">
              <TabsList className="w-full bg-white/5 mb-3">
                <TabsTrigger value="all" className="flex-1 text-[10px]">All</TabsTrigger>
                <TabsTrigger value="active" className="flex-1 text-[10px]">Active</TabsTrigger>
                <TabsTrigger value="best" className="flex-1 text-[10px]">Best</TabsTrigger>
                <TabsTrigger value="risk" className="flex-1 text-[10px]">At Risk</TabsTrigger>
              </TabsList>
              <TabsContent value={agentTab} className="mt-0">
                <div className="space-y-2 max-h-[200px] overflow-y-auto">
                  {filteredAgents.length > 0 ? (
                    filteredAgents.slice(0, 5).map((agent) => (
                      <MiniAgentCard key={agent.id} agent={agent} />
                    ))
                  ) : (
                    <div className="text-center py-6 text-muted-foreground">
                      <Bot className="w-6 h-6 mx-auto mb-2 opacity-50" />
                      <p className="text-xs">No agents found</p>
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
              Top Performers
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
                  <p className="text-xs">No data yet</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="glass border-white/10 col-span-2 md:col-span-2 lg:col-span-2 xl:col-span-4">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="grid grid-cols-3 gap-2">
              <QuickActionButton 
                icon={Bot} 
                label="Deploy" 
                color="primary"
                onClick={() => navigate('/agents')}
              />
              <QuickActionButton 
                icon={Pause} 
                label="Pause All" 
                color="yellow"
                onClick={() => {}}
              />
              <QuickActionButton 
                icon={AlertTriangle} 
                label="Emergency" 
                color="red"
                onClick={() => {}}
              />
            </div>
          </CardContent>
        </Card>

        {/* Crypto Market */}
        <Card className="glass border-white/10 col-span-2 md:col-span-4 lg:col-span-6 xl:col-span-8">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="font-heading text-xs tracking-wider uppercase text-muted-foreground">
                Crypto Market
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 text-[10px]"
                onClick={() => navigate('/crypto')}
              >
                View All <ChevronRight className="w-3 h-3 ml-1" />
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
