import { useState } from "react";
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

const ToggleSwitch = ({ checked, onChange, disabled }) => (
  <button
    onClick={() => !disabled && onChange(!checked)}
    disabled={disabled}
    className={`relative w-12 h-7 rounded-full transition-colors duration-200 ${
      checked ? "bg-[#34C759]" : "bg-[#E5E5EA]"
    } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
  >
    <div className={`absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-sm transition-transform duration-200 ${
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
      className="flex-1 h-1.5 bg-[#E5E5EA] rounded-full appearance-none cursor-pointer accent-[#D97757]"
    />
    <span className="text-[14px] font-medium text-[#1a1a1a] w-12 text-right tabular-nums">
      {value}{label}
    </span>
  </div>
);

const SettingRow = ({ label, description, children, border }) => (
  <div className={`flex items-center justify-between py-3.5 ${border !== false ? "border-b border-black/5" : ""} last:border-0`}>
    <div className="flex-1 mr-4">
      <p className="text-[15px] font-medium text-[#1a1a1a]">{label}</p>
      {description && <p className="text-[13px] text-[#86868b] mt-0.5">{description}</p>}
    </div>
    <div className="shrink-0">{children}</div>
  </div>
);

const SettingsGroup = ({ title, children }) => (
  <div className="bg-white rounded-2xl shadow-sm border border-black/5 overflow-hidden">
    {title && (
      <div className="px-5 py-3 border-b border-black/5">
        <h3 className="text-[13px] font-medium text-[#86868b] uppercase tracking-wide">{title}</h3>
      </div>
    )}
    <div className="divide-y divide-black/5 px-5">
      {children}
    </div>
  </div>
);

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("notifications");
  const [settings, setSettings] = useState({
    notifyOnTrade: true,
    notifyOnReplication: true,
    notifyOnRisk: true,
    notifyOnOpportunity: true,
    emailNotifications: false,

    defaultCapital: 100,
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
    debugMode: false
  });

  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success("Configuración guardada correctamente");
    setSaving(false);
  };

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const tabs = [
    { id: "notifications", label: "Notificaciones", icon: Bell },
    { id: "agents", label: "Agentes", icon: Bot },
    { id: "trading", label: "Trading", icon: Zap },
    { id: "system", label: "Sistema", icon: Database }
  ];

  return (
    <div className="min-h-screen bg-[#F5F3EF]" data-testid="settings-page">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-[28px] font-semibold text-[#1a1a1a] tracking-tight">
              Configuración
            </h1>
            <p className="text-[15px] text-[#86868b] mt-1">
              Preferencias del sistema y valores predeterminados
            </p>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#D97757] text-white rounded-full text-[14px] font-medium hover:bg-[#D97757]/90 transition-colors disabled:opacity-50 shadow-sm shadow-[#D97757]/20"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            Guardar
          </button>
        </div>

        {/* Tabs */}
        <div className="flex bg-white rounded-full border border-black/5 p-1 shadow-sm">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-full text-[14px] font-medium transition-all ${
                  isActive
                    ? "bg-[#D97757] text-white shadow-sm"
                    : "text-[#86868b] hover:text-[#1a1a1a]"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Notifications Tab */}
        {activeTab === "notifications" && (
          <div className="space-y-4">
            <SettingsGroup title="Notificaciones">
              <SettingRow label="Notificaciones de Operaciones" description="Notificar cuando se abren o cierran operaciones">
                <ToggleSwitch
                  checked={settings.notifyOnTrade}
                  onChange={(v) => updateSetting('notifyOnTrade', v)}
                />
              </SettingRow>
              <SettingRow label="Eventos de Replicación" description="Notificar cuando los agentes se replican">
                <ToggleSwitch
                  checked={settings.notifyOnReplication}
                  onChange={(v) => updateSetting('notifyOnReplication', v)}
                />
              </SettingRow>
              <SettingRow label="Alertas de Riesgo" description="Notificar cuando los agentes están en riesgo">
                <ToggleSwitch
                  checked={settings.notifyOnRisk}
                  onChange={(v) => updateSetting('notifyOnRisk', v)}
                />
              </SettingRow>
              <SettingRow label="Alertas de Oportunidad" description="Notificar sobre oportunidades de trading detectadas">
                <ToggleSwitch
                  checked={settings.notifyOnOpportunity}
                  onChange={(v) => updateSetting('notifyOnOpportunity', v)}
                />
              </SettingRow>
              <SettingRow label="Notificaciones por Email" description="Enviar notificaciones por email (requiere configuración)">
                <ToggleSwitch
                  checked={settings.emailNotifications}
                  onChange={(v) => updateSetting('emailNotifications', v)}
                  disabled
                />
              </SettingRow>
            </SettingsGroup>
          </div>
        )}

        {/* Agents Tab */}
        {activeTab === "agents" && (
          <div className="space-y-4">
            <SettingsGroup title="Predeterminados del Agente">
              <SettingRow label="Capital Inicial Predeterminado">
                <div className="flex items-center gap-2">
                  <span className="text-[15px] text-[#86868b]">$</span>
                  <input
                    type="number"
                    value={settings.defaultCapital}
                    onChange={(e) => updateSetting('defaultCapital', parseFloat(e.target.value) || 0)}
                    className="w-24 px-3 py-2 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all text-center"
                  />
                </div>
              </SettingRow>
              <SettingRow label="Nivel de Riesgo Predeterminado">
                <select
                  value={settings.defaultRiskLevel}
                  onChange={(e) => updateSetting('defaultRiskLevel', e.target.value)}
                  className="px-3 py-2 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all"
                >
                  <option value="low">Bajo</option>
                  <option value="medium">Medio</option>
                  <option value="high">Alto</option>
                </select>
              </SettingRow>
            </SettingsGroup>

            <SettingsGroup title="Auto-Replicación">
              <SettingRow label="Activar Auto-Replicación" description="Replicar automáticamente agentes exitosos">
                <ToggleSwitch
                  checked={settings.autoReplicate}
                  onChange={(v) => updateSetting('autoReplicate', v)}
                />
              </SettingRow>
              <SettingRow label="Umbral de Replicación" description={`Replicar cuando el ROI alcanza ${settings.replicationThreshold}%`}>
                <div className="w-48">
                  <SliderControl
                    value={settings.replicationThreshold}
                    onChange={(v) => updateSetting('replicationThreshold', v)}
                    min={10}
                    max={100}
                    step={5}
                    label="%"
                  />
                </div>
              </SettingRow>
            </SettingsGroup>

            <SettingsGroup title="Auto-Terminación">
              <SettingRow label="Activar Auto-Terminación" description="Terminar automáticamente agentes con pérdidas">
                <ToggleSwitch
                  checked={settings.autoTerminate}
                  onChange={(v) => updateSetting('autoTerminate', v)}
                />
              </SettingRow>
              <SettingRow label="Balance de Terminación">
                <div className="flex items-center gap-2">
                  <span className="text-[15px] text-[#86868b]">$</span>
                  <input
                    type="number"
                    value={settings.terminationThreshold}
                    onChange={(e) => updateSetting('terminationThreshold', parseFloat(e.target.value) || 0)}
                    className="w-24 px-3 py-2 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all text-center"
                  />
                </div>
              </SettingRow>
            </SettingsGroup>
          </div>
        )}

        {/* Trading Tab */}
        {activeTab === "trading" && (
          <div className="space-y-4">
            <SettingsGroup title="Parámetros de Trading">
              <SettingRow label="Máx. Operaciones Simultáneas">
                <input
                  type="number"
                  value={settings.maxConcurrentTrades}
                  onChange={(e) => updateSetting('maxConcurrentTrades', parseInt(e.target.value) || 0)}
                  className="w-24 px-3 py-2 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all text-center"
                />
              </SettingRow>
              <SettingRow label="Tamaño de Posición" description={`${settings.defaultPositionSize}% del saldo disponible`}>
                <div className="w-48">
                  <SliderControl
                    value={settings.defaultPositionSize}
                    onChange={(v) => updateSetting('defaultPositionSize', v)}
                    min={1}
                    max={20}
                    step={1}
                    label="%"
                  />
                </div>
              </SettingRow>
              <SettingRow label="Stop Loss Predeterminado">
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    value={settings.stopLossDefault}
                    onChange={(e) => updateSetting('stopLossDefault', parseFloat(e.target.value) || 0)}
                    className="w-20 px-3 py-2 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all text-center"
                  />
                  <span className="text-[15px] text-[#86868b]">%</span>
                </div>
              </SettingRow>
              <SettingRow label="Take Profit Predeterminado">
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    value={settings.takeProfitDefault}
                    onChange={(e) => updateSetting('takeProfitDefault', parseFloat(e.target.value) || 0)}
                    className="w-20 px-3 py-2 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all text-center"
                  />
                  <span className="text-[15px] text-[#86868b]">%</span>
                </div>
              </SettingRow>
            </SettingsGroup>
          </div>
        )}

        {/* System Tab */}
        {activeTab === "system" && (
          <div className="space-y-4">
            <SettingsGroup title="Sistema">
              <SettingRow label="Intervalo de Actualización">
                <select
                  value={String(settings.refreshInterval)}
                  onChange={(e) => updateSetting('refreshInterval', parseInt(e.target.value))}
                  className="px-3 py-2 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all"
                >
                  <option value="10">10 segundos</option>
                  <option value="30">30 segundos</option>
                  <option value="60">1 minuto</option>
                  <option value="300">5 minutos</option>
                </select>
              </SettingRow>
              <SettingRow label="Retención de Datos">
                <select
                  value={String(settings.dataRetentionDays)}
                  onChange={(e) => updateSetting('dataRetentionDays', parseInt(e.target.value))}
                  className="px-3 py-2 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all"
                >
                  <option value="30">30 días</option>
                  <option value="90">90 días</option>
                  <option value="180">180 días</option>
                  <option value="365">1 año</option>
                </select>
              </SettingRow>
              <SettingRow label="Modo Depuración" description="Activar registro detallado" border={false}>
                <ToggleSwitch
                  checked={settings.debugMode}
                  onChange={(v) => updateSetting('debugMode', v)}
                />
              </SettingRow>
            </SettingsGroup>

            {/* Danger Zone */}
            <SettingsGroup>
              <div className="px-5 py-3 border-b border-black/5">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-[#FF3B30]" />
                  <h3 className="text-[13px] font-medium text-[#FF3B30] uppercase tracking-wide">Zona de Peligro</h3>
                </div>
              </div>
              <div className="p-5 space-y-3">
                <button className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-[#FF3B30]/20 text-[#FF3B30] hover:bg-[#FF3B30]/5 transition-colors group">
                  <span className="text-[15px] font-medium">Restablecer Configuración</span>
                  <ChevronRight className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" />
                </button>
                <button className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-[#FF3B30]/20 text-[#FF3B30] hover:bg-[#FF3B30]/5 transition-colors group">
                  <span className="text-[15px] font-medium">Borrar Todos los Datos</span>
                  <ChevronRight className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" />
                </button>
                <button className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-[#FF3B30]/20 text-[#FF3B30] hover:bg-[#FF3B30]/5 transition-colors group">
                  <span className="text-[15px] font-medium">Terminar Todos los Agentes</span>
                  <ChevronRight className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" />
                </button>
              </div>
            </SettingsGroup>
          </div>
        )}
      </div>
    </div>
  );
}
