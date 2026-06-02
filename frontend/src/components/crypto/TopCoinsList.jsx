import { useCryptoData } from '@/hooks/use-crypto';
import PriceCard from './PriceCard';
import MiniChart from './MiniChart';

/**
 * TopCoinsList - displays top cryptocurrencies by market cap
 * @param {{ limit?: number, interval?: number }} props
 */
export default function TopCoinsList({ limit = 5, interval = 60000 }) {
  const { data, loading, error, lastUpdated, refetch } = useCryptoData('topcoins', { limit, interval });
  const coins = data?.coins || [];

  return (
    <div className="space-y-3">
      {coins.slice(0, limit).map((coin, index) => (
        <div key={coin.id} className="flex items-center gap-3">
          <span className="text-xs text-[var(--text-muted)] w-4">{index + 1}</span>
          <div className="flex-1">
            <PriceCard 
              coin={coin} 
              loading={loading && index === 0}
              error={index === 0 ? error : undefined}
              lastUpdated={index === 0 ? lastUpdated : undefined}
              onRefresh={index === 0 ? refetch : undefined}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * CryptoTicker - single row ticker for top coins
 * @param {{ limit?: number, interval?: number }} props
 */
export function CryptoTicker({ limit = 5, interval = 30000 }) {
  const { data, loading, error, lastUpdated, refetch } = useCryptoData('topcoins', { limit, interval });
  const coins = data?.coins || [];
  const isLoading = loading && coins.length === 0;

  return (
    <div className="flex items-center gap-4 overflow-x-auto py-2">
      {isLoading && (
        <div className="flex items-center gap-4">
          {[...Array(limit)].map((_, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="w-6 h-6 bg-[var(--bg-elevated)] rounded-full animate-pulse" />
              <div className="w-16 h-4 bg-[var(--bg-elevated)] rounded animate-pulse" />
            </div>
          ))}
        </div>
      )}
      
      {coins.map((coin) => {
        const isPositive = (coin.price_change_24h || 0) >= 0;
        return (
          <div 
            key={coin.id} 
            className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-[var(--bg-hover)] transition-colors shrink-0"
          >
            {coin.image && (
              <img src={coin.image} alt={coin.symbol} className="w-5 h-5 rounded-full" />
            )}
            <span className="text-sm font-medium text-[var(--text-primary)]">
              {coin.symbol}
            </span>
            <span className="text-sm font-mono text-[var(--text-primary)]">
              ${coin.current_price >= 1 ? coin.current_price.toLocaleString() : coin.current_price.toFixed(4)}
            </span>
            <span className={`text-xs ${isPositive ? 'text-blue-500' : 'text-red-500'}`}>
              {isPositive ? '+' : ''}{coin.price_change_24h?.toFixed(2)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

/**
 * CryptoDashboard - full crypto dashboard section
 * @param {{ limit?: number, interval?: number }} props
 */
export function CryptoDashboard({ limit = 10, interval = 60000 }) {
  const topCoinsData = useCryptoData('topcoins', { limit, interval });
  const trendingData = useCryptoData('trending', { limit: 7, interval });
  
  const coins = topCoinsData.data?.coins || [];
  const trending = trendingData.data?.trending || [];

  return (
    <div className="space-y-4">
      {/* Top Coins Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
        {coins.slice(0, limit).map((coin) => {
          const isPositive = (coin.price_change_24h || 0) >= 0;
          return (
            <div key={coin.id} className="app-card">
              <div className="flex items-center gap-2 mb-2">
                {coin.image && (
                  <img src={coin.image} alt={coin.symbol} className="w-6 h-6 rounded-full" />
                )}
                <div className="min-w-0">
                  <p className="text-sm font-medium text-[var(--text-primary)] truncate">{coin.symbol}</p>
                  <p className="text-xs text-[var(--text-muted)] truncate">{coin.name}</p>
                </div>
              </div>
              <p className="text-lg font-bold font-mono text-[var(--accent)]">
                ${coin.current_price >= 1 ? coin.current_price.toLocaleString() : coin.current_price.toFixed(4)}
              </p>
              <p className={`text-xs ${isPositive ? 'text-blue-500' : 'text-red-500)'}`}>
                {isPositive ? '+' : ''}{coin.price_change_24h?.toFixed(2)}% 24h
              </p>
            </div>
          );
        })}
      </div>

      {/* Timestamp */}
      {topCoinsData.lastUpdated && (
        <p className="text-xs text-[var(--text-muted)] text-right">
          Last updated: {topCoinsData.lastUpdated.toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}