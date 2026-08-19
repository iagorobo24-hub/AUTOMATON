import { describe, expect, it } from 'vitest';
import { normalizePaperExecutions } from './LiveTradeFeed.jsx';

describe('paper execution monitor normalization', () => {
  it('preserves Paper provenance, execution prices, fees and status', () => {
    const result = normalizePaperExecutions([
      {
        id: 9,
        agent_id: 2,
        symbol: 'BTC/USDT',
        side: 'BUY',
        requested_quantity: '0.01',
        provider: 'binance_public',
        market_price: '65000',
        fill_price: '65065',
        fee: '0.65065',
        status: 'FILLED',
        evidence_mode: 'paper',
        policy_version: 'paper-v1',
        quote_observed_at: '2026-08-19T14:00:00+00:00',
      },
    ]);

    expect(result[0]).toEqual({
      id: 9,
      agentId: 2,
      symbol: 'BTC/USDT',
      side: 'BUY',
      quantity: 0.01,
      provider: 'binance_public',
      marketPrice: 65000,
      fillPrice: 65065,
      fee: 0.65065,
      status: 'FILLED',
      evidenceMode: 'paper',
      policyVersion: 'paper-v1',
      observedAt: '2026-08-19T14:00:00+00:00',
    });
  });

  it('does not promote missing provenance into Paper evidence', () => {
    const result = normalizePaperExecutions([{ id: 1, status: 'REJECTED' }]);
    expect(result[0].evidenceMode).toBe('unknown');
    expect(result[0].provider).toBe('unknown');
  });
});
