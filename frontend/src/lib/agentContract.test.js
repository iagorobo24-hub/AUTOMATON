import { describe, expect, it } from 'vitest';
import { normalizeAgents } from './agentContract';


describe('SQLModel agent contract adapter', () => {
  it('quarantines legacy performance fields while preserving operational state', () => {
    const agents = normalizeAgents([
      {
        id: 1,
        nombre: 'ADAN',
        estrategia: 'S1',
        estado: 'ACTIVO',
        presupuesto_inicial: 1000,
        presupuesto_actual: 1100,
        padre_id: null,
        umbral_replica: 0.15,
        profit_percent: null,
        trades_count: null,
        successful_trades: null,
        legacy_trades_count: 3,
        performance_evidence_valid: false,
        evidence_mode: 'legacy_unclassified',
        creado_en: '2026-08-18T00:00:00+00:00',
      },
      {
        id: 2,
        nombre: 'ADAN_child_1',
        estrategia: 'S1',
        estado: 'REPLICADO',
        presupuesto_inicial: 1000,
        presupuesto_actual: 1000,
        padre_id: 1,
        umbral_replica: 0.15,
        performance_evidence_valid: false,
        evidence_mode: 'legacy_unclassified',
        creado_en: '2026-08-18T00:01:00+00:00',
      },
    ]);

    expect(agents[0]).toMatchObject({
      name: 'ADAN',
      strategy: 'S1',
      status: 'active',
      finances: { initial_capital: 1000, current_balance: 1100 },
      performance: {
        roi_percent: null,
        evidence_valid: false,
        evidence_mode: 'legacy_unclassified',
      },
      trading_stats: { total_trades: null, winning_trades: null, legacy_records: 3 },
      lineage: { children_ids: [2] },
    });
    expect(agents[1].status).toBe('replicated');
    expect(agents[1].lineage.parent_id).toBe(1);
  });

  it('uses explicit validated evidence when it becomes available', () => {
    const [agent] = normalizeAgents([
      {
        id: 1,
        nombre: 'PAPER',
        estrategia: 'S1',
        estado: 'ACTIVO',
        presupuesto_inicial: 1000,
        presupuesto_actual: 1100,
        profit_percent: 0.1,
        trades_count: 10,
        successful_trades: 6,
        performance_evidence_valid: true,
        evidence_mode: 'paper',
      },
    ]);

    expect(agent.performance.roi_percent).toBe(10);
    expect(agent.performance.evidence_valid).toBe(true);
    expect(agent.trading_stats.total_trades).toBe(10);
  });
});
