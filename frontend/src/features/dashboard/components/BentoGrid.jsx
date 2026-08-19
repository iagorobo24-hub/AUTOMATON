import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from "@/components/ui/card";
import { Activity, Bot, HeartPulse, TrendingUp } from "lucide-react";
import { agentsAPI, healthAPI, tradesAPI } from "@/lib/api";

export function normalizeDashboardData(agents = [], tradeStats = {}, health = {}) {
  const activeAgents = agents.filter((agent) => agent.estado === 'ACTIVO').length;
  const deadAgents = agents.filter((agent) => agent.estado === 'MUERTO').length;
  const replicatedAgents = agents.filter((agent) => agent.estado === 'REPLICADO').length;
  const evidenceValid = tradeStats.evidence_valid === true;

  return {
    totalAgents: agents.length,
    activeAgents,
    deadAgents,
    replicatedAgents,
    totalTrades: evidenceValid && tradeStats.total_trades != null ? Number(tradeStats.total_trades) : null,
    closedTrades: evidenceValid && tradeStats.trades_cerrados != null ? Number(tradeStats.trades_cerrados) : null,
    profitTotal: evidenceValid && tradeStats.profit_total != null ? Number(tradeStats.profit_total) : null,
    winRatePercent: evidenceValid && tradeStats.win_rate_percent != null ? Number(tradeStats.win_rate_percent) : null,
    legacyRecords: Number(tradeStats.legacy_records ?? 0),
    evidenceValid,
    evidenceMode: tradeStats.evidence_mode || 'unknown',
    runtimeMode: health.runtime_mode || 'unknown',
    syntheticDisabled: health.synthetic_engine === 'disabled',
    riskMode: health.risk || 'unknown',
    paperTrading: health.paper_trading || 'unknown',
  };
}

function metricValue(value, formatter) {
  return value == null ? 'N/D' : formatter(value);
}

export function BentoGrid() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['dashboard-runtime'],
    queryFn: async () => {
      const [agentsResponse, statsResponse, healthResponse] = await Promise.all([
        agentsAPI.list(),
        tradesAPI.stats(),
        healthAPI.health(),
      ]);
      return normalizeDashboardData(
        Array.isArray(agentsResponse.data) ? agentsResponse.data : [],
        statsResponse.data || {},
        healthResponse.data || {},
      );
    },
    refetchInterval: 10000,
  });

  const metrics = data || normalizeDashboardData();
  const runtimeLabel = isLoading
    ? 'Consultando'
    : isError
      ? 'Desconocido'
      : metrics.paperTrading === 'operator_only_phase_4' && metrics.riskMode === 'authoritative_phase_4'
        ? 'Paper operador · Risk activo'
        : metrics.syntheticDisabled
          ? 'Transición · sintético desactivado'
          : 'Revisar runtime';
  const cards = [
    { title: 'Win Rate verificable', value: metricValue(metrics.winRatePercent, (v) => `${v.toFixed(1)}%`), icon: TrendingUp },
    { title: 'PnL verificable', value: metricValue(metrics.profitTotal, (v) => `€${v.toFixed(2)}`), icon: Activity },
    { title: 'Agentes activos', value: String(metrics.activeAgents), icon: Bot },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-[#0e1511]">
      <Card className="md:col-span-3 md:row-span-2 p-6 min-h-[300px]">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Runtime Paper de transición</h3>
            <p className="text-[10px] text-gray-500 font-mono mt-1">Paper manual con Risk obligatorio · métricas legacy excluidas · automatización de estrategias aún desactivada</p>
          </div>
          <span className="font-mono text-[#3b82f6] text-lg font-bold">{metrics.totalTrades == null ? 'N/D trades válidos' : `${metrics.totalTrades} trades`}</span>
        </div>
        {isLoading ? (
          <p className="text-sm text-gray-500 font-mono">Consultando runtime…</p>
        ) : isError ? (
          <p className="text-sm text-red-400 font-mono">No se pudo cargar el resumen del runtime.</p>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card rounded-lg p-4"><p className="text-xs text-gray-500 uppercase">Agentes totales</p><p className="text-2xl font-mono text-gray-200 mt-2">{metrics.totalAgents}</p></div>
            <div className="glass-card rounded-lg p-4"><p className="text-xs text-gray-500 uppercase">Trades verificables</p><p className="text-2xl font-mono text-gray-200 mt-2">{metrics.closedTrades == null ? 'N/D' : metrics.closedTrades}</p></div>
            <div className="glass-card rounded-lg p-4"><p className="text-xs text-gray-500 uppercase">Replicados</p><p className="text-2xl font-mono text-gray-200 mt-2">{metrics.replicatedAgents}</p></div>
            <div className="glass-card rounded-lg p-4"><p className="text-xs text-gray-500 uppercase">Legacy sin clasificar</p><p className="text-2xl font-mono text-gray-200 mt-2">{metrics.legacyRecords}</p></div>
          </div>
        )}
      </Card>

      {cards.map(({ title, value, icon: Icon }) => (
        <Card key={title} className="p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-[10px] uppercase tracking-wider font-semibold">{title}</span>
            <Icon className="w-4 h-4 text-[#3b82f6]/70" />
          </div>
          <div className="font-mono text-2xl font-bold tracking-tighter text-[#3b82f6] mt-4">{value}</div>
        </Card>
      ))}

      <Card className="p-4 bg-[#3b82f6]/5 border-[#3b82f6]/20 flex flex-col justify-center items-center gap-2">
        <HeartPulse className="w-4 h-4 text-[#3b82f6]" />
        <div className="text-[10px] uppercase tracking-widest text-gray-400">Runtime</div>
        <span className="text-xs font-mono text-gray-200 text-center">{runtimeLabel}</span>
      </Card>
    </div>
  );
}
