import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from "@/components/ui/card";
import { Activity, RefreshCw } from "lucide-react";
import { paperAPI } from "@/lib/api";

export function normalizePaperExecutions(rawExecutions = []) {
  return rawExecutions.map((execution) => ({
    id: execution.id,
    agentId: execution.agent_id ?? null,
    symbol: execution.symbol || 'UNKNOWN',
    side: execution.side || 'UNKNOWN',
    quantity: Number(execution.requested_quantity ?? 0),
    provider: execution.provider || 'unknown',
    marketPrice: Number(execution.market_price ?? 0),
    fillPrice: Number(execution.fill_price ?? 0),
    fee: Number(execution.fee ?? 0),
    status: execution.status || 'UNKNOWN',
    evidenceMode: execution.evidence_mode || 'unknown',
    policyVersion: execution.policy_version || 'unknown',
    observedAt: execution.quote_observed_at || null,
  }));
}

export function LiveTradeFeed() {
  const { data = [], isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['paper-executions-feed'],
    queryFn: async () => {
      const response = await paperAPI.executions({ limit: 50 });
      return normalizePaperExecutions(Array.isArray(response.data) ? response.data : []);
    },
    refetchInterval: 5000,
  });

  return (
    <Card className="flex flex-col h-full bg-[#0e1511] border-[#3c4a42] overflow-hidden">
      <div className="p-4 border-b border-[#3c4a42] flex items-center justify-between bg-[#141b17]">
        <div className="flex items-center gap-3">
          <Activity className="w-4 h-4 text-[#3b82f6]" />
          <div>
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Ejecuciones Paper</h3>
            <p className="text-[9px] text-gray-500 font-mono mt-1">PAPER · mercado real · capital virtual · policy paper-v1</p>
          </div>
        </div>
        <button onClick={() => refetch()} disabled={isFetching} className="evo-button-outline px-3 py-2 text-xs" aria-label="Actualizar ejecuciones Paper">
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {isLoading ? (
        <div className="p-6 text-sm text-gray-500 font-mono">Consultando ejecuciones Paper…</div>
      ) : isError ? (
        <div className="p-6 text-sm text-red-400 font-mono">No se pudieron cargar las ejecuciones Paper.</div>
      ) : data.length === 0 ? (
        <div className="p-10 text-center text-sm text-gray-500">Todavía no hay ejecuciones Paper persistidas.</div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-[#0e1511] text-[10px] text-gray-500 uppercase tracking-widest border-b border-[#3c4a42]">
              <tr>
                <th className="px-4 py-3">Agente</th>
                <th className="px-4 py-3">Mercado</th>
                <th className="px-4 py-3">Lado</th>
                <th className="px-4 py-3 text-right">Quote real</th>
                <th className="px-4 py-3 text-right">Fill Paper</th>
                <th className="px-4 py-3 text-right">Fee</th>
                <th className="px-4 py-3 text-right">Estado</th>
                <th className="px-4 py-3 text-right">Evidencia</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#3c4a42]/30">
              {data.map((execution) => (
                <tr key={execution.id} className="hover:bg-[#1a211d] transition-colors">
                  <td className="px-4 py-4 font-mono text-sm text-gray-200">{execution.agentId == null ? '—' : `#${execution.agentId}`}</td>
                  <td className="px-4 py-4 font-mono text-xs text-gray-300">
                    <div>{execution.symbol}</div>
                    <div className="text-[9px] text-gray-500 mt-1">{execution.provider}</div>
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-gray-300">{execution.side}</td>
                  <td className="px-4 py-4 text-right font-mono text-xs text-gray-200">{execution.marketPrice.toFixed(4)}</td>
                  <td className="px-4 py-4 text-right font-mono text-xs text-gray-200">{execution.fillPrice.toFixed(4)}</td>
                  <td className="px-4 py-4 text-right font-mono text-xs text-gray-400">{execution.fee.toFixed(4)}</td>
                  <td className="px-4 py-4 text-right font-mono text-xs text-gray-300">{execution.status}</td>
                  <td className="px-4 py-4 text-right">
                    <span className="text-[10px] font-mono text-blue-400">
                      {execution.evidenceMode === 'paper' ? 'PAPER · REAL' : 'NO VÁLIDA'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
