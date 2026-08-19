import { useCallback, useEffect, useState } from "react";
import { Activity, Database, RefreshCw, ShieldAlert } from "lucide-react";
import { healthAPI, riskAPI } from "@/lib/api";

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRuntime = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthResponse, riskResponse] = await Promise.all([
        healthAPI.health(),
        riskAPI.activeProfile(),
      ]);
      setRuntime(healthResponse.data);
      setRiskProfile(riskResponse.data);
    } catch (err) {
      setRuntime(null);
      setRiskProfile(null);
      setError(err?.message || "No se pudo consultar el runtime");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRuntime();
  }, [fetchRuntime]);

  const apiOperational = runtime?.status === "ok";
  const syntheticDisabled = runtime?.synthetic_engine === "disabled";
  const runtimeLabel = loading
    ? "Consultando…"
    : !runtime
      ? "Desconocido"
      : syntheticDisabled
        ? "Sintético desactivado"
        : "Revisar configuración";

  return (
    <div className="min-h-screen bg-background" data-testid="settings-page">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl font-bold tracking-wide text-foreground uppercase">Configuración</h1>
            <p className="text-sm text-muted-foreground mt-1">Estado del runtime Paper con Risk obligatorio</p>
          </div>
          <button onClick={fetchRuntime} disabled={loading} className="evo-button-outline px-4 py-2.5 text-sm" aria-label="Actualizar estado del runtime">
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            <span className="ml-2 hidden sm:inline">Actualizar</span>
          </button>
        </div>

        {error && (
          <div className="glass-card rounded-xl p-4 border border-red-500/20 text-sm text-red-400" role="alert">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <StatusCard label="API" value={loading ? "Consultando…" : apiOperational ? "Operativa" : "No disponible"} description="Endpoint /health del backend activo" active={!loading && apiOperational} />
          <StatusCard label="Risk" value={loading ? "Consultando…" : riskProfile?.paused ? "Pausado" : riskProfile?.version || "Desconocido"} description="Perfil persistido que autoriza o rechaza cada orden Paper activa." active={!loading && Boolean(riskProfile) && !riskProfile?.paused} />
          <StatusCard label="Synthetic/Test" value={runtimeLabel} description="El generador aleatorio no participa en el runtime normal ni produce evidencia financiera." active={!loading && syntheticDisabled} />
        </div>

        <div className="glass-card rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-white/5 flex items-center gap-2">
            <Database className="w-4 h-4 text-cyan-400" aria-hidden="true" />
            <h2 className="evo-section-title">Runtime efectivo</h2>
          </div>
          <div className="px-5">
            <RuntimeRow label="Persistencia" value="SQLModel + SQLite" description="Accounting es la fuente financiera autoritativa; Trade legacy queda fuera de la evidencia Paper." />
            <RuntimeRow label="Modo" value={runtime?.runtime_mode || "transition"} description="Runtime de transición sin motor autónomo de trading." />
            <RuntimeRow label="Market Data" value={runtime?.market_data || "unknown"} description="Quotes reales y fail-closed para la frontera Paper." />
            <RuntimeRow label="Accounting" value={runtime?.accounting || "unknown"} description="Cash, posiciones, fills, fees y reconciliación persistentes." />
            <RuntimeRow label="Risk Engine" value={runtime?.risk || "unknown"} description={`Perfil ${riskProfile?.version || "desconocido"}; circuit breaker ${riskProfile?.paused ? "PAUSADO" : "activo"}.`} />
            <RuntimeRow label="Paper Trading" value={runtime?.paper_trading || "unknown"} description="Ejecución virtual manual sobre mercado real, siempre detrás de Risk." />
            <RuntimeRow label="Trading automático" value={runtime?.automated_trading || "blocked_until_strategy_integration"} description="Risk ya existe, pero los agentes todavía no están conectados a ejecución automática." />
            <RuntimeRow label="Live" value={runtime?.live_execution || "disabled"} description="Sin adaptador Live ni ruta capaz de enviar órdenes reales." />
          </div>
        </div>

        <div className="glass-card rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-white/5 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" aria-hidden="true" />
            <h2 className="evo-section-title">Controles disponibles</h2>
          </div>
          <div className="px-5 py-4 text-sm text-muted-foreground space-y-2">
            <p>La API Risk dispone de pause/resume como circuit breaker explícito. No activa trading automático.</p>
            <p>La API Paper mantiene órdenes MARKET manuales de operador contra quotes reales; cada orden debe recibir ALLOW de Risk antes de crear estado financiero.</p>
            <p>La replicación de agentes sigue bloqueada hasta definir transferencia de capital y fitness en Agent Evolution.</p>
          </div>
        </div>

        <div className="glass-card rounded-xl p-5 border border-amber-500/15">
          <div className="flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" aria-hidden="true" />
            <div>
              <p className="text-sm font-medium text-foreground">Legacy preservado, no operativo</p>
              <p className="text-xs text-muted-foreground mt-1">MongoDB, TradingEngine, PaperTradingEngine y BinanceService legacy siguen versionados para auditoría/migración, pero no participan en Market Data, Accounting, Risk o Paper activos.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
