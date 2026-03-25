import { useState, useEffect } from "react";
import { 
  Settings as SettingsIcon, 
  Bell, 
  Bot, 
  Palette, 
  Shield, 
  Database,
  Zap,
  Save,
  RefreshCw,
  ToggleLeft,
  ToggleRight,
  ChevronRight
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

// ==================== SETTINGS SECTION ====================
const SettingsSection = ({ icon: Icon, title, description, children }) => (
  <Card className="glass border-white/10">
    <CardHeader className="pb-3">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-sm bg-primary/10">
          <Icon className="w-5 h-5 text-primary" />
        </div>
        <div>
          <CardTitle className="font-heading text-base">{title}</CardTitle>
          <CardDescription className="text-xs">{description}</CardDescription>
        </div>
      </div>
    </CardHeader>
    <CardContent className="space-y-4">
      {children}
    </CardContent>
  </Card>
);

// ==================== SETTING ROW ====================
const SettingRow = ({ label, description, children }) => (
  <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-0">
    <div>
      <p className="text-sm font-medium">{label}</p>
      {description && <p className="text-xs text-muted-foreground">{description}</p>}
    </div>
    {children}
  </div>
);

// ==================== MAIN SETTINGS PAGE ====================
export default function SettingsPage() {
  const [settings, setSettings] = useState({
    // Notifications
    notifyOnTrade: true,
    notifyOnReplication: true,
    notifyOnRisk: true,
    notifyOnOpportunity: true,
    emailNotifications: false,
    
    // Agent defaults
    defaultCapital: 100,
    defaultRiskLevel: "medium",
    autoReplicate: true,
    replicationThreshold: 50,
    autoTerminate: true,
    terminationThreshold: 1,
    
    // Trading
    maxConcurrentTrades: 5,
    defaultPositionSize: 5,
    stopLossDefault: 2,
    takeProfitDefault: 5,
    
    // System
    refreshInterval: 30,
    dataRetentionDays: 90,
    debugMode: false
  });

  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    // Simulate save
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success("Ajustes guardados correctamente");
    setSaving(false);
  };

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-6" data-testid="settings-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide uppercase">
            Ajustes
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Configura preferencias del sistema y valores por defecto
          </p>
        </div>
        
        <Button 
          onClick={handleSave}
          disabled={saving}
          className="bg-primary text-black hover:bg-primary/90"
        >
          {saving ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Save className="w-4 h-4 mr-2" />
          )}
          Guardar Cambios
        </Button>
      </div>

      <Tabs defaultValue="notifications" className="space-y-6">
        <TabsList className="bg-white/5 border border-white/10">
          <TabsTrigger value="notifications" className="data-[state=active]:bg-primary/20">
            <Bell className="w-4 h-4 mr-2" />
            Notificaciones
          </TabsTrigger>
          <TabsTrigger value="agents" className="data-[state=active]:bg-primary/20">
            <Bot className="w-4 h-4 mr-2" />
            Agentes
          </TabsTrigger>
          <TabsTrigger value="trading" className="data-[state=active]:bg-primary/20">
            <Zap className="w-4 h-4 mr-2" />
            Trading
          </TabsTrigger>
          <TabsTrigger value="system" className="data-[state=active]:bg-primary/20">
            <Database className="w-4 h-4 mr-2" />
            Sistema
          </TabsTrigger>
        </TabsList>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <SettingsSection
            icon={Bell}
            title="Preferencias de Notificación"
            description="Controla qué eventos generan notificaciones"
          >
            <SettingRow 
              label="Notificaciones de Trade" 
              description="Notificar al abrir/cerrar trades"
            >
              <Switch 
                checked={settings.notifyOnTrade}
                onCheckedChange={(checked) => updateSetting('notifyOnTrade', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Eventos de Replicación" 
              description="Notificar cuando los agentes se replican"
            >
              <Switch 
                checked={settings.notifyOnReplication}
                onCheckedChange={(checked) => updateSetting('notifyOnReplication', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Alertas de Riesgo" 
              description="Notificar cuando los agentes están en riesgo"
            >
              <Switch 
                checked={settings.notifyOnRisk}
                onCheckedChange={(checked) => updateSetting('notifyOnRisk', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Alertas de Oportunidad" 
              description="Notificar oportunidades de trading detectadas"
            >
              <Switch 
                checked={settings.notifyOnOpportunity}
                onCheckedChange={(checked) => updateSetting('notifyOnOpportunity', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Notificaciones por Email" 
              description="Enviar notificaciones por email (requiere configuración)"
            >
              <Switch 
                checked={settings.emailNotifications}
                onCheckedChange={(checked) => updateSetting('emailNotifications', checked)}
                disabled
              />
            </SettingRow>
          </SettingsSection>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-6">
          <SettingsSection
            icon={Bot}
            title="Configuración de Agentes"
            description="Ajustes por defecto para nuevos agentes"
          >
            <SettingRow label="Capital Inicial por Defecto">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">$</span>
                <Input
                  type="number"
                  value={settings.defaultCapital}
                  onChange={(e) => updateSetting('defaultCapital', parseFloat(e.target.value))}
                  className="w-24 bg-black/50 border-white/10"
                />
              </div>
            </SettingRow>
            
            <SettingRow label="Nivel de Riesgo por Defecto">
              <Select 
                value={settings.defaultRiskLevel}
                onValueChange={(value) => updateSetting('defaultRiskLevel', value)}
              >
                <SelectTrigger className="w-32 bg-black/50 border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glass border-white/10">
                  <SelectItem value="low">Bajo</SelectItem>
                  <SelectItem value="medium">Medio</SelectItem>
                  <SelectItem value="high">Alto</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
          </SettingsSection>

          <SettingsSection
            icon={Zap}
            title="Auto-Replicación"
            description="Configurar replicación automática de agentes"
          >
            <SettingRow 
              label="Habilitar Auto-Replicación" 
              description="Replicar automáticamente agentes exitosos"
            >
              <Switch 
                checked={settings.autoReplicate}
                onCheckedChange={(checked) => updateSetting('autoReplicate', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Umbral de Replicación" 
              description={`Replicar cuando ROI alcance ${settings.replicationThreshold}%`}
            >
              <div className="flex items-center gap-4 w-48">
                <Slider
                  value={[settings.replicationThreshold]}
                  onValueChange={([value]) => updateSetting('replicationThreshold', value)}
                  min={10}
                  max={100}
                  step={5}
                  className="flex-1"
                />
                <span className="text-sm font-mono w-12 text-right">
                  {settings.replicationThreshold}%
                </span>
              </div>
            </SettingRow>
          </SettingsSection>

          <SettingsSection
            icon={Shield}
            title="Auto-Terminación"
            description="Configurar terminación automática de agentes"
          >
            <SettingRow 
              label="Habilitar Auto-Terminación" 
              description="Terminar automáticamente agentes que fallen"
            >
              <Switch 
                checked={settings.autoTerminate}
                onCheckedChange={(checked) => updateSetting('autoTerminate', checked)}
              />
            </SettingRow>
            
            <SettingRow label="Balance de Terminación">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">$</span>
                <Input
                  type="number"
                  value={settings.terminationThreshold}
                  onChange={(e) => updateSetting('terminationThreshold', parseFloat(e.target.value))}
                  className="w-24 bg-black/50 border-white/10"
                />
              </div>
            </SettingRow>
          </SettingsSection>
        </TabsContent>

        {/* Trading Tab */}
        <TabsContent value="trading" className="space-y-6">
          <SettingsSection
            icon={Zap}
            title="Configuración de Trading"
            description="Parámetros por defecto para trades"
          >
            <SettingRow label="Trades Concurrentes Máx.">
              <Input
                type="number"
                value={settings.maxConcurrentTrades}
                onChange={(e) => updateSetting('maxConcurrentTrades', parseInt(e.target.value))}
                className="w-24 bg-black/50 border-white/10"
              />
            </SettingRow>
            
            <SettingRow 
              label="Tamaño de Posición" 
              description={`${settings.defaultPositionSize}% del balance disponible`}
            >
              <div className="flex items-center gap-4 w-48">
                <Slider
                  value={[settings.defaultPositionSize]}
                  onValueChange={([value]) => updateSetting('defaultPositionSize', value)}
                  min={1}
                  max={20}
                  step={1}
                  className="flex-1"
                />
                <span className="text-sm font-mono w-12 text-right">
                  {settings.defaultPositionSize}%
                </span>
              </div>
            </SettingRow>
            
            <SettingRow label="Stop Loss por Defecto">
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  value={settings.stopLossDefault}
                  onChange={(e) => updateSetting('stopLossDefault', parseFloat(e.target.value))}
                  className="w-20 bg-black/50 border-white/10"
                />
                <span className="text-muted-foreground">%</span>
              </div>
            </SettingRow>
            
            <SettingRow label="Take Profit por Defecto">
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  value={settings.takeProfitDefault}
                  onChange={(e) => updateSetting('takeProfitDefault', parseFloat(e.target.value))}
                  className="w-20 bg-black/50 border-white/10"
                />
                <span className="text-muted-foreground">%</span>
              </div>
            </SettingRow>
          </SettingsSection>
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system" className="space-y-6">
          <SettingsSection
            icon={Database}
            title="Configuración del Sistema"
            description="Ajustes generales del sistema"
          >
            <SettingRow label="Intervalo de Actualización">
              <Select 
                value={String(settings.refreshInterval)}
                onValueChange={(value) => updateSetting('refreshInterval', parseInt(value))}
              >
                <SelectTrigger className="w-32 bg-black/50 border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glass border-white/10">
                  <SelectItem value="10">10 segundos</SelectItem>
                  <SelectItem value="30">30 segundos</SelectItem>
                  <SelectItem value="60">1 minuto</SelectItem>
                  <SelectItem value="300">5 minutos</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
            
            <SettingRow label="Retención de Datos">
              <Select 
                value={String(settings.dataRetentionDays)}
                onValueChange={(value) => updateSetting('dataRetentionDays', parseInt(value))}
              >
                <SelectTrigger className="w-32 bg-black/50 border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glass border-white/10">
                  <SelectItem value="30">30 días</SelectItem>
                  <SelectItem value="90">90 días</SelectItem>
                  <SelectItem value="180">180 días</SelectItem>
                  <SelectItem value="365">1 año</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
            
            <SettingRow 
              label="Modo Debug" 
              description="Habilitar logging detallado"
            >
              <Switch 
                checked={settings.debugMode}
                onCheckedChange={(checked) => updateSetting('debugMode', checked)}
              />
            </SettingRow>
          </SettingsSection>

          <SettingsSection
            icon={Shield}
            title="Zona de Peligro"
            description="Acciones irreversibles"
          >
            <div className="space-y-3">
              <Button 
                variant="outline" 
                className="w-full justify-between border-destructive/30 text-destructive hover:bg-destructive/10"
              >
                Restablecer Ajustes
                <ChevronRight className="w-4 h-4" />
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-between border-destructive/30 text-destructive hover:bg-destructive/10"
              >
                Borrar Todos los Datos
                <ChevronRight className="w-4 h-4" />
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-between border-destructive/30 text-destructive hover:bg-destructive/10"
              >
                Terminar Todos los Agentes
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </SettingsSection>
        </TabsContent>
      </Tabs>
    </div>
  );
}
