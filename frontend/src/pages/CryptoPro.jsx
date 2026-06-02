import React from 'react';
import { MarketGrid } from '@/features/crypto/components/MarketGrid';

export default function CryptoPro() {
  return (
    <div className="p-6 space-y-6">
      <header className="flex justify-between items-center border-bottom border-border-pro pb-4">
        <div>
          <h1 className="text-2xl font-bold text-blue-pro tracking-tight uppercase">Terminal Táctica</h1>
          <p className="text-xs text-[#86948a] font-mono">MARKET_DATA::REALTIME_FEED</p>
        </div>
      </header>
      <MarketGrid />
    </div>
  );
}
