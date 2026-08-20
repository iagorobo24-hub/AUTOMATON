import { useCallback, useEffect, useState } from "react";
import { Activity, Database, RefreshCw, ShieldAlert } from "lucide-react";
import { evolutionAPI, healthAPI, liveAPI, researchAPI, riskAPI, runtimeAPI } from "@/lib/api";

function StatusCard({ label, value, description, active }) {
  return <div className="glass-card rounded-xl p-5"><div className="flex items-center justify-between gap-4 mb-2"><p className="text-xs uppercase tracking-wider text-muted-foreground">{label}</p><span className={`w-2.5 h-2.5 rounded-full ${active ? "bg-green-500" : "bg-gray-500"}`} /></div><p className="text-lg font-semibold text-foreground">{value}</p>{description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}</div>;
}
function RuntimeRow({ label, value, description }) { return <div className="flex items-start justify-between gap-6 py-4 border-b border-white/5 last:border-0"><div><p className="text-sm font-medium text-foreground">{label}</p>{description && <p className="text-xs text-muted-foreground mt-1 max-w-xl">{description}</p>}</div><span className="text-sm font-mono text-cyan-400 shrink-0">{value}</span></div>; }

export default function SettingsPage() {
  const [runtime, setRuntime] = useState(null), [riskProfile, setRiskProfile] = useState(null), [evolutionPolicy, setEvolutionPolicy] = useState(null);
  const [runtimeStatus, setRuntimeStatus] = useState(null), [runtimeSessions, setRuntimeSessions] = useState([]), [researchPolicy, setResearchPolicy] = useState(null);
  const [liveStatus, setLiveStatus] = useState(null), [livePolicy, setLivePolicy] = useState(null), [loading, setLoading] = useState(true), [error, setError] = useState(null);

  const fetchRuntime = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [healthResponse, riskResponse, evolutionResponse, runtimeResponse, sessionsResponse, researchResponse, liveStatusResponse, livePolicyResponse] = await Promise.all([
        healthAPI.health(), riskAPI.activeProfile(), evolutionAPI.activePolicy(), runtimeAPI.status(), runtimeAPI.sessions({ limit: 20 }), researchAPI.activePolicy(), liveAPI.status(), liveAPI.policy(),
      ]);
      setRuntime(healthResponse.data); setRiskProfile(riskResponse.data); setEvolutionPolicy(evolutionResponse.data); setRuntimeStatus(runtimeResponse.data);
      setRuntimeSessions(Array.isArray(sessionsResponse.data) ? sessionsResponse.data : []); setResearchPolicy(researchResponse.data); setLiveStatus(liveStatusResponse.data); setLivePolicy(livePolicyResponse.data);
    } catch (err) {
      setRuntime(null); setRiskProfile(null); setEvolutionPolicy(null); setRuntimeStatus(null); setRuntimeSessions([]); setResearchPolicy(null); setLiveStatus(null); setLivePolicy(null);
      setError(err?.message || "No se pudo consultar el runtime");
    } finally { setLoading(false); }
  }, []);
  useEffect(() => { fetchRuntime(); }, [fetchRuntime]);

  const apiOperational = runtime?.status === "ok", syntheticDisabled = runtime?.synthetic_engine === "disabled", backtestingReady = runtime?.backtesting === "evidence_phase_5";
  const evolutionReady = runtime?.agent_evolution === "evidence_phase_6", paperRuntimeReady = runtime?.paper_runtime === "runtime_phase_7", researchReady = runtime?.strategy_research === "evidence_phase_8";
  const liveReadinessAvailable = runtime?.live_execution === "readiness_phase_10" && liveStatus?.mode === "readiness_phase_10";
  const activeSessions = runtimeSessions.filter((item) => ["RUNNING", "DEGRADED", "RECOVERY_REQUIRED"].includes(item.status)).length;
  const runtimeLabel = loading ? "Consultando…" : !runtime ? "Desconocido" : syntheticDisabled ? "Sintético desactivado" : "Revisar configuración";

  return <div className="min-h-screen bg-background" data-testid="settings-page"><div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
    <div className="flex items-center justify-between gap-4"><div><h1 className="font-heading text-3xl font-bold tracking-wide text-foreground uppercase">Configuración</h1><p className="text-sm text-muted-foreground mt-1">Paper autónomo, Research reproducible y frontera Live preparada sin capital real</p></div><button onClick={fetchRuntime} disabled={loading} className="evo-button-outline px-4 py-2.5 text-sm"><RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /><span className="ml-2 hidden sm:inline">Actualizar</span></button></div>
    {error && <div className="glass-card rounded-xl p-4 border border-red-500/20 text-sm text-red-400" role="alert">{error}</div>}

    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <StatusCard label="API" value={loading ? "Consultando…" : apiOperational ? "Operativa" : "No disponible"} description="Endpoint /health del backend activo" active={!loading && apiOperational} />
      <StatusCard label="Risk" value={loading ? "Consultando…" : riskProfile?.paused ? "Pausado" : riskProfile?.version || "Desconocido"} description="Autoriza o rechaza cada orden Paper." active={!loading && Boolean(riskProfile) && !riskProfile?.paused} />
      <StatusCard label="Backtesting" value={loading ? "Consultando…" : backtestingReady ? "Phase 5" : "No disponible"} description="Evidencia histórica reproducible; no implica rentabilidad." active={!loading && backtestingReady} />
      <StatusCard label="Agent Evolution" value={loading ? "Consultando…" : evolutionPolicy?.version || "Desconocido"} description="Fitness, lineage y replicación manual." active={!loading && evolutionReady && evolutionPolicy?.active} />
      <StatusCard label="Paper Runtime" value={loading ? "Consultando…" : paperRuntimeReady ? `Phase 7 · ${activeSessions} activas` : "No disponible"} description="Sesiones persistentes sin auto-resume." active={!loading && paperRuntimeReady} />
      <StatusCard label="Strategy Research" value={loading ? "Consultando…" : researchPolicy?.version || "Desconocido"} description="TRAIN/VALIDATION/OOS + forward Paper; promoción manual." active={!loading && researchReady && researchPolicy?.active} />
      <StatusCard label="Live Readiness" value={loading ? "Consultando…" : liveReadinessAvailable ? (liveStatus?.architecture_ready ? "Architecture ready" : "Phase 10 · gated") : "No disponible"} description="Controles, reconciliación y límites preparados. No existe transmisión de órdenes reales." active={!loading && liveReadinessAvailable} />
      <StatusCard label="REAL CAPITAL" value={loading ? "Consultando…" : runtime?.real_capital_execution === "disabled" ? "DISABLED" : "REVISAR"} description="Fase 10 no autoriza ni activa dinero real." active={false} />
      <StatusCard label="Synthetic/Test" value={runtimeLabel} description="El generador aleatorio no participa en evidencia financiera." active={!loading && syntheticDisabled} />
    </div>

    <div className="glass-card rounded-xl overflow-hidden"><div className="px-5 py-3 border-b border-white/5 flex items-center gap-2"><Database className="w-4 h-4 text-cyan-400" /><h2 className="evo-section-title">Runtime efectivo</h2></div><div className="px-5">
      <RuntimeRow label="Persistencia" value="SQLModel + SQLite" description="Accounting sigue siendo autoridad de Paper; Live Readiness mantiene evidencia separada." />
      <RuntimeRow label="Market Data" value={runtime?.market_data || "unknown"} description="Mercado real y fail-closed." />
      <RuntimeRow label="Risk Engine" value={runtime?.risk || "unknown"} description={`Perfil ${riskProfile?.version || "desconocido"}; ${riskProfile?.paused ? "PAUSADO" : "activo"}.`} />
      <RuntimeRow label="Paper Runtime" value={runtime?.paper_runtime || "unknown"} description={`${runtimeStatus?.policy_version || "runtime-v1"}; sin auto-resume.`} />
      <RuntimeRow label="Strategy Research" value={runtime?.strategy_research || "unknown"} description={`Política ${researchPolicy?.version || "desconocida"}; promoción manual.`} />
      <RuntimeRow label="Live Readiness" value={runtime?.live_execution || "unknown"} description={`Política ${livePolicy?.version || "live-v1"}; adapter ${liveStatus?.adapter || "disabled"}; emergency stop ${liveStatus?.emergency_stop ? "ACTIVE" : "clear"}.`} />
      <RuntimeRow label="Máximo readiness capital" value={livePolicy?.max_deployable_capital ? `$${livePolicy.max_deployable_capital}` : "unknown"} description="Ceiling de diseño; no es capital autorizado." />
      <RuntimeRow label="Real capital" value={runtime?.real_capital_execution || "disabled"} description="Sin endpoint de órdenes Live, sin credenciales de trading y sin activación automática." />
    </div></div>

    <div className="glass-card rounded-xl overflow-hidden"><div className="px-5 py-3 border-b border-white/5 flex items-center gap-2"><Activity className="w-4 h-4 text-cyan-400" /><h2 className="evo-section-title">Controles disponibles</h2></div><div className="px-5 py-4 text-sm text-muted-foreground space-y-2">
      <p>Paper sigue detrás de Risk y separado de Live.</p><p>Research clasifica candidatos; no despliega ni activa nada.</p>
      <p>Live Readiness dispone de policy, evaluaciones, reconciliación y emergency stop persistente.</p>
      <p>No existe botón de activar Live ni de enviar órdenes reales en esta interfaz.</p>
    </div></div>

    <div className="glass-card rounded-xl p-5 border border-amber-500/15"><div className="flex items-start gap-3"><ShieldAlert className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" /><div><p className="text-sm font-medium text-foreground">REAL CAPITAL DISABLED</p><p className="text-xs text-muted-foreground mt-1">`ARCHITECTURE_READY` solo significa que la frontera técnica cumple los gates de `live-v1`. Activar dinero real requiere otra decisión explícita y un adapter de exchange auditado que no existe en Phase 10.</p></div></div></div>
  </div></div>;
}
