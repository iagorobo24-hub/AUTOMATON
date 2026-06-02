import React from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useMarketData } from '../hooks/useMarketData';
import { useQuickDeploy } from '../hooks/useQuickDeploy';

export function MarketGrid() {
  const { data: coins, isLoading, isError } = useMarketData();
  const { mutate: deploy, isPending: isDeploying } = useQuickDeploy();

  if (isLoading) {
    return <div className="p-8 text-center text-text-blue-500 animate-pulse font-mono">LOADING_TACTICAL_DATA...</div>;
  }

  if (isError) {
    return <div className="p-8 text-center text-red-400 font-mono">ERROR::CONNECTION_FAILED</div>;
  }

  return (
    <Card className="overflow-hidden">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-[#161d19] border-bottom border-[#3c4a42]">
            <th className="px-4 py-3 text-[10px] font-bold text-[#86948a] uppercase tracking-wider">Activo</th>
            <th className="px-4 py-3 text-[10px] font-bold text-[#86948a] uppercase tracking-wider text-right">Precio (USD)</th>
            <th className="px-4 py-3 text-[10px] font-bold text-[#86948a] uppercase tracking-wider text-right">24h %</th>
            <th className="px-4 py-3 text-[10px] font-bold text-[#86948a] uppercase tracking-wider text-center">RSI (14)</th>
            <th className="px-4 py-3 text-[10px] font-bold text-[#86948a] uppercase tracking-wider text-center">Agentes</th>
            <th className="px-4 py-3 text-[10px] font-bold text-[#86948a] uppercase tracking-wider text-center">Acción</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#3c4a42]">
          {coins?.map((coin) => (
            <tr key={coin.id} className="hover:bg-[#242c27] transition-colors group">
              <td className="px-4 py-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-[#3c4a42] flex items-center justify-center font-bold text-[10px] text-white">
                    {coin.symbol[0]}
                  </div>
                  <div>
                    <div className="font-bold text-text-blue-500 leading-none">{coin.symbol}</div>
                    <div className="text-[10px] text-[#86948a] uppercase mt-1">{coin.name}</div>
                  </div>
                </div>
              </td>
              <td className="px-4 py-4 text-right font-mono text-sm tracking-tighter">
                ${coin.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
              <td className={`px-4 py-4 text-right font-mono text-sm ${coin.change24h >= 0 ? 'text-text-blue-500' : 'text-red-400'}`}>
                {coin.change24h >= 0 ? '+' : ''}{coin.change24h.toFixed(2)}%
              </td>
              <td className="px-4 py-4 text-center">
                <span className={`px-2 py-0.5 rounded-sm text-[10px] font-bold uppercase ${
                  coin.rsi > 70 ? 'bg-red-400/10 text-red-400' : 
                  coin.rsi < 30 ? 'bg-text-blue-500/10 text-text-blue-500' : 
                  'bg-[#3c4a42]/20 text-[#86948a]'
                }`}>
                  {coin.rsi} {coin.rsi > 70 ? 'OVERBOUGHT' : coin.rsi < 30 ? 'OVERSOLD' : 'NEUTRAL'}
                </span>
              </td>
              <td className="px-4 py-4 text-center font-mono text-sm">
                {coin.activeAgents}
              </td>
              <td className="px-4 py-4 text-center">
                <Button 
                  variant="blue" 
                  className="text-[10px] py-1 px-3 h-auto"
                  onClick={() => deploy(coin.symbol)}
                  disabled={isDeploying}
                >
                  {isDeploying ? 'DEPLOYING...' : 'QUICK DEPLOY'}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
