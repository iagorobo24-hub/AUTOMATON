import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';

/**
 * Format USD price
 */
function formatPrice(price) {
  if (!price && price !== 0) return '--';
  if (price >= 1) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  }
  // For small prices, show more decimals
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 6,
  }).format(price);
}

/**
 * Format large numbers (market cap, volume)
 */
function formatLargeNum(num) {
  if (!num && num !== 0) return '--';
  if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
  if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
  if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
  if (num >= 1e3) return `$${(num / 1e3).toFixed(1)}K`;
  return `$${num.toFixed(2)}`;
}

/**
 * Format percentage change
 */
function formatChange(change) {
  if (!change && change !== 0) return '--';
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}%`;
}

/**
 * Format last updated time
 */
function formatTime(date) {
  if (!date) return '';
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * PriceCard - displays cryptocurrency price and stats
 * @param {{
 *   coin: { id, symbol, name, image, current_price, market_cap, price_change_24h, volume_24h },
 *   loading?: boolean,
 *   error?: string,
 *   lastUpdated?: Date,
 *   onRefresh?: () => void
 * }} props
 */
export default function PriceCard({ coin, loading, error, lastUpdated, onRefresh }) {
  const isPositive = (coin?.price_change_24h || 0) >= 0;
  const isLoading = loading === true;
  const hasError = !!error;

  return (
    <div className="app-card">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {coin?.image && (
            <img src={coin.image} alt={coin.symbol} className="w-6 h-6 rounded-full" />
          )}
          <div>
            <p className="text-sm font-semibold text-[var(--text-primary)]">{coin?.name || 'Loading...'}</p>
            <p className="text-xs text-[var(--text-muted)] uppercase">{coin?.symbol || '--'}</p>
          </div>
        </div>
        
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-1.5 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 text-[var(--text-secondary)] ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        )}
      </div>

      {/* Error State */}
      {hasError && (
        <div className="py-4 text-center">
          <p className="text-sm text-red-500">{error}</p>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="mt-2 text-sm text-[var(--accent)] hover:underline"
            >
              Retry
            </button>
          )}
        </div>
      )}

      {/* Loading State */}
      {isLoading && !coin && (
        <div className="py-4 space-y-2">
          <div className="h-8 bg-[var(--bg-elevated)] rounded animate-pulse w-3/4" />
          <div className="h-4 bg-[var(--bg-elevated)] rounded animate-pulse w-1/2" />
        </div>
      )}

      {/* Data */}
      {coin && !isLoading && !hasError && (
        <>
          {/* Price */}
          <div className="mb-3">
            <p className="text-2xl font-bold font-mono text-[var(--accent)]">
              {formatPrice(coin.current_price)}
            </p>
            <div className={`flex items-center gap-1 text-sm ${isPositive ? 'text-blue-500' : 'text-red-500'}`}>
              {isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span>{formatChange(coin.price_change_24h)} (24h)</span>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <p className="text-xs text-[var(--text-muted)]">Market Cap</p>
              <p className="font-mono text-[var(--text-primary)]">{formatLargeNum(coin.market_cap)}</p>
            </div>
            <div>
              <p className="text-xs text-[var(--text-muted)]">Volume 24h</p>
              <p className="font-mono text-[var(--text-primary)]">{formatLargeNum(coin.volume_24h)}</p>
            </div>
          </div>
        </>
      )}

      {/* Footer */}
      {lastUpdated && (
        <div className="mt-3 pt-2 border-t border-[var(--border-subtle)]">
          <p className="text-xs text-[var(--text-muted)]">
            Updated {formatTime(lastUpdated)}
          </p>
        </div>
      )}
    </div>
  );
}