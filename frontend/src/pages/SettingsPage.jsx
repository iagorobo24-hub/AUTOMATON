import { useCallback, useEffect, useState } from "react";
import { Activity, Database, RefreshCw, ShieldAlert } from "lucide-react";
import { evolutionAPI, healthAPI, researchAPI, riskAPI, runtimeAPI } from "@/lib/api";

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
  const [runtimeStatus, setRuntimeStatus] = useState(null);
  const [runtimeSessions, setRuntimeSessions] = useState([]);
  const [researchPolicy, setResearchPolicy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRuntime = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthResponse, riskResponse, evolutionResponse, runtimeResponse, sessionsResponse, researchResponse] = await Promise.all([
        healthAPI.health(), riskAPI.activeProfile(), evolutionAPI.activePolicy(), runtimeAPI.status(), runtimeAPI.sessions({ limit: 20 }), researchAPI.activePolicy(),
      ]);
      setRuntime(healthResponse.data);
      setRiskProfile(riskResponse.data);
      setEvolutionPolicy(evolutionResponse.data);
      setRuntimeStatus(runtimeResponse.data);
      setRuntimeSessions(Array.isArray(sessionsResponse.data) ? sessionsResponse.data : []);
      setResearchPolicy(researchResponse.data);
    } catch (err) {
      setRuntime(null); setRiskProfile(null); setEvolutionPolicy(null); setRuntimeStatus(null); setRuntimeSessions([]); setResearchPolicy(null);
      setError(err?.message || "No se pudo consultar el runtime");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchRuntime(); }, [fetchRuntime]);

  const apiOperational = runtime?.status === "ok";
  const syntheticDisabled = runtime?.synthetic_engine === "disabled";
  const backtestingReady = runtime?.backtesting === "evidence_phase_5";
  const evolutionReady = runtime?.agent_evolution === "evidence_phase_6";
  const paperRuntimeReady = runtime?.paper_runtime === "runtime_phase_7";
  const researchReady = runtime?.strategy_research === "evidence_phase_8";
  const activeSessions = runtimeSessions.filter((item) => ["RUNNING", "DEGRADED", "RECOVERY_REQUIRED"].includes(item.status)).length;
  const runtimeLabel = loading ? "Consultando…" : !runtime ? "Desconocido" : syntheticDisabled ? "Sintético desactivado" : "Revisar configuración";

  return (
    <div className="min-h-screen bg-background" data-testid="settings-page">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        <div className="flex items-center justify-between gap-4"><div><h1 className="font-heading text-3xl font-bold tracking-wide text-foreground uppercase">Configuración</h1><p className="text-sm text-muted-foreground mt-1">Paper autónomo con Risk, evidencia reproducible y Strategy Research OOS/forward</p></div><button onClick={fetchRuntime} disabled={loading} className="evo-button-outline px-4 py-2.5 text-sm" aria-label="Actualizar estado del runtime"><RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /><span className="ml-2 hidden sm:inline">Actualizar</span></button></div>
        {error && <div className="glass-card rounded-xl p-4 border border-red-500/20 text-sm text-red-400" role="alert">{error}</div>}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <StatusCard label="API" value={loading ? "Consultando…" : apiOperational ? "Operativa" : "No disponible"} description="Endpoint /health del backend activo" active={!loading && apiOperational} />
          <StatusCard label="Risk" value={loading ? "Consultando…" : riskProfile?.paused ? "Pausado" : riskProfile?.version || "Desconocido"} description="Autoriza o rechaza cada orden Paper, manual o autónoma." active={!loading && Boolean(riskProfile) && !riskProfile?.paused} />
          <StatusCard label="Backtesting" value={loading ? "Consultando…" : backtestingReady ? "Phase 5" : "No disponible"} description="Evidencia histórica reproducible; no implica rentabilidad validada." active={!loading && backtestingReady} />
          <StatusCard label="Agent Evolution" value={loading ? "Consultando…" : evolutionPolicy?.version || "Desconocido"} description="Fitness + lineage + transferencia de capital. Replicación sigue siendo manual." active={!loading && evolutionReady && evolutionPolicy?.active} />
          <StatusCard label="Paper Runtime" value={loading ? "Consultando…" : paperRuntimeReady ? `Phase 7 · ${activeSessions} activas` : "No disponible"} description="Sesiones persistentes; nunca se reanudan silenciosamente tras restart." active={!loading && paperRuntimeReady} />
          <StatusCard label="Strategy Research" value={loading ? "Consultando…" : researchPolicy?.version || "Desconocido"} description="TRAIN/VALIDATION/OOS + forward Paper. Promoción manual; no es garantía de rentabilidad." active={!loading && researchReady && researchPolicy?.active} />
          <StatusCard label="Synthetic/Test" value={runtimeLabel} description="El generador aleatorio no participa en evidencia financiera." active={!loading && syntheticDisabled} />
        </div>

        <div className="glass-card rounded-xl overflow-hidden"><div className="px-5 py-3 border-b border-white/5 flex items-center gap-2"><Database className="w-4 h-4 text-cyan-400" /><h2 className="evo-section-title">Runtime efectivo</h2></div><div className="px-5">
          <RuntimeRow label="Persistencia" value="SQLModel + SQLite" description="Accounting sigue siendo la única autoridad financiera activa." />
          <RuntimeRow label="Market Data" value={runtime?.market_data || "unknown"} description="Mercado real y fail-closed." />
          <RuntimeRow label="Risk Engine" value={runtime?.risk || "unknown"} description={`Perfil ${riskProfile?.version || "desconocido"}; circuit breaker ${riskProfile?.paused ? "PAUSADO" : "activo"}.`} />
          <RuntimeRow label="Paper Trading" value={runtime?.paper_trading || "unknown"} description="Ejecución virtual manual y autónoma sobre mercado real, siempre detrás de Risk." />
          <RuntimeRow label="Paper Runtime" value={runtime?.paper_runtime || "unknown"} description={`${runtimeStatus?.policy_version || "runtime-v1"}; scheduler persistente SQLite + asyncio in-process, sin auto-resume.`} />
          <RuntimeRow label="Backtesting" value={runtime?.backtesting || "unknown"} description="Datasets SHA-256 y ejecución determinista t→t+1." />
          <RuntimeRow label="Agent Evolution" value={runtime?.agent_evolution || "unknown"} description={`Política ${evolutionPolicy?.version || "desconocida"}; asignación hija ${(Number(evolutionPolicy?.child_allocation_fraction || 0) * 100).toFixed(0)}% del capital elegible.`} />
          <RuntimeRow label="Strategy Research" value={runtime?.strategy_research || "unknown"} description={`Política ${researchPolicy?.version || "desconocida"}; promoción manual exige OOS + forward Paper y source SHA vigente.`} />
          <RuntimeRow label="Trading automático" value={runtime?.automated_trading || "unknown"} description="Disponible únicamente dentro de sesiones Paper Phase 7 explícitamente iniciadas; una promoción Research no auto-despliega nada." />
          <RuntimeRow label="Live" value={runtime?.live_execution || "disabled"} description="Sin adaptador Live ni órdenes reales." />
        </div></div>

        <div className="glass-card rounded-xl overflow-hidden"><div className="px-5 py-3 border-b border-white/5 flex items-center gap-2"><Activity className="w-4 h-4 text-cyan-400" /><h2 className="evo-section-title">Controles disponibles</h2></div><div className="px-5 py-4 text-sm text-muted-foreground space-y-2">
          <p>Risk dispone de pause/resume y sigue siendo obligatorio para cada orden.</p>
          <p>Paper conserva órdenes MARKET manuales y añade origen `strategy_runtime` solo desde sesiones Phase 7.</p>
          <p>Las sesiones 24/7 tienen start/pause/resume/recover/stop, heartbeat y ciclos persistentes por candle.</p>
          <p>Backtesting evalúa S1-S4 sobre históricos reproducibles.</p>
          <p>Strategy Research exige ventanas cronológicas TRAIN/VALIDATION/OOS y forward Paper; no existe optimizador ni mutación automática.</p>
          <p>La promoción Research es una clasificación manual de evidencia y no cambia automáticamente ninguna sesión o estrategia.</p>
        </div></div>

        <div className="glass-card rounded-xl p-5 border border-amber-500/15"><div className="flex items-start gap-3"><ShieldAlert className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" /><div><p className="text-sm font-medium text-foreground">Live continúa estructuralmente aislado</p><p className="text-xs text-muted-foreground mt-1">MongoDB y motores legacy siguen fuera del runtime activo. Strategy Research no habilita órdenes reales ni convierte un candidato promovido en Live-eligible.</p></div></div></div>
      </div>
    </div>
  );
}
