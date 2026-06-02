import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Settings as SettingsIcon,
  Bell,
  Bot,
  Zap,
  Database,
  Save,
  RefreshCw,
  ChevronRight,
  Shield,
  AlertTriangle
} from "lucide-react";
import { toast } from "sonner";
import { systemAPI, tradingAPI } from "@/lib/api";
import { cn } from "@/lib/utils";

/* ── Reusable UI primitives ── */
const ToggleSwitch = ({ checked, onChange, disabled, "aria-label": ariaLabel }) => (
  <button
    onClick={() => !disabled && onChange(!checked)}
    disabled={disabled}
    className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${
      checked ? "bg-cyan-500" : "bg-white/10"
    } ${disabled ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
    role="switch"
    aria-checked={checked}
    aria-label={ariaLabel}
  >
    <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-transform duration-200 ${
      checked ? "translate-x-5" : "translate-x-0"
    }`} />
  </button>
);

const SliderControl = ({ value, onChange, min, max, step, label }) => (
  <div className="flex items-center gap-4">
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className="flex-1 h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer accent-cyan-500"
      aria-label={label}
    />
    <span className="text-sm font-mono text-foreground w-14 text-right tabular-nums">
      {value}{label}
    </span>
  </div>
);

const SettingRow = ({ label, description, children, border }) => (
  <div className={`flex items-center justify-between py-3.5 ${border !== false ? "border-b border-white/5" : ""} last:border-0`}>
    <div className="flex-1 mr-4">
      <p className="text-sm font-medium text-foreground">{label}</p>
      {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
    </div>
    <div className="shrink-0">{children}</div>
  </div>
);

const SettingsGroup = ({ title, children }) => (
  <motion.div
    initial={{ opacity: 0, y: 8 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
    className="glass-card rounded-xl overflow-hidden"
  >
    {title && (
      <div className="px-5 py-3 border-b border-white/5">
        <h3 className="evo-section-title">{title}</h3>
      </div>
    )}
    <div className="px-5">
      {children}
    </div>
  </motion.div>
);

/* ── Main Page ── */
export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("notifications");
  const [settings, setSettings] = useState({
    notifyOnTrade: true,
    notifyOnReplication: true,
    notifyOnRisk: true,
    notifyOnOpportunity: true,
    emailNotifications: false,
    defaultCapital: 1000,
    defaultRiskLevel: "medium",
    autoReplicate: true,
    replicationThreshold: 50,
    autoTerminate: true,
    terminationThreshold: 1,
    maxConcurrentTrades: 5,
    defaultPositionSize: 5,
    stopLossDefault: 2,
    takeProfitDefault: 5,
    refreshInterval: 30,
    dataRetentionDays: 90,
    debugMode: false,
    systemMode: "test",
  });
  const [saving, setSaving] = useState(false);
  const [engineStatus, setEngineStatus] = useState(null);

  /* Fetch real engine status on mount */
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const r = await tradingAPI.engineStatus();
        setEngineStatus(r.data);
      } catch {}
    };
    fetchStatus();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      // Switch system mode if changed
      if (settings.systemMode) {
        await systemAPI.setMode(settings.systemMode);
      }
      toast.success("Configuración guardada correctamente");
    } catch (err) {
      toast.error(err?.message || "Error al guardar la configuración");
    }
    setSaving(false);
  };

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleDangerAction = async (action) => {
    try {
      if (action === "reset") {
        await systemAPI.resetAgents(settings.defaultCapital);
        toast.success("Agentes reiniciados correctamente");
      } else if (action === "emergency-stop") {
        toast.error("Acción destructiva — usa el Panel para confirmar");
      } else {
        toast.info("Función en desarrollo");
      }
    } catch (err) {
      toast.error(err?.message || "Error en la acción");
    }
  };

  const tabs = [
    { id: "notifications", label: "Notificaciones", icon: Bell },
    { id: "agents", label: "Agentes", icon: Bot },
    { id: "trading", label: "Trading", icon: Zap },
    { id: "system", label: "Sistema", icon: Database }
  ];

  return (
    <div className="min-h-screen bg-background" data-testid="settings-page">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="font-heading text-3xl font-bold tracking-wide text-foreground uppercase">
              Configuración
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Preferencias del sistema y valores predeterminados
            </p>
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="evo-button-primary px-5 py-2.5 text-sm rounded-lg"
            aria-label="Guardar configuración"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            <span className="ml-2 hidden sm:inline">Guardar</span>
          </button>
        </motion.div>

        {/* Tabs */}
        <div className="flex glass-card rounded-lg p-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all",
                  isActive
                    ? "bg-cyan-500/15 text-cyan-400 ring-1 ring-cyan-500/20"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/[0.04]"
                )}
                role="tab"
                aria-selected={isActive}
                aria-controls={`settings-panel-${tab.id}`}
              >
                <Icon className="w-4 h-4" aria-hidden="true" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* ── Notifications Tab ── */}
        {activeTab === "notifications" && (
          <div className="space-y-4" role="tabpanel" id="settings-panel-notifications">
            <SettingsGroup title="Notificaciones">
              <SettingRow label="Notificaciones de Operaciones" description="Notificar cuando se abren o cierran operaciones">
                <ToggleSwitch checked={settings.notifyOnTrade} onChange={(v) => updateSetting('notifyOnTrade', v)} aria-label="Notificar operaciones" />
              </SettingRow>
              <SettingRow label="Eventos de Replicación" description="Notificar cuando los agentes se replican">
                <ToggleSwitch checked={settings.notifyOnReplication} onChange={(v) => updateSetting('notifyOnReplication', v)} aria-label="Notificar replicación" />
              </SettingRow>
              <SettingRow label="Alertas de Riesgo" description="Notificar cuando los agentes están en riesgo">
                <ToggleSwitch checked={settings.notifyOnRisk} onChange={(v) => updateSetting('notifyOnRisk', v)} aria-label="Alertas de riesgo" />
              </SettingRow>
              <SettingRow label="Alertas de Oportunidad" description="Notificar sobre oportunidades de trading detectadas">
                <ToggleSwitch checked={settings.notifyOnOpportunity} onChange={(v) => updateSetting('notifyOnOpportunity', v)} aria-label="Alertas de oportunidad" />
              </SettingRow>
              <SettingRow label="Notificaciones por Email" description="Enviar notificaciones por email (requiere configuración)">
                <ToggleSwitch checked={settings.emailNotifications} onChange={(v) => updateSetting('emailNotifications', v)} disabled aria-label="Notificaciones por email" />
              </SettingRow>
            </SettingsGroup>
          </div>
        )}

        {/* ── Agents Tab ── */}
        {activeTab === "agents" && (
          <div className="space-y-4" role="tabpanel" id="settings-panel-agents">
            <SettingsGroup title="Predeterminados del Agente">
              <SettingRow label="Capital Inicial Predeterminado">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground font-mono">€</span>
                  <input
                    type="number"
                    value={settings.defaultCapital}
                    onChange={(e) => updateSetting('defaultCapital', parseFloat(e.target.value) || 0)}
                    className="evo-input w-28 text-center py-2 text-sm"
                    aria-label="Capital inicial"
                  />
                </div>
              </SettingRow>
              <SettingRow label="Nivel de Riesgo Predeterminado">
                <select
                  value={settings.defaultRiskLevel}
                  onChange={(e) => updateSetting('defaultRiskLevel', e.target.value)}
                  className="evo-input w-36 py-2 text-sm"
                  aria-label="Nivel de riesgo"
                >
                  <option value="low">Bajo</option>
                  <option value="medium">Medio</option>
                  <option value="high">Alto</option>
                </select>
              </SettingRow>
            </SettingsGroup>

            <SettingsGroup title="Auto-Replicación">
              <SettingRow label="Activar Auto-Replicación" description="Replicar automáticamente agentes exitosos">
                <ToggleSwitch checked={settings.autoReplicate} onChange={(v) => updateSetting('autoReplicate', v)} aria-label="Auto-replicación" />
              </SettingRow>
              <SettingRow label="Umbral de Replicación" description={`Replicar cuando el ROI alcanza ${settings.replicationThreshold}%`}>
                <div className="w-48">
                  <SliderControl value={settings.replicationThreshold} onChange={(v) => updateSetting('replicationThreshold', v)} min={10} max={100} step={5} label="%" />
                </div>
              </SettingRow>
            </SettingsGroup>

            <SettingsGroup title="Auto-Terminación">
              <SettingRow label="Activar Auto-Terminación" description="Terminar automáticamente agentes con pérdidas">
                <ToggleSwitch checked={settings.autoTerminate} onChange={(v) => updateSetting('autoTerminate', v)} aria-label="Auto-terminación" />
              </SettingRow>
              <SettingRow label="Balance de Terminación">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground font-mono">€</span>
                  <input
                    type="number"
                    value={settings.terminationThreshold}
                    onChange={(e) => updateSetting('terminationThreshold', parseFloat(e.target.value) || 0)}
                    className="evo-input w-28 text-center py-2 text-sm"
                    aria-label="Balance de terminación"
                  />
                </div>
              </SettingRow>
            </SettingsGroup>
          </div>
        )}

        {/* ── Trading Tab ── */}
        {activeTab === "trading" && (
          <div className="space-y-4" role="tabpanel" id="settings-panel-trading">
            <SettingsGroup title="Parámetros de Trading">
              <SettingRow label="Máx. Operaciones Simultáneas">
                <input type="number" value={settings.maxConcurrentTrades} onChange={(e) => updateSetting('maxConcurrentTrades', parseInt(e.target.value) || 0)} className="evo-input w-24 text-center py-2 text-sm" aria-label="Máx operaciones simultáneas" />
              </SettingRow>
              <SettingRow label="Tamaño de Posición" description={`${settings.defaultPositionSize}% del saldo disponible`}>
                <div className="w-48">
                  <SliderControl value={settings.defaultPositionSize} onChange={(v) => updateSetting('defaultPositionSize', v)} min={1} max={20} step={1} label="%" />
                </div>
              </SettingRow>
              <SettingRow label="Stop Loss Predeterminado">
                <div className="flex items-center gap-2">
                  <input type="number" value={settings.stopLossDefault} onChange={(e) => updateSetting('stopLossDefault', parseFloat(e.target.value) || 0)} className="evo-input w-20 text-center py-2 text-sm" aria-label="Stop loss" />
                  <span className="text-sm text-muted-foreground font-mono">%</span>
                </div>
              </SettingRow>
              <SettingRow label="Take Profit Predeterminado">
                <div className="flex items-center gap-2">
                  <input type="number" value={settings.takeProfitDefault} onChange={(e) => updateSetting('takeProfitDefault', parseFloat(e.target.value) || 0)} className="evo-input w-20 text-center py-2 text-sm" aria-label="Take profit" />
                  <span className="text-sm text-muted-foreground font-mono">%</span>
                </div>
              </SettingRow>
            </SettingsGroup>
          </div>
        )}

        {/* ── System Tab ── */}
        {activeTab === "system" && (
          <div className="space-y-4" role="tabpanel" id="settings-panel-system">
            <SettingsGroup title="Estado del Motor">
              <div className="py-3">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "w-2.5 h-2.5 rounded-full",
                    engineStatus?.status === "running" ? "bg-green-500 animate-pulse" : "bg-muted"
                  )} aria-hidden="true" />
                  <span className="text-sm text-foreground font-mono">
                    {engineStatus ? `${engineStatus.status}` : "Desconocido"}
                  </span>
                </div>
              </div>
            </SettingsGroup>

            <SettingsGroup title="Sistema">
              <SettingRow label="Modo del Sistema" description="Test = datos simulados, Live = datos reales de Binance">
                <select
                  value={settings.systemMode}
                  onChange={(e) => updateSetting('systemMode', e.target.value)}
                  className="evo-input w-32 py-2 text-sm"
                  aria-label="Modo del sistema"
                >
                  <option value="test">Test (Simulado)</option>
                  <option value="live">Live (Binance)</option>
                </select>
              </SettingRow>
              <SettingRow label="Intervalo de Actualización">
                <select value={String(settings.refreshInterval)} onChange={(e) => updateSetting('refreshInterval', parseInt(e.target.value))} className="evo-input w-36 py-2 text-sm" aria-label="Intervalo de actualización">
                  <option value="10">10 segundos</option>
                  <option value="30">30 segundos</option>
                  <option value="60">1 minuto</option>
                  <option value="300">5 minutos</option>
                </select>
              </SettingRow>
              <SettingRow label="Retención de Datos">
                <select value={String(settings.dataRetentionDays)} onChange={(e) => updateSetting('dataRetentionDays', parseInt(e.target.value))} className="evo-input w-36 py-2 text-sm" aria-label="Retención de datos">
                  <option value="30">30 días</option>
                  <option value="90">90 días</option>
                  <option value="180">180 días</option>
                  <option value="365">1 año</option>
                </select>
              </SettingRow>
              <SettingRow label="Modo Depuración" description="Activar registro detallado" border={false}>
                <ToggleSwitch checked={settings.debugMode} onChange={(v) => updateSetting('debugMode', v)} aria-label="Modo depuración" />
              </SettingRow>
            </SettingsGroup>

            {/* Danger Zone */}
            <SettingsGroup>
              <div className="px-5 py-3 border-b border-white/5">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-500" aria-hidden="true" />
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-red-500">Zona de Peligro</h3>
                </div>
              </div>
              <div className="p-5 space-y-3">
                <button
                  onClick={() => handleDangerAction("reset")}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/5 transition-colors group"
                  aria-label="Restablecer configuración"
                >
                  <span className="text-sm font-medium">Restablecer Configuración</span>
                  <ChevronRight className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
                </button>
                <button
                  onClick={() => handleDangerAction("clear")}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/5 transition-colors group"
                  aria-label="Borrar todos los datos"
                >
                  <span className="text-sm font-medium">Borrar Todos los Datos</span>
                  <ChevronRight className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
                </button>
                <button
                  onClick={() => handleDangerAction("emergency-stop")}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-lg border border-red-500/20 text-red-400 hover:bg-red-500/5 transition-colors group"
                  aria-label="Terminar todos los agentes"
                >
                  <span className="text-sm font-medium">Terminar Todos los Agentes</span>
                  <ChevronRight className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
                </button>
              </div>
            </SettingsGroup>
          </div>
        )}
      </div>
    </div>
  );
}
