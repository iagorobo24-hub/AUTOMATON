import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from "@/components/ui/card";
import { Activity, RefreshCw } from "lucide-react";
import { tradesAPI } from "@/lib/api";

export function normalizeTradeFeed(rawTrades = []) {
  return rawTrades.map((trade) => ({
    id: trade.id,
    agentId: trade.agente_id,
    type: trade.tipo || 'UNKNOWN',
    entry: Number(trade.precio_entrada ?? 0),
    exit: trade.precio_salida == null ? null : Number(trade.precio_salida),
    amount: Number(trade.cantidad ?? 0),
    pnl: trade.resultado == null ? null : Number(trade.resultado),
    timestamp: trade.timestamp || null,
    status: trade.precio_salida == null ? 'OPEN' : 'CLOSED',
    evidenceMode: trade.evidence_mode || 'unknown',
    evidenceValid: trade.evidence_valid === true,
  }));
}

export function LiveTradeFeed() {
  const { data = [], isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['trades-feed'],
    queryFn: async () => {
      const response = await tradesAPI.list({ limit: 50 });
      return normalizeTradeFeed(Array.isArray(response.data) ? response.data : []);
    },
    refetchInterval: 5000,
  });

  return (
    <Card className="flex flex-col h-full bg-[#0e1511] border-[#3c4a42] overflow-hidden">
      <div className="p-4 border-b border-[#3c4a42] flex items-center justify-between bg-[#141b17]">
        <div className="flex items-center gap-3">
          <Activity className="w-4 h-4 text-[#3b82f6]" />
          <div>
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Registros históricos</h3>
            <p className="text-[9px] text-gray-500 font-mono mt-1">Legacy sin procedencia verificable · no son evidencia Paper</p>
          </div>
        </div>
        <button onClick={() => refetch()} disabled={isFetching} className="evo-button-outline px-3 py-2 text-xs" aria-label="Actualizar registros">
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {isLoading ? (
        <div className="p-6 text-sm text-gray-500 font-mono">Consultando registros…</div>
      ) : isError ? (
        <div className="p-6 text-sm text-red-400 font-mono">No se pudieron cargar los registros.</div>
      ) : data.length === 0 ? (
        <div className="p-10 text-center text-sm text-gray-500">No hay registros persistidos.</div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-[#0e1511] text-[10px] text-gray-500 uppercase tracking-widest border-b border-[#3c4a42]">
              <tr>
                <th className="px-4 py-3">Agente</th>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3 text-right">Entrada</th>
                <th className="px-4 py-3 text-right">Salida</th>
                <th className="px-4 py-3 text-right">PnL histórico</th>
                <th className="px-4 py-3 text-right">Evidencia</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#3c4a42]/30">
              {data.map((trade) => (
                <tr key={trade.id} className="hover:bg-[#1a211d] transition-colors">
                  <td className="px-4 py-4 font-mono text-sm text-gray-200">#{trade.agentId}</td>
                  <td className="px-4 py-4 font-mono text-xs text-gray-400">{trade.type}</td>
                  <td className="px-4 py-4 text-right font-mono text-xs text-gray-200">{trade.entry.toFixed(2)}</td>
                  <td className="px-4 py-4 text-right font-mono text-xs text-gray-200">{trade.exit == null ? '—' : trade.exit.toFixed(2)}</td>
                  <td className="px-4 py-4 text-right font-mono text-sm text-gray-500">{trade.pnl == null ? '—' : `${trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}`}</td>
                  <td className="px-4 py-4 text-right"><span className="text-[10px] font-mono text-amber-400">{trade.evidenceValid ? trade.evidenceMode : 'NO VÁLIDA'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
