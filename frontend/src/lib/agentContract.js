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
    const roi = initial > 0 ? ((current - initial) / initial) * 100 : 0;

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
      performance: { roi_percent: roi },
      trading_stats: {
        total_trades: Number(agent.trades_count ?? 0),
        winning_trades: Number(agent.successful_trades ?? 0),
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
