import { useState } from 'react';
import { Save, RefreshCw, Cog, Bell, Shield } from 'lucide-react';

import Layout from '../components/layout/Layout';

export default function Settings() {
  const [settings, setSettings] = useState({
    refreshInterval: 5,
    notifications: true,
    autoStart: false,
    apiEndpoint: 'http://localhost:8000',
    logLevel: 'info',
  });

  const handleSave = () => {
    // In production, save to backend or localStorage
    console.log('Saving settings:', settings);
    alert('Settings saved!');
  };

  const headerActions = (
    <button onClick={handleSave} className="btn-primary">
      <Save className="h-4 w-4 mr-2" />
      Save Changes
    </button>
  );

  return (
    <Layout actions={headerActions}>
      <div className="max-w-2xl space-y-6">
        {/* General Settings */}
        <div className="app-card">
          <div className="flex items-center gap-3 mb-6">
            <Cog className="h-5 w-5 text-[var(--accent)]" />
            <h3 className="text-lg font-semibold text-[var(--text-primary)]">General</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">
                Refresh Interval (seconds)
              </label>
              <input
                type="number"
                value={settings.refreshInterval}
                onChange={(e) => setSettings({ ...settings, refreshInterval: parseInt(e.target.value) })}
                min="1"
                max="300"
                className="app-input w-32"
              />
            </div>

            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">
                API Endpoint
              </label>
              <input
                type="text"
                value={settings.apiEndpoint}
                onChange={(e) => setSettings({ ...settings, apiEndpoint: e.target.value })}
                className="app-input"
              />
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="autoStart"
                checked={settings.autoStart}
                onChange={(e) => setSettings({ ...settings, autoStart: e.target.checked })}
                className="rounded border-[var(--border)] bg-[var(--bg-elevated)]"
              />
              <label htmlFor="autoStart" className="text-sm text-[var(--text-secondary)]">
                Auto-start agents on system boot
              </label>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="app-card">
          <div className="flex items-center gap-3 mb-6">
            <Bell className="h-5 w-5 text-[var(--accent)]" />
            <h3 className="text-lg font-semibold text-[var(--text-primary)]">Notifications</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="notifications"
                checked={settings.notifications}
                onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
                className="rounded border-[var(--border)] bg-[var(--bg-elevated)]"
              />
              <label htmlFor="notifications" className="text-sm text-[var(--text-secondary)]">
                Enable push notifications
              </label>
            </div>

            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">
                Log Level
              </label>
              <select
                value={settings.logLevel}
                onChange={(e) => setSettings({ ...settings, logLevel: e.target.value })}
                className="app-input w-40"
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warn">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
        </div>

        {/* System */}
        <div className="app-card">
          <div className="flex items-center gap-3 mb-6">
            <RefreshCw className="h-5 w-5 text-[var(--accent)]" />
            <h3 className="text-lg font-semibold text-[var(--text-primary)]">System</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[var(--text-primary)]">Clear Cache</p>
                <p className="text-xs text-[var(--text-muted)]">Remove temporary files and reset UI state</p>
              </div>
              <button 
                onClick={() => confirm('Clear all cache?') && console.log('Cache cleared')}
                className="btn-ghost"
              >
                Clear
              </button>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-[var(--border-subtle)]">
              <div>
                <p className="text-sm text-[var(--text-primary)]">Reset Configuration</p>
                <p className="text-xs text-[var(--destructive)]">Warning: This will reset all settings to default</p>
              </div>
              <button 
                onClick={() => confirm('Reset all settings to default?') && console.log('Settings reset')}
                className="btn-ghost text-[var(--destructive)] hover:text-[var(--destructive)]"
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        {/* Version Info */}
        <div className="text-center text-sm text-[var(--text-muted)]">
          AUTOMATON v2.2.0
        </div>
      </div>
    </Layout>
  );
}
