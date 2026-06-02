import { useState, useEffect } from 'react';
import { getTrades } from '../services/api.js';
import { TrendingUp, TrendingDown, Minus, Receipt } from 'lucide-react';

import Layout from '../components/layout/Layout';
import EmptyState from '../components/shared/EmptyState';
import { ScrollArea } from '@/components/ui/scroll-area';

function Trades() {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTrades = async () => {
    try {
      setError(null);
      const data = await getTrades();
      // Take last 50
      setTrades(data.slice(0, 50));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
    const interval = setInterval(fetchTrades, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Loading state
  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-[var(--text-muted)]">Loading trades...</div>
        </div>
      </Layout>
    );
  }

  // Error state
  if (error) {
    return (
      <Layout>
        <EmptyState 
          icon={Receipt}
          title="Error loading trades"
          subtitle={error}
        />
        <button onClick={fetchTrades} className="btn-primary mt-4">
          Retry
        </button>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="app-card text-center">
          <p className="text-xs text-[var(--text-muted)] uppercase">Total Trades</p>
          <p className="mt-1 font-mono text-2xl font-bold text-[var(--text-primary)]">
            {trades.length}
          </p>
        </div>
        <div className="app-card text-center">
          <p className="text-xs text-[var(--text-muted)] uppercase">Winning</p>
          <p className="mt-1 font-mono text-2xl font-bold text-[var(--accent)]">
            {trades.filter(t => t.resultado > 0).length}
          </p>
        </div>
        <div className="app-card text-center">
          <p className="text-xs text-[var(--text-muted)] uppercase">Losing</p>
          <p className="mt-1 font-mono text-2xl font-bold text-[var(--destructive)]">
            {trades.filter(t => t.resultado < 0).length}
          </p>
        </div>
      </div>

      {/* Trades List */}
      <ScrollArea className="h-[calc(100vh-280px)]">
        <div className="space-y-2">
          {trades.map((trade) => {
            const isWin = trade.resultado > 0;
            const isLoss = trade.resultado < 0;
            const isOpen = trade.resultado === null || trade.resultado === undefined;
            
            const resultado = isOpen
              ? 'Open'
              : `${trade.resultado >= 0 ? '+' : ''}${trade.resultado.toFixed(2)}`;

            const ResultIcon = isWin ? TrendingUp : isLoss ? TrendingDown : Minus;
            const resultColor = isWin ? 'text-[var(--accent)]' : isLoss ? 'text-[var(--destructive)]' : 'text-[var(--text-muted)]';
            const resultBg = isWin ? 'bg-[var(--accent-dim)]' : isLoss ? 'bg-red-500/10' : 'bg-[var(--bg-elevated)]';

            return (
              <div 
                key={trade.id} 
                className="app-card app-card-hover flex items-center justify-between py-3"
              >
                <div className="flex items-center gap-4">
                  <div className={`h-10 w-10 rounded-lg ${resultBg} flex items-center justify-center`}>
                    <ResultIcon className={`h-5 w-5 ${resultColor}`} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-medium text-[var(--text-primary)]">
                        Agent #{trade.agente_id}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--text-secondary)] uppercase">
                        {trade.tipo}
                      </span>
                    </div>
                    <p className="text-sm text-[var(--text-muted)]">
                      Entry: ${trade.precio_entrada?.toFixed(2)}
                      {trade.precio_salida && ` → $${trade.precio_salida.toFixed(2)}`}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className={`font-mono font-semibold ${resultColor}`}>
                    {resultado}
                  </p>
                  <p className="text-xs text-[var(--text-muted)]">
                    {formatTimestamp(trade.timestamp)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {trades.length === 0 && (
          <EmptyState
            icon={Receipt}
            title="No trades recorded"
            subtitle="Trades will appear here when agents execute them"
          />
        )}
      </ScrollArea>
    </Layout>
  );
}

export default Trades;
