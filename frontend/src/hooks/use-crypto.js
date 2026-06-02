"use client";

import * as React from "react";
import * as api from "../services/api";

/**
 * Hook for fetching crypto data with auto-refresh
 * @param {string} type - 'topcoins' | 'trending' | 'price' | 'history'
 * @param {object} options - { limit, coinId, days, interval }
 */
export function useCryptoData(type, options = {}) {
  const { limit = 10, coinId = "bitcoin", days = 7, interval = 60000 } = options;
  
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const [lastUpdated, setLastUpdated] = React.useState(null);

  const fetchData = React.useCallback(async () => {
    try {
      setError(null);
      let result;
      
      switch (type) {
        case "topcoins":
          result = await api.getTopCoins(limit);
          break;
        case "trending":
          result = await api.getTrending();
          break;
        case "price":
          result = await api.getCoinPrice(coinId);
          break;
        case "history":
          result = await api.getCoinHistory(coinId, days);
          break;
        default:
          throw new Error(`Unknown type: ${type}`);
      }
      
      setData(result);
      setLastUpdated(new Date());
    } catch (err) {
      console.error(`[useCryptoData] Error fetching ${type}:`, err);
      setError(err.message || "Failed to fetch crypto data");
    } finally {
      setLoading(false);
    }
  }, [type, limit, coinId, days]);

  // Initial fetch + interval
  React.useEffect(() => {
    fetchData();
    
    if (interval > 0) {
      const timer = setInterval(fetchData, interval);
      return () => clearInterval(timer);
    }
  }, [fetchData, interval]);

  return { data, loading, error, lastUpdated, refetch: fetchData };
}

/**
 * Hook for single coin price with history
 */
export function useCoinPrice(coinId, interval = 60000) {
  const priceData = useCryptoData("price", { coinId, interval });
  const historyData = useCryptoData("history", { coinId, days: 7, interval: 0 });
  
  return {
    price: priceData.data,
    history: historyData.data,
    loading: priceData.loading || historyData.loading,
    error: priceData.error || historyData.error,
    lastUpdated: priceData.lastUpdated,
    refetch: priceData.refetch,
  };
}