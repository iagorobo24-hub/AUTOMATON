import { useCallback, useEffect, useState } from "react";
import { Activity, Database, RefreshCw, ShieldAlert } from "lucide-react";
import { healthAPI } from "@/lib/api";

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRuntime = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await healthAPI.health();
      setRuntime(response.data);
    } catch (err) {
      setRuntime(null);
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
            <p className="text-sm text-muted-foreground mt-1">Estado del baseline previo a Real Market Data</p>
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
          <StatusCard
            label="API"
            value={loading ? "Consultando…" : apiOperational ? "Operativa" : "No disponible"}
            description="Endpoint /health del backend activo"
            active={!loading && apiOperational}
          />
          <StatusCard
            label="Synthetic/Test"
            value={runtimeLabel}
            description="El generador aleatorio no participa en el runtime normal ni produce evidencia financiera."
            active={!loading && syntheticDisabled}
          />
        </div>

        <div className="glass-card rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-white/5 flex items-center gap-2">
            <Database className="w-4 h-4 text-cyan-400" aria-hidden="true" />
            <h2 className="evo-section-title">Runtime efectivo</h2>
          </div>
          <div className="px-5">
            <RuntimeRow label="Persistencia" value="SQLModel + SQLite" description="Fuente de verdad técnica actual para agentes y registros legacy." />
            <RuntimeRow label="Modo" value={runtime?.runtime_mode || "transition"} description="Baseline de transición: sin motor autónomo de trading activo." />
            <RuntimeRow label="Paper Trading" value={runtime?.paper_trading || "not_implemented"} description="Paper no se declara activo hasta consumir mercado real y accounting verificable." />
            <RuntimeRow label="Evidencia financiera" value="No disponible" description="Los registros previos carecen de procedencia por modo y quedan excluidos de métricas verificables." />
          </div>
        </div>

        <div className="glass-card rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-white/5 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" aria-hidden="true" />
            <h2 className="evo-section-title">Controles disponibles</h2>
          </div>
          <div className="px-5 py-4 text-sm text-muted-foreground space-y-2">
            <p>La página Agentes permite crear, fondear, replicar manualmente y retirar agentes del inventario técnico.</p>
            <p>No existe control de PnL simulado en la superficie activa. Paper/Live, riesgo global y ejecución se habilitarán únicamente en sus fases correspondientes.</p>
          </div>
        </div>

        <div className="glass-card rounded-xl p-5 border border-amber-500/15">
          <div className="flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" aria-hidden="true" />
            <div>
              <p className="text-sm font-medium text-foreground">Legacy preservado, no operativo</p>
              <p className="text-xs text-muted-foreground mt-1">
                MongoDB, TradingEngine, PaperTradingEngine y BinanceService legacy siguen versionados para auditoría/migración, pero no se montan ni pueden aportar datos a la evidencia activa.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
