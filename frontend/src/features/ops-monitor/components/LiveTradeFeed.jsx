import React, { useState, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { useTradingSocket } from "@/shared/hooks/useTradingSocket";
import { ArrowUpRight, ArrowDownRight, Zap, ListFilter } from "lucide-react";

export function LiveTradeFeed() {
  const { isConnected, lastMessage } = useTradingSocket();
  const [trades, setTrades] = useState([
    { id: 1, pair: "BTC/USDT", type: "LONG", entry: 64200.50, current: 65100.20, amount: "0.45", pnl: 2.4, status: "ACTIVE" },
    { id: 2, pair: "ETH/USDT", type: "SHORT", entry: 3450.10, current: 3410.50, amount: "12.5", pnl: 1.2, status: "ACTIVE" },
    { id: 3, pair: "SOL/USDT", type: "LONG", entry: 145.20, current: 142.10, amount: "150.0", pnl: -2.1, status: "ACTIVE" },
    { id: 4, pair: "LINK/USDT", type: "LONG", entry: 18.50, current: 19.10, amount: "450.0", pnl: 3.2, status: "ACTIVE" },
  ]);

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'MARKET_UPDATE') {
      const { pair, price } = lastMessage.data || {};
      if (pair && price) {
        setTrades(prev => prev.map(trade => {
          if (trade.pair === pair) {
            const pnlValue = trade.type === 'LONG' 
              ? ((price - trade.entry) / trade.entry) * 100
              : ((trade.entry - price) / trade.entry) * 100;
            return { ...trade, current: price, pnl: pnlValue };
          }
          return trade;
        }));
      }
    }
    
    if (lastMessage && lastMessage.type === 'TRADE_UPDATE') {
      const newTrade = lastMessage.data;
      if (newTrade && newTrade.id) {
        setTrades(prev => {
          const exists = prev.find(t => t.id === newTrade.id);
          if (exists) {
            return prev.map(t => t.id === newTrade.id ? { ...t, ...newTrade } : t);
          }
          return [newTrade, ...prev].slice(0, 10);
        });
      }
    }
  }, [lastMessage]);

  return (
    <Card className="flex flex-col h-full bg-[#0e1511] border-[#3c4a42] overflow-hidden">
      <div className="p-4 border-b border-[#3c4a42] flex items-center justify-between bg-[#141b17]">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Zap className={`w-4 h-4 ${isConnected ? 'text-[#3b82f6]' : 'text-orange-500'}`} />
            {isConnected && (
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-[#3b82f6] rounded-full animate-ping" />
            )}
          </div>
          <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Live Operations Monitor</h3>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 px-2 py-0.5 border border-[#3c4a42] bg-[#0e1511]">
             <ListFilter className="w-3 h-3 text-gray-500" />
             <span className="text-[9px] font-mono text-gray-500 uppercase">Filter</span>
          </div>
          <div className="text-[9px] font-mono font-bold text-[#3b82f6] bg-[#3b82f6]/10 px-2 py-0.5">
            {isConnected ? 'LIVE_STREAM' : 'RECONNECTING...'}
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-[#3c4a42] scrollbar-track-transparent">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 bg-[#0e1511] text-[10px] text-gray-500 uppercase tracking-widest border-b border-[#3c4a42] z-10">
            <tr>
              <th className="px-4 py-3 font-semibold">Asset / Position</th>
              <th className="px-4 py-3 font-semibold">Strategy</th>
              <th className="px-4 py-3 font-semibold text-right">Entry / Current</th>
              <th className="px-4 py-3 font-semibold text-right">PnL Latent</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#3c4a42]/30">
            {trades.map((trade) => (
              <tr key={trade.id} className="hover:bg-[#1a211d] group transition-all duration-200">
                <td className="px-4 py-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-1 h-8 ${trade.type === 'LONG' ? 'bg-[#3b82f6]' : 'bg-red-500'}`} />
                    <div>
                      <div className="font-bold text-sm text-gray-200 tracking-tight">{trade.pair}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-[9px] font-mono px-1 py-0.5 rounded-sm ${
                          trade.type === 'LONG' ? 'bg-[#3b82f6]/10 text-[#3b82f6]' : 'bg-red-500/10 text-red-500'
                        }`}>
                          {trade.type}
                        </span>
                        <span className="text-[9px] font-mono text-gray-500 uppercase">{trade.amount} UNITS</span>
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] font-mono text-gray-400 uppercase tracking-tighter">Alpha_V2</span>
                    <span className="text-[9px] font-mono text-[#3b82f6]/60 uppercase">High_Freq</span>
                  </div>
                </td>
                <td className="px-4 py-4 text-right">
                  <div className="font-mono text-xs text-gray-200 font-medium">
                    {trade.current.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-[10px] font-mono text-gray-500 mt-1">
                    ENTRY: {trade.entry.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </div>
                </td>
                <td className="px-4 py-4 text-right">
                  <div className={`font-mono text-sm font-bold flex items-center justify-end gap-1.5 ${
                    trade.pnl >= 0 ? 'text-[#3b82f6]' : 'text-red-500'
                  }`}>
                    <span className="text-xs">{trade.pnl >= 0 ? '+' : ''}</span>
                    {trade.pnl.toFixed(2)}%
                    {trade.pnl >= 0 ? 
                      <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" /> : 
                      <ArrowDownRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:translate-y-0.5 transition-transform" />
                    }
                  </div>
                  <div className="text-[9px] font-mono text-gray-500 mt-1 uppercase tracking-tighter">
                    Real-time delta
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="p-3 border-t border-[#3c4a42] bg-[#141b17] flex items-center justify-between">
        <div className="text-[9px] font-mono text-gray-500 uppercase tracking-widest">
          Active Ops: {trades.length}
        </div>
        <div className="text-[9px] font-mono text-[#3b82f6]/70 uppercase tracking-widest animate-pulse">
          Listening for AGENT_EVENTS...
        </div>
      </div>
    </Card>
  );
}
