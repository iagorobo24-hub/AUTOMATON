import { useQuery } from '@tanstack/react-query';
import { api } from '@/shared/lib/api-client';

/**
 * Hook to fetch market data for the tactical terminal
 */
export function useMarketData() {
  return useQuery({
    queryKey: ['market-data'],
    queryFn: async () => {
      // Fetch trending and top coins in parallel
      const [trending, top] = await Promise.all([
        api.get('/crypto/trending').catch(() => []),
        api.get('/crypto/top').catch(() => []),
      ]);

      // Merge and sanitize data
      // Note: Backend might return different structures, we normalize here
      const coins = [...(trending || []), ...(top || [])];
      
      // Remove duplicates by symbol
      const uniqueCoins = Array.from(new Map(coins.map(c => [c.symbol, c])).values());

      return uniqueCoins.map(coin => ({
        id: coin.id || coin.symbol,
        symbol: coin.symbol?.toUpperCase() || '???',
        name: coin.name || coin.symbol,
        price: coin.price || coin.current_price || 0,
        change24h: coin.change24h || coin.price_change_percentage_24h || 0,
        rsi: coin.rsi || (Math.random() * 40 + 30).toFixed(1), // Mock RSI if missing
        activeAgents: coin.agents_count || 0,
      }));
    },
    refetchInterval: 30000, // Refresh every 30s
  });
}
