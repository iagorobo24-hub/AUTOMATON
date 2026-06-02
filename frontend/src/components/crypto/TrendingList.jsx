import { TrendingUp } from 'lucide-react';

/**
 * TrendingList - displays trending cryptocurrencies
 * @param {{
 *   coins: Array<{ id, name, symbol, market_cap_rank, thumb }>,
 *   loading?: boolean,
 *   error?: string
 * }} props
 */
export default function TrendingList({ coins, loading, error }) {
  const hasError = !!error;
  const isLoading = loading === true;

  return (
    <div className="app-card">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp className="w-4 h-4 text-[var(--accent)]" />
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Trending</h3>
      </div>

      {/* Error State */}
      {hasError && (
        <div className="py-4 text-center">
          <p className="text-sm text-red-500">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && !coins && (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="w-6 h-6 bg-[var(--bg-elevated)] rounded-full animate-pulse" />
              <div className="flex-1 h-4 bg-[var(--bg-elevated)] rounded animate-pulse" />
            </div>
          ))}
        </div>
      )}

      {/* Data */}
      {coins && coins.length > 0 && !isLoading && !hasError && (
        <div className="space-y-2">
          {coins.map((coin) => (
            <div 
              key={coin.id} 
              className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
            >
              {coin.thumb && (
                <img 
                  src={coin.thumb} 
                  alt={coin.symbol} 
                  className="w-6 h-6 rounded-full" 
                />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                  {coin.name}
                </p>
                <p className="text-xs text-[var(--text-muted)] uppercase">
                  {coin.symbol}
                </p>
              </div>
              {coin.market_cap_rank && (
                <span className="text-xs font-mono text-[var(--text-muted)]">
                  #{coin.market_cap_rank}
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {coins && coins.length === 0 && !isLoading && !hasError && (
        <p className="text-sm text-[var(--text-muted)] text-center py-4">
          No trending coins
        </p>
      )}
    </div>
  );
}