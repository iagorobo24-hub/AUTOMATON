import React from 'react';
import { BentoGrid } from '@/features/dashboard/components/BentoGrid';

export default function DashboardPro() {
  return (
    <div className="p-6 space-y-6">
      <header className="flex justify-between items-center border-bottom border-border-pro pb-4">
        <div>
          <h1 className="text-2xl font-bold text-blue-pro tracking-tight uppercase">Dashboard Pro</h1>
          <p className="text-xs text-[#86948a] font-mono">SYSTEM_STATUS::OPERATIONAL</p>
        </div>
      </header>
      <BentoGrid />
    </div>
  );
}
