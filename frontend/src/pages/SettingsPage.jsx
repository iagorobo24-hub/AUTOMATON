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
    toast.success("Settings saved successfully");
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
            Settings
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Configure system preferences and defaults
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
          Save Changes
        </Button>
      </div>

      <Tabs defaultValue="notifications" className="space-y-6">
        <TabsList className="bg-white/5 border border-white/10">
          <TabsTrigger value="notifications" className="data-[state=active]:bg-primary/20">
            <Bell className="w-4 h-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="agents" className="data-[state=active]:bg-primary/20">
            <Bot className="w-4 h-4 mr-2" />
            Agents
          </TabsTrigger>
          <TabsTrigger value="trading" className="data-[state=active]:bg-primary/20">
            <Zap className="w-4 h-4 mr-2" />
            Trading
          </TabsTrigger>
          <TabsTrigger value="system" className="data-[state=active]:bg-primary/20">
            <Database className="w-4 h-4 mr-2" />
            System
          </TabsTrigger>
        </TabsList>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <SettingsSection
            icon={Bell}
            title="Notification Preferences"
            description="Control which events trigger notifications"
          >
            <SettingRow 
              label="Trade Notifications" 
              description="Notify on trade open/close events"
            >
              <Switch 
                checked={settings.notifyOnTrade}
                onCheckedChange={(checked) => updateSetting('notifyOnTrade', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Replication Events" 
              description="Notify when agents replicate"
            >
              <Switch 
                checked={settings.notifyOnReplication}
                onCheckedChange={(checked) => updateSetting('notifyOnReplication', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Risk Alerts" 
              description="Notify when agents are at risk"
            >
              <Switch 
                checked={settings.notifyOnRisk}
                onCheckedChange={(checked) => updateSetting('notifyOnRisk', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Opportunity Alerts" 
              description="Notify on detected trading opportunities"
            >
              <Switch 
                checked={settings.notifyOnOpportunity}
                onCheckedChange={(checked) => updateSetting('notifyOnOpportunity', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Email Notifications" 
              description="Send notifications to email (requires setup)"
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
            title="Agent Defaults"
            description="Default settings for new agents"
          >
            <SettingRow label="Default Initial Capital">
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
            
            <SettingRow label="Default Risk Level">
              <Select 
                value={settings.defaultRiskLevel}
                onValueChange={(value) => updateSetting('defaultRiskLevel', value)}
              >
                <SelectTrigger className="w-32 bg-black/50 border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glass border-white/10">
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
          </SettingsSection>

          <SettingsSection
            icon={Zap}
            title="Auto-Replication"
            description="Configure automatic agent replication"
          >
            <SettingRow 
              label="Enable Auto-Replication" 
              description="Automatically replicate successful agents"
            >
              <Switch 
                checked={settings.autoReplicate}
                onCheckedChange={(checked) => updateSetting('autoReplicate', checked)}
              />
            </SettingRow>
            
            <SettingRow 
              label="Replication Threshold" 
              description={`Replicate when ROI reaches ${settings.replicationThreshold}%`}
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
            title="Auto-Termination"
            description="Configure automatic agent termination"
          >
            <SettingRow 
              label="Enable Auto-Termination" 
              description="Automatically terminate failing agents"
            >
              <Switch 
                checked={settings.autoTerminate}
                onCheckedChange={(checked) => updateSetting('autoTerminate', checked)}
              />
            </SettingRow>
            
            <SettingRow label="Termination Balance">
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
            title="Trading Defaults"
            description="Default parameters for trades"
          >
            <SettingRow label="Max Concurrent Trades">
              <Input
                type="number"
                value={settings.maxConcurrentTrades}
                onChange={(e) => updateSetting('maxConcurrentTrades', parseInt(e.target.value))}
                className="w-24 bg-black/50 border-white/10"
              />
            </SettingRow>
            
            <SettingRow 
              label="Default Position Size" 
              description={`${settings.defaultPositionSize}% of available balance`}
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
            
            <SettingRow label="Default Stop Loss">
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
            
            <SettingRow label="Default Take Profit">
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
            title="System Configuration"
            description="General system settings"
          >
            <SettingRow label="Data Refresh Interval">
              <Select 
                value={String(settings.refreshInterval)}
                onValueChange={(value) => updateSetting('refreshInterval', parseInt(value))}
              >
                <SelectTrigger className="w-32 bg-black/50 border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glass border-white/10">
                  <SelectItem value="10">10 seconds</SelectItem>
                  <SelectItem value="30">30 seconds</SelectItem>
                  <SelectItem value="60">1 minute</SelectItem>
                  <SelectItem value="300">5 minutes</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
            
            <SettingRow label="Data Retention">
              <Select 
                value={String(settings.dataRetentionDays)}
                onValueChange={(value) => updateSetting('dataRetentionDays', parseInt(value))}
              >
                <SelectTrigger className="w-32 bg-black/50 border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glass border-white/10">
                  <SelectItem value="30">30 days</SelectItem>
                  <SelectItem value="90">90 days</SelectItem>
                  <SelectItem value="180">180 days</SelectItem>
                  <SelectItem value="365">1 year</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
            
            <SettingRow 
              label="Debug Mode" 
              description="Enable verbose logging"
            >
              <Switch 
                checked={settings.debugMode}
                onCheckedChange={(checked) => updateSetting('debugMode', checked)}
              />
            </SettingRow>
          </SettingsSection>

          <SettingsSection
            icon={Shield}
            title="Danger Zone"
            description="Irreversible actions"
          >
            <div className="space-y-3">
              <Button 
                variant="outline" 
                className="w-full justify-between border-destructive/30 text-destructive hover:bg-destructive/10"
              >
                Reset All Settings
                <ChevronRight className="w-4 h-4" />
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-between border-destructive/30 text-destructive hover:bg-destructive/10"
              >
                Clear All Data
                <ChevronRight className="w-4 h-4" />
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-between border-destructive/30 text-destructive hover:bg-destructive/10"
              >
                Terminate All Agents
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </SettingsSection>
        </TabsContent>
      </Tabs>
    </div>
  );
}
