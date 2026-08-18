import { useQuery } from '@tanstack/react-query';
import { cryptoAPI } from '@/lib/api';

export function normalizeMarketData(trending = [], top = []) {
  const coins = [...trending, ...top];
  const uniqueCoins = Array.from(new Map(coins.map((coin) => [coin.symbol, coin])).values());

  return uniqueCoins.map((coin) => ({
    id: coin.id || coin.symbol,
    symbol: coin.symbol?.toUpperCase() || '???',
    name: coin.name || coin.symbol,
    price: coin.price ?? coin.current_price ?? 0,
    change24h: coin.change24h ?? coin.price_change_24h ?? coin.price_change_percentage_24h ?? 0,
    rsi: Number.isFinite(coin.rsi) ? coin.rsi : null,
    activeAgents: coin.agents_count ?? 0,
  }));
}

export function useMarketData() {
  return useQuery({
    queryKey: ['market-data'],
    queryFn: async () => {
      const [trendingResponse, topResponse] = await Promise.all([
        cryptoAPI.trending(),
        cryptoAPI.topCoins(),
      ]);

      return normalizeMarketData(
        trendingResponse.data?.trending ?? [],
        topResponse.data?.coins ?? [],
      );
    },
    refetchInterval: 30000,
  });
}
