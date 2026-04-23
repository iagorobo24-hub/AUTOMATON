import React from 'react';
import { LiveTradeFeed } from '@/features/ops-monitor/components/LiveTradeFeed';

export default function OpsMonitorPro() {
  return (
    <div className="p-6 space-y-6">
      <header className="flex justify-between items-center border-bottom border-border-pro pb-4">
        <div>
          <h1 className="text-2xl font-bold text-emerald-pro tracking-tight uppercase">Monitor Operativo</h1>
          <p className="text-xs text-[#86948a] font-mono">LIVE_TELEMETRY::ACTIVE_TRADES</p>
        </div>
      </header>
      <LiveTradeFeed />
    </div>
  );
}
