import { useState, useEffect } from "react";
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
  Copy
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MetricCard = ({ title, value, change, icon: Icon, trend, color = "primary" }) => {
  const isPositive = change >= 0;
  const colorClasses = {
    primary: "text-primary",
    green: "text-cyber-green",
    red: "text-destructive",
    purple: "text-secondary"
  };

  return (
    <Card className="glass border-white/10 card-hover metric-card">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-heading font-semibold tracking-wider text-muted-foreground uppercase">
              {title}
            </p>
            <p className={cn("text-3xl font-mono font-bold mt-2", colorClasses[color])}>
              {value}
            </p>
            {change !== undefined && (
              <div className={cn(
                "flex items-center gap-1 mt-2 text-xs font-mono",
                isPositive ? "text-cyber-green" : "text-destructive"
              )}>
                {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                <span>{isPositive ? "+" : ""}{change.toFixed(2)}%</span>
              </div>
            )}
          </div>
          <div className={cn(
            "p-3 rounded-sm",
            color === "primary" && "bg-primary/10",
            color === "green" && "bg-cyber-green/10",
            color === "red" && "bg-destructive/10",
            color === "purple" && "bg-secondary/10"
          )}>
            <Icon className={cn("w-5 h-5", colorClasses[color])} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const AgentStatusBadge = ({ status }) => {
  const statusConfig = {
    active: { color: "bg-primary/20 text-primary border-primary/30", label: "ACTIVE" },
    replicating: { color: "bg-cyber-green/20 text-cyber-green border-cyber-green/30", label: "REPLICATING" },
    dying: { color: "bg-destructive/20 text-destructive border-destructive/30", label: "DYING" },
    dead: { color: "bg-white/10 text-muted-foreground border-white/10", label: "DEAD" }
  };
  
  const config = statusConfig[status] || statusConfig.active;
  
  return (
    <span className={cn(
      "px-2 py-1 text-[10px] font-mono font-semibold rounded-sm border",
      config.color
    )}>
      {config.label}
    </span>
  );
};

const MiniAgentCard = ({ agent }) => {
  // Extract data from new schema structure
  const finances = agent.finances || {};
  const performance = agent.performance || {};
  
  const balance = finances.current_balance ?? agent.balance ?? 0;
  const roi = performance.roi_percent ?? agent.roi ?? 0;
  const generation = agent.generation ?? 1;

  const statusClass = {
    active: "status-active",
    replicating: "status-replicating",
    dying: "status-dying",
    dead: "status-dead",
    paused: "status-active",
    hibernating: "status-active"
  }[agent.status] || "";

  return (
    <div className={cn(
      "glass p-4 rounded-sm border border-white/10 card-hover",
      statusClass
    )}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-primary" />
          <span className="font-mono text-sm">{agent.name}</span>
          <span className="text-[10px] text-secondary">G{generation}</span>
        </div>
        <AgentStatusBadge status={agent.status} />
      </div>
      <div className="grid grid-cols-2 gap-4 text-xs">
        <div>
          <p className="text-muted-foreground mb-1">BALANCE</p>
          <p className="font-mono font-semibold">${balance.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-muted-foreground mb-1">ROI</p>
          <p className={cn(
            "font-mono font-semibold",
            roi >= 0 ? "text-cyber-green" : "text-destructive"
          )}>
            {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );
};

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [agents, setAgents] = useState([]);
  const [cryptoData, setCryptoData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
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
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Mock chart data
  const chartData = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    value: 1000 + Math.random() * 500 + (i * 20)
  }));

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-white/5 rounded-sm" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="dashboard-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide uppercase">
            System Overview
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time orchestrator metrics
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 rounded-sm bg-cyber-green/10 border border-cyber-green/30">
          <Activity className="w-4 h-4 text-cyber-green animate-pulse" />
          <span className="text-xs font-mono text-cyber-green">LIVE</span>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Agents"
          value={stats?.agents?.active || 0}
          change={12.5}
          icon={Bot}
          color="primary"
        />
        <MetricCard
          title="Total Balance"
          value={`$${(stats?.finances?.total_balance || 0).toFixed(2)}`}
          change={stats?.finances?.avg_roi || 0}
          icon={DollarSign}
          color="green"
        />
        <MetricCard
          title="Replicating"
          value={stats?.agents?.replicating || 0}
          icon={Copy}
          color="purple"
        />
        <MetricCard
          title="Terminated"
          value={stats?.agents?.dead || 0}
          icon={Skull}
          color="red"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio Chart */}
        <Card className="glass border-white/10 lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-sm tracking-wider uppercase text-muted-foreground">
              Portfolio Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00F3FF" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#00F3FF" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis 
                    dataKey="time" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#666', fontSize: 10 }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#666', fontSize: 10 }}
                    tickFormatter={(v) => `$${v}`}
                  />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(0,0,0,0.9)',
                      border: '1px solid rgba(0,243,255,0.3)',
                      borderRadius: '4px',
                      fontSize: '12px'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#00F3FF"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorValue)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Agent Status */}
        <Card className="glass border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-sm tracking-wider uppercase text-muted-foreground flex items-center justify-between">
              <span>Agent Status</span>
              <span className="text-xs text-primary">{agents.length} TOTAL</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 max-h-[340px] overflow-y-auto">
            {agents.length > 0 ? (
              agents.slice(0, 5).map((agent) => (
                <MiniAgentCard key={agent.id} agent={agent} />
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No agents deployed</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Crypto Ticker */}
      <Card className="glass border-white/10">
        <CardHeader className="pb-2">
          <CardTitle className="font-heading text-sm tracking-wider uppercase text-muted-foreground">
            Crypto Market
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {cryptoData.map((coin) => (
              <div 
                key={coin.id}
                className="flex items-center gap-3 p-3 rounded-sm bg-white/5 border border-white/10"
              >
                <img src={coin.image} alt={coin.name} className="w-8 h-8 rounded-full" />
                <div className="flex-1 min-w-0">
                  <p className="font-mono text-sm font-semibold truncate">{coin.symbol}</p>
                  <p className="font-mono text-xs text-muted-foreground">
                    ${coin.current_price?.toLocaleString()}
                  </p>
                </div>
                <div className={cn(
                  "text-xs font-mono",
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
  );
}
