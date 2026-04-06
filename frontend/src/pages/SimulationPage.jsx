import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Zap, Play, Square, RotateCcw, Activity, TrendingUp, TrendingDown,
  Bot, Skull, Copy, Clock, DollarSign, Target, BarChart3
} from "lucide-react";
import { toast } from "sonner";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";
import { simulationAPI, dashboardAPI } from "@/lib/api";
import { useAppMode } from "@/hooks/useAppMode";

const GREEN = "#00FF88";
const RED = "#FF003C";
const CYAN = "#00F3FF";

const formatUptime = (seconds) => {
  if (!seconds || seconds < 0) return "0m";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
};

/* ── Metric Card ── */
function SimMetric({ icon: Icon, label, value, color = "text-foreground", sub }) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card rounded-xl p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-9 h-9 rounded-lg bg-cyan-500/10 flex items-center justify-center">
          <Icon size={18} className="text-cyan-400" />
        </div>
        <span className="evo-section-title">{label}</span>
      </div>
      <p className={`text-2xl font-bold font-mono tracking-tight ${color}`}>{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </motion.div>
  );
}

/* ── Main Page ── */
export default function SimulationPage() {
  const { setMode, isSimulation } = useAppMode();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [capital, setCapital] = useState(1000);
  const [numAgents, setNumAgents] = useState(3);
  const [portfolioData, setPortfolioData] = useState([]);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await simulationAPI.status();
      setStatus(res.data);

      // Build portfolio history data point
      if (res.data.active && res.data.total_balance != null) {
        setPortfolioData(prev => {
          const newPoint = {
            time: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
            balance: res.data.total_balance,
            pnl: res.data.total_pnl,
          };
          const updated = [...prev, newPoint];
          return updated.slice(-60); // keep last 60 data points
        });
      }
    } catch {
      // Silently fail — simulation might not be started yet
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const handleStart = async () => {
    setActionLoading(true);
    try {
      const res = await simulationAPI.start(capital, numAgents);
      toast.success(res.data.message);
      setMode("simulation");
      setPortfolioData([]);
      await fetchStatus();
    } catch (err) {
      toast.error(err?.message || "Error al iniciar simulación");
    } finally { setActionLoading(false); }
  };

  const handleStop = async () => {
    setActionLoading(true);
    try {
      const res = await simulationAPI.stop();
      toast.success(res.data.message);
      await fetchStatus();
    } catch (err) {
      toast.error(err?.message || "Error al detener simulación");
    } finally { setActionLoading(false); }
  };

  const handleReset = async () => {
    setActionLoading(true);
    try {
      const res = await simulationAPI.reset(capital, numAgents);
      toast.success(res.data.message);
      setPortfolioData([]);
      await fetchStatus();
    } catch (err) {
      toast.error(err?.message || "Error al reiniciar simulación");
    } finally { setActionLoading(false); }
  };

  const isActive = status?.active || false;
  const pnlColor = (status?.total_pnl || 0) >= 0 ? GREEN : RED;

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center gap-3 text-muted-foreground">
          <RotateCcw className="w-5 h-5 animate-spin" />
          <span>Cargando simulación...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-[1400px] mx-auto px-4 lg:px-6 py-8 space-y-6">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl font-bold uppercase tracking-wide text-foreground flex items-center gap-3">
              <Zap className="text-cyan-400" size={28} />
              Modo Simulación
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Paper Trading con datos reales de Binance — sin riesgo
            </p>
          </div>

          {/* Status Badge */}
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
            isActive
              ? "bg-green-500/10 border-green-500/20"
              : "bg-white/5 border-white/10"
          }`}>
            <div className={`w-2.5 h-2.5 rounded-full ${isActive ? "bg-green-500 animate-pulse" : "bg-muted"}`} />
            <span className={`text-sm font-medium ${isActive ? "text-green-400" : "text-muted-foreground"}`}>
              {isActive ? "SIMULACIÓN ACTIVA" : "INACTIVA"}
            </span>
          </div>
        </motion.div>

        {/* Active Banner */}
        {isActive && (
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}
            className="glass-card rounded-xl p-5 border-l-4 border-l-green-500">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-foreground">
                  ⚡ Simulación en curso — {status?.num_agents} agentes operando con datos reales
                </p>
                <p className="text-xs text-muted-foreground mt-1 font-mono">
                  Iniciada: {status?.started_at ? new Date(status.started_at).toLocaleString('es-ES') : '—'}
                  {' · '}Uptime: {formatUptime(status?.uptime_seconds)}
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold font-mono" style={{ color: pnlColor }}>
                  {status?.total_pnl >= 0 ? "+" : ""}€{status?.total_pnl?.toFixed(2) || "0.00"}
                </p>
                <p className="text-xs font-mono" style={{ color: pnlColor }}>
                  {status?.pnl_percent >= 0 ? "+" : ""}{status?.pnl_percent?.toFixed(2) || "0.00"}%
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Configuration Panel */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="glass-card rounded-xl p-6">
          <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
            <BarChart3 size={18} className="text-cyan-400" />
            Configuración
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div>
              <label className="evo-section-title block mb-2">Capital por agente (€)</label>
              <input type="number" min="50" step="50" value={capital}
                onChange={(e) => setCapital(parseFloat(e.target.value) || 100)}
                className="evo-input text-center font-mono" disabled={isActive}
                aria-label="Capital por agente" />
            </div>
            <div>
              <label className="evo-section-title block mb-2">Nº de agentes</label>
              <input type="number" min="1" max="10" value={numAgents}
                onChange={(e) => setNumAgents(parseInt(e.target.value) || 3)}
                className="evo-input text-center font-mono" disabled={isActive}
                aria-label="Número de agentes" />
            </div>
            <div>
              <label className="evo-section-title block mb-2">Capital total</label>
              <p className="evo-metric-value !text-xl font-mono text-cyan-400">
                €{(capital * numAgents).toLocaleString()}
              </p>
            </div>
          </div>

          <div className="flex gap-2.5">
            {!isActive ? (
              <button onClick={handleStart} disabled={actionLoading}
                className="evo-button-primary px-6 py-2.5 text-sm flex items-center gap-2 disabled:opacity-50">
                <Play size={16} /> Iniciar Simulación
              </button>
            ) : (
              <>
                <button onClick={handleStop} disabled={actionLoading}
                  className="evo-button-destructive px-6 py-2.5 text-sm flex items-center gap-2 disabled:opacity-50">
                  <Square size={16} /> Detener
                </button>
                <button onClick={handleReset} disabled={actionLoading}
                  className="evo-button-outline px-6 py-2.5 text-sm flex items-center gap-2 disabled:opacity-50">
                  <RotateCcw size={16} /> Reiniciar
                </button>
              </>
            )}
          </div>
        </motion.div>

        {/* Live Metrics */}
        {isActive && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <SimMetric icon={DollarSign} label="Balance Total" value={`€${(status?.total_balance || 0).toFixed(2)}`} sub={`Inicial: €${(status?.initial_total_capital || 0).toFixed(0)}`} />
            <SimMetric icon={status?.total_pnl >= 0 ? TrendingUp : TrendingDown} label="PnL Total" value={`€${(status?.total_pnl || 0).toFixed(2)}`} color={pnlColor} sub={`${(status?.pnl_percent || 0).toFixed(1)}%`} />
            <SimMetric icon={Activity} label="Win Rate" value={`${status?.win_rate || 0}%`} color={(status?.win_rate || 0) >= 50 ? GREEN : RED} sub={`${status?.total_trades || 0} trades`} />
            <SimMetric icon={Bot} label="Agentes Activos" value={status?.active_agents || 0} sub={`De ${status?.num_agents || 0} iniciales`} />
            <SimMetric icon={Copy} label="Replicaciones" value={status?.replications || 0} color={GREEN} />
            <SimMetric icon={Skull} label="Muertes" value={status?.dead_agents || 0} color={RED} />
          </div>
        )}

        {/* Portfolio Chart */}
        {isActive && portfolioData.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="glass-card rounded-xl p-6">
            <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
              <Target size={18} className="text-cyan-400" />
              Rendimiento en Vivo
            </h2>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={portfolioData}>
                  <defs>
                    <linearGradient id="simGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={CYAN} stopOpacity={0.15} />
                      <stop offset="95%" stopColor={CYAN} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: "#6B7280", fontSize: 11 }} interval="preserveStartEnd" />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: "#6B7280", fontSize: 11 }} tickFormatter={(v) => `€${v.toFixed(0)}`} domain={['auto', 'auto']} />
                  <Tooltip contentStyle={{ background: "hsl(240 10% 6%)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10, boxShadow: "0 8px 24px rgba(0,0,0,0.4)", fontSize: 12 }} formatter={(value) => [`€${value.toFixed(2)}`, 'Balance']} />
                  <Area type="monotone" dataKey="balance" stroke={CYAN} strokeWidth={2} fillOpacity={1} fill="url(#simGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        )}

        {/* Not Active State */}
        {!isActive && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
            className="glass-card rounded-xl text-center py-20 px-6">
            <div className="w-20 h-20 rounded-xl bg-cyan-500/10 flex items-center justify-center mx-auto mb-6">
              <Zap className="w-10 h-10 text-cyan-400" />
            </div>
            <h3 className="text-xl font-semibold text-foreground mb-2">Simulación Lista</h3>
            <p className="text-muted-foreground max-w-md mx-auto mb-2">
              Configura el capital y número de agentes, luego pulsa <strong>Iniciar Simulación</strong>.
            </p>
            <p className="text-xs text-muted-foreground max-w-md mx-auto">
              Los agentes operarán 24/7 con datos reales de Binance, usando las 3 estrategias de trading.
              Se autorreplicarán con ROI &gt; 50% y morirán al llegar a €0.
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
