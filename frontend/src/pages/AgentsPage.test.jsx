import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

const { list, replicate, create, remove, deposit, toastSuccess, toastError } = vi.hoisted(() => ({
  list: vi.fn(), replicate: vi.fn(), create: vi.fn(), remove: vi.fn(), deposit: vi.fn(),
  toastSuccess: vi.fn(), toastError: vi.fn(),
}));

vi.mock('@/lib/api', () => ({
  agentsAPI: { list, replicate, create, delete: remove, deposit },
}));
vi.mock('@/lib/agentContract', () => ({ normalizeAgents: (items) => items }));
vi.mock('sonner', () => ({ toast: { success: toastSuccess, error: toastError } }));
vi.mock('framer-motion', () => ({ motion: { div: ({ children, ...props }) => <div {...props}>{children}</div> } }));

import AgentsPage from './AgentsPage.jsx';

const agent = {
  id: 1, name: 'ADAN', strategy: 'S1', status: 'active',
  finances: { current_balance: 1000, initial_capital: 1000 },
  performance: { evidence_valid: false, roi_percent: null },
  trading_stats: { total_trades: null, winning_trades: null, legacy_records: 0 },
  lineage: { parent_id: null, children_ids: [] },
};

describe('AgentsPage Phase 6 evolution actions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    list.mockResolvedValue({ data: [agent] });
  });

  it('offers manual evidence-gated replication and delegates to backend', async () => {
    replicate.mockResolvedValue({ data: { allocated_capital: '250' } });
    render(<AgentsPage />);
    expect(await screen.findByText('ADAN')).toBeTruthy();

    fireEvent.click(screen.getByLabelText('Opciones del agente'));
    expect(screen.getByText(/exige Backtest reproducible/i)).toBeTruthy();
    fireEvent.click(screen.getByText('Replicar con fitness'));

    await waitFor(() => expect(replicate).toHaveBeenCalledWith(1));
    expect(toastSuccess).toHaveBeenCalledWith(expect.stringMatching(/250\.00/));
  });

  it('shows the backend fitness rejection instead of implying profitability', async () => {
    replicate.mockRejectedValue({ status: 409, message: 'fitness rejected: PAPER_TRADES_INSUFFICIENT' });
    render(<AgentsPage />);
    await screen.findByText('ADAN');
    fireEvent.click(screen.getByLabelText('Opciones del agente'));
    fireEvent.click(screen.getByText('Replicar con fitness'));

    await waitFor(() => expect(toastError).toHaveBeenCalledWith('fitness rejected: PAPER_TRADES_INSUFFICIENT'));
    expect(screen.queryByText(/rentable/i)).toBeNull();
  });
});
