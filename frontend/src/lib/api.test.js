import { describe, expect, it } from 'vitest';
import { buildPaperMarketOrderParams, normalizeApiBase } from './api';
import { normalizeMarketData } from '../features/crypto/hooks/useMarketData';

describe('active API integration helpers', () => {
  it('normalizes backend URLs to the /api prefix exactly once', () => {
    expect(normalizeApiBase()).toBe('http://127.0.0.1:8000/api');
    expect(normalizeApiBase('http://localhost:8000/')).toBe('http://localhost:8000/api');
    expect(normalizeApiBase('http://localhost:8000/api')).toBe('http://localhost:8000/api');
  });

  it('builds Paper market-order params with the required idempotency key', () => {
    expect(buildPaperMarketOrderParams({
      requestId: 'operator-001',
      accountId: 7,
      symbol: 'BTC-USDT',
      side: 'BUY',
      quantity: '0.01',
    })).toEqual({
      request_id: 'operator-001',
      account_id: 7,
      symbol: 'BTC-USDT',
      side: 'BUY',
      quantity: '0.01',
    });
  });

  it('normalizes CoinGecko responses without inventing missing RSI values', () => {
    const result = normalizeMarketData(
      [{ id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin' }],
      [{
        id: 'bitcoin',
        symbol: 'BTC',
        name: 'Bitcoin',
        current_price: 65000,
        price_change_24h: 2.5,
      }],
    );

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      id: 'bitcoin',
      symbol: 'BTC',
      name: 'Bitcoin',
      price: 65000,
      change24h: 2.5,
      rsi: null,
    });
  });
});
