const STATUS_MAP = {
  ACTIVO: 'active',
  MUERTO: 'dead',
  REPLICADO: 'replicated',
};

export function normalizeAgents(rawAgents = []) {
  const childrenByParent = new Map();
  for (const agent of rawAgents) {
    if (agent.padre_id == null) continue;
    const children = childrenByParent.get(agent.padre_id) || [];
    children.push(agent.id);
    childrenByParent.set(agent.padre_id, children);
  }

  return rawAgents.map((agent) => {
    const initial = Number(agent.presupuesto_inicial ?? 0);
    const current = Number(agent.presupuesto_actual ?? 0);
    const evidenceValid = agent.performance_evidence_valid === true;
    const roi = evidenceValid && agent.profit_percent != null
      ? Number(agent.profit_percent) * 100
      : null;

    return {
      id: agent.id,
      name: agent.nombre,
      strategy: agent.estrategia,
      agent_type: 'crypto_trader',
      status: STATUS_MAP[agent.estado] || 'unknown',
      finances: {
        initial_capital: initial,
        current_balance: current,
      },
      performance: {
        roi_percent: roi,
        evidence_valid: evidenceValid,
        evidence_mode: agent.evidence_mode || 'unknown',
      },
      trading_stats: {
        total_trades: evidenceValid && agent.trades_count != null ? Number(agent.trades_count) : null,
        winning_trades: evidenceValid && agent.successful_trades != null ? Number(agent.successful_trades) : null,
        legacy_records: Number(agent.legacy_trades_count ?? 0),
      },
      lineage: {
        parent_id: agent.padre_id ?? null,
        children_ids: childrenByParent.get(agent.id) || [],
      },
      replication_threshold: agent.umbral_replica,
      created_at: agent.creado_en,
    };
  });
}
