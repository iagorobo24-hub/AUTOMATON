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
        risk: 'authoritative_phase_4',
        paper_trading: 'autonomous_phase_7',
        paper_runtime: 'runtime_phase_7',
        automated_trading: 'paper_enabled_phase_7',
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
      riskMode: 'authoritative_phase_4',
      paperTrading: 'autonomous_phase_7',
      paperRuntime: 'runtime_phase_7',
      automatedTrading: 'paper_enabled_phase_7',
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
      {
        runtime_mode: 'transition',
        synthetic_engine: 'disabled',
        risk: 'authoritative_phase_4',
        paper_trading: 'autonomous_phase_7',
        paper_runtime: 'runtime_phase_7',
        automated_trading: 'paper_enabled_phase_7',
      },
    );

    expect(result.totalTrades).toBe(7);
    expect(result.profitTotal).toBe(42.5);
    expect(result.winRatePercent).toBe(60);
    expect(result.evidenceValid).toBe(true);
    expect(result.riskMode).toBe('authoritative_phase_4');
    expect(result.paperTrading).toBe('autonomous_phase_7');
    expect(result.paperRuntime).toBe('runtime_phase_7');
  });
});
