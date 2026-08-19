import { describe, expect, it } from 'vitest';
import { normalizeDashboardData } from './BentoGrid.jsx';

describe('dashboard runtime normalization', () => {
  it('does not promote legacy trade records into financial evidence', () => {
    const result = normalizeDashboardData(
      [
        { estado: 'ACTIVO' },
        { estado: 'REPLICADO' },
        { estado: 'MUERTO' },
      ],
      {
        evidence_valid: false,
        evidence_mode: 'legacy_unclassified',
        legacy_records: 7,
        total_trades: null,
        trades_cerrados: null,
        profit_total: null,
        win_rate_percent: null,
      },
      {
        status: 'ok',
        runtime_mode: 'transition',
        synthetic_engine: 'disabled',
        paper_trading: 'not_implemented',
      },
    );

    expect(result).toEqual({
      totalAgents: 3,
      activeAgents: 1,
      deadAgents: 1,
      replicatedAgents: 1,
      totalTrades: null,
      closedTrades: null,
      profitTotal: null,
      winRatePercent: null,
      legacyRecords: 7,
      evidenceValid: false,
      evidenceMode: 'legacy_unclassified',
      runtimeMode: 'transition',
      syntheticDisabled: true,
      paperTrading: 'not_implemented',
    });
  });

  it('accepts financial metrics only when the API marks them as valid evidence', () => {
    const result = normalizeDashboardData(
      [],
      {
        evidence_valid: true,
        evidence_mode: 'paper',
        total_trades: 7,
        trades_cerrados: 5,
        profit_total: 42.5,
        win_rate_percent: 60,
      },
      { runtime_mode: 'paper', synthetic_engine: 'disabled', paper_trading: 'active' },
    );

    expect(result.totalTrades).toBe(7);
    expect(result.profitTotal).toBe(42.5);
    expect(result.winRatePercent).toBe(60);
    expect(result.evidenceValid).toBe(true);
  });
});
