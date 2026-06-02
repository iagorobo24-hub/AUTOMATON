import React from 'react';
import { Card } from "@/components/ui/card";
import { TrendingUp, Activity, Users, PieChart } from "lucide-react";

const KPI_DATA = [
  {
    title: "Win Rate",
    value: "68.5%",
    change: "+2.4%",
    icon: TrendingUp,
    color: "text-[#3b82f6]"
  },
  {
    title: "PnL 24h",
    value: "+$1,240.50",
    change: "+12.3%",
    icon: Activity,
    color: "text-[#3b82f6]"
  },
  {
    title: "Agentes Activos",
    value: "14",
    change: "Live",
    icon: Users,
    color: "text-[#3b82f6]"
  }
];

export function BentoGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-[#0e1511]">
      {/* Portfolio Chart - Large Area */}
      <Card className="md:col-span-3 md:row-span-2 p-6 flex flex-col min-h-[300px]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <PieChart className="w-5 h-5 text-[#3b82f6]" />
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Portfolio Performance</h3>
          </div>
          <span className="font-mono text-[#3b82f6] text-lg font-bold">+$5,240.00</span>
        </div>
        
        {/* Placeholder for Chart */}
        <div className="flex-1 border border-dashed border-[#3c4a42] flex items-center justify-center bg-[#141b17]/50">
          <div className="text-center">
            <div className="text-gray-500 font-mono text-xs uppercase tracking-widest mb-2">
              Portfolio History API
            </div>
            <div className="text-[10px] text-[#3b82f6]/40 font-mono">
              CONNECTING_STREAM...
            </div>
          </div>
        </div>
      </Card>

      {/* KPI Cards */}
      {KPI_DATA.map((kpi, index) => (
        <Card key={index} className="p-4 flex flex-col justify-between hover:border-[#3b82f6]/50 transition-colors">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-[10px] uppercase tracking-wider font-semibold">{kpi.title}</span>
            <kpi.icon className="w-4 h-4 text-[#3b82f6]/70" />
          </div>
          <div className="mt-4">
            <div className={`font-mono text-2xl font-bold tracking-tighter ${kpi.color}`}>
              {kpi.value}
            </div>
            <div className="text-[10px] font-mono mt-1 text-gray-500 uppercase tracking-tighter flex items-center gap-1">
              <span className="w-1 h-1 rounded-full bg-current animate-pulse" />
              {kpi.change}
            </div>
          </div>
        </Card>
      ))}

      {/* Additional small slot for Bento feel - Status Card */}
      <Card className="p-4 bg-[#3b82f6]/5 border-[#3b82f6]/20 flex flex-col justify-center items-center gap-2">
        <div className="text-[#3b82f6] font-mono text-[10px] uppercase tracking-[0.2em] font-bold">
          System Health
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-[#0e1511] border border-[#3b82f6]/30 rounded-sm">
          <div className="w-2 h-2 rounded-full bg-[#3b82f6] shadow-[0_0_8px_#3b82f6]" />
          <span className="text-[10px] font-mono text-gray-300 font-bold uppercase tracking-widest">Optimal</span>
        </div>
      </Card>
    </div>
  );
}
