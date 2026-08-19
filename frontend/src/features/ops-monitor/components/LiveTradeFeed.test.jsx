import { describe, expect, it } from 'vitest';
import { normalizeTradeFeed } from './LiveTradeFeed.jsx';

describe('operations monitor normalization', () => {
  it('preserves legacy records while exposing their invalid evidence status', () => {
    const result = normalizeTradeFeed([
      {
        id: 4,
        agente_id: 2,
        precio_entrada: 65000,
        precio_salida: 65500,
        cantidad: 0.01,
        tipo: 'LONG',
        resultado: 5,
        timestamp: '2026-08-18T10:00:00+00:00',
        evidence_mode: 'legacy_unclassified',
        evidence_valid: false,
      },
      {
        id: 5,
        agente_id: 2,
        precio_entrada: 66000,
        precio_salida: null,
        cantidad: 0.01,
        tipo: 'LONG',
        resultado: null,
        timestamp: '2026-08-18T10:01:00+00:00',
        evidence_mode: 'legacy_unclassified',
        evidence_valid: false,
      },
    ]);

    expect(result[0]).toMatchObject({
      id: 4,
      agentId: 2,
      status: 'CLOSED',
      pnl: 5,
      evidenceMode: 'legacy_unclassified',
      evidenceValid: false,
    });
    expect(result[1]).toMatchObject({ id: 5, status: 'OPEN', pnl: null, exit: null, evidenceValid: false });
    expect(result[0]).not.toHaveProperty('pair');
    expect(result[0]).not.toHaveProperty('current');
  });
});
