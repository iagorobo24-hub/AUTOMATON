import { useCallback, useEffect, useState } from "react";
import { Activity, Database, RefreshCw, ShieldAlert } from "lucide-react";
import { evolutionAPI, healthAPI, riskAPI } from "@/lib/api";

function StatusCard({ label, value, description, active }) {
  return (
    <div className="glass-card rounded-xl p-5">
      <div className="flex items-center justify-between gap-4 mb-2">
        <p className="text-xs uppercase tracking-wider text-muted-foreground">{label}</p>
        <span className={`w-2.5 h-2.5 rounded-full ${active ? "bg-green-500" : "bg-gray-500"}`} aria-hidden="true" />
      </div>
      <p className="text-lg font-semibold text-foreground">{value}</p>
      {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
    </div>
  );
}

function RuntimeRow({ label, value, description }) {
  return (
    <div className="flex items-start justify-between gap-6 py-4 border-b border-white/5 last:border-0">
      <div>
        <p className="text-sm font-medium text-foreground">{label}</p>
        {description && <p className="text-xs text-muted-foreground mt-1 max-w-xl">{description}</p>}
      </div>
      <span className="text-sm font-mono text-cyan-400 shrink-0">{value}</span>
    </div>
  );
}

export default function SettingsPage() {
  const [runtime, setRuntime] = useState(null);
  const [riskProfile, setRiskProfile] = useState(null);
  const [evolutionPolicy, setEvolutionPolicy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRuntime = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthResponse, riskResponse, evolutionResponse] = await Promise.all([
        healthAPI.health(), riskAPI.activeProfile(), evolutionAPI.activePolicy(),
      ]);
      setRuntime(healthResponse.data);
      setRiskProfile(riskResponse.data);
      setEvolutionPolicy(evolutionResponse.data);
    } catch (err) {
      setRuntime(null); setRiskProfile(null); setEvolutionPolicy(null);
      setError(err?.message || "No se pudo consultar el runtime");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchRuntime(); }, [fetchRuntime]);

  const apiOperational = runtime?.status === "ok";
  const syntheticDisabled = runtime?.synthetic_engine === "disabled";
  const backtestingReady = runtime?.backtesting === "evidence_phase_5";
  const evolutionReady = runtime?.agent_evolution === "evidence_phase_6";
  const runtimeLabel = loading ? "Consultando…" : !runtime ? "Desconocido" : syntheticDisabled ? "Sintético desactivado" : "Revisar configuración";

  return (
    <div className="min-h-screen bg-background" data-testid="settings-page">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        <div className="flex items-center justify-between gap-4"><div><h1 className="font-heading text-3xl font-bold tracking-wide text-foreground uppercase">Configuración</h1><p className="text-sm text-muted-foreground mt-1">Paper con Risk, Backtesting reproducible y evolución de agentes basada en evidencia</p></div><button onClick={fetchRuntime} disabled={loading} className="evo-button-outline px-4 py-2.5 text-sm" aria-label="Actualizar estado del runtime"><RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /><span className="ml-2 hidden sm:inline">Actualizar</span></button></div>
        {error && <div className="glass-card rounded-xl p-4 border border-red-500/20 text-sm text-red-400" role="alert">{error}</div>}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <StatusCard label="API" value={loading ? "Consultando…" : apiOperational ? "Operativa" : "No disponible"} description="Endpoint /health del backend activo" active={!loading && apiOperational} />
          <StatusCard label="Risk" value={loading ? "Consultando…" : riskProfile?.paused ? "Pausado" : riskProfile?.version || "Desconocido"} description="Autoriza o rechaza cada orden Paper." active={!loading && Boolean(riskProfile) && !riskProfile?.paused} />
          <StatusCard label="Backtesting" value={loading ? "Consultando…" : backtestingReady ? "Phase 5" : "No disponible"} description="Evidencia histórica reproducible; no implica rentabilidad validada." active={!loading && backtestingReady} />
          <StatusCard label="Agent Evolution" value={loading ? "Consultando…" : evolutionPolicy?.version || "Desconocido"} description="Fitness + lineage + transferencia de capital. Replicación manual, no automática." active={!loading && evolutionReady && evolutionPolicy?.active} />
          <StatusCard label="Synthetic/Test" value={runtimeLabel} description="El generador aleatorio no participa en evidencia financiera." active={!loading && syntheticDisabled} />
        </div>

        <div className="glass-card rounded-xl overflow-hidden"><div className="px-5 py-3 border-b border-white/5 flex items-center gap-2"><Database className="w-4 h-4 text-cyan-400" /><h2 className="evo-section-title">Runtime efectivo</h2></div><div className="px-5">
          <RuntimeRow label="Persistencia" value="SQLModel + SQLite" description="Accounting sigue siendo la única autoridad financiera activa." />
          <RuntimeRow label="Market Data" value={runtime?.market_data || "unknown"} description="Mercado real y fail-closed." />
          <RuntimeRow label="Risk Engine" value={runtime?.risk || "unknown"} description={`Perfil ${riskProfile?.version || "desconocido"}; circuit breaker ${riskProfile?.paused ? "PAUSADO" : "activo"}.`} />
          <RuntimeRow label="Paper Trading" value={runtime?.paper_trading || "unknown"} description="Ejecución virtual manual sobre mercado real detrás de Risk." />
          <RuntimeRow label="Backtesting" value={runtime?.backtesting || "unknown"} description="Datasets SHA-256 y ejecución determinista t→t+1." />
          <RuntimeRow label="Agent Evolution" value={runtime?.agent_evolution || "unknown"} description={`Política ${evolutionPolicy?.version || "desconocida"}; asignación hija ${(Number(evolutionPolicy?.child_allocation_fraction || 0) * 100).toFixed(0)}% del capital elegible.`} />
          <RuntimeRow label="Trading automático" value={runtime?.automated_trading || "blocked_until_phase_7_runtime"} description="Phase 6 no activa loops autónomos; eso pertenece al runtime 24/7 de Phase 7." />
          <RuntimeRow label="Live" value={runtime?.live_execution || "disabled"} description="Sin adaptador Live ni órdenes reales." />
        </div></div>

        <div className="glass-card rounded-xl overflow-hidden"><div className="px-5 py-3 border-b border-white/5 flex items-center gap-2"><Activity className="w-4 h-4 text-cyan-400" /><h2 className="evo-section-title">Controles disponibles</h2></div><div className="px-5 py-4 text-sm text-muted-foreground space-y-2">
          <p>Risk dispone de pause/resume; no activa trading automático.</p>
          <p>Paper mantiene órdenes MARKET manuales contra quotes reales.</p>
          <p>Backtesting evalúa S1-S4 sobre históricos reproducibles; no existe optimizador automático.</p>
          <p>La replicación Phase 6 exige Backtest con fingerprint vigente y evidencia Paper del propio agente; si pasa, transfiere capital financiado del padre al hijo y nunca lo duplica.</p>
        </div></div>

        <div className="glass-card rounded-xl p-5 border border-amber-500/15"><div className="flex items-start gap-3"><ShieldAlert className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" /><div><p className="text-sm font-medium text-foreground">Legacy preservado, no operativo</p><p className="text-xs text-muted-foreground mt-1">MongoDB y motores legacy siguen versionados para auditoría/migración, pero no participan en Market Data, Accounting, Risk, Paper, Backtesting o Agent Evolution activos.</p></div></div></div>
      </div>
    </div>
  );
}
