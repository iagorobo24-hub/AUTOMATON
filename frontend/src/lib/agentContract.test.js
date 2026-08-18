import { describe, expect, it } from 'vitest';
import { normalizeAgents } from './agentContract';


describe('SQLModel agent contract adapter', () => {
  it('maps backend fields and statuses into the Dark Pro view model', () => {
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
        creado_en: '2026-08-18T00:01:00+00:00',
      },
    ]);

    expect(agents[0]).toMatchObject({
      name: 'ADAN',
      strategy: 'S1',
      status: 'active',
      finances: { initial_capital: 1000, current_balance: 1100 },
      performance: { roi_percent: 10 },
      lineage: { children_ids: [2] },
    });
    expect(agents[1].status).toBe('replicated');
    expect(agents[1].lineage.parent_id).toBe(1);
  });

  it('does not invent an impossible ROI when initial capital is zero', () => {
    const [agent] = normalizeAgents([
      {
        id: 1,
        nombre: 'BROKEN',
        estrategia: 'S1',
        estado: 'MUERTO',
        presupuesto_inicial: 0,
        presupuesto_actual: 0,
      },
    ]);

    expect(agent.status).toBe('dead');
    expect(agent.performance.roi_percent).toBe(0);
  });
});
