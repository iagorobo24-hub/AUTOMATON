import { describe, expect, it } from 'vitest';
import { normalizeDashboardData } from './BentoGrid.jsx';

describe('dashboard runtime normalization', () => {
  it('derives metrics from active SQLModel contracts only', () => {
    const result = normalizeDashboardData(
      [
        { estado: 'ACTIVO' },
        { estado: 'REPLICADO' },
        { estado: 'MUERTO' },
      ],
      { total_trades: 7, trades_cerrados: 5, profit_total: 42.5, win_rate_percent: 60 },
      { status: 'ok', agent_engine: 'running' },
    );

    expect(result).toEqual({
      totalAgents: 3,
      activeAgents: 1,
      deadAgents: 1,
      replicatedAgents: 1,
      totalTrades: 7,
      closedTrades: 5,
      profitTotal: 42.5,
      winRatePercent: 60,
      engineRunning: true,
    });
  });
});
