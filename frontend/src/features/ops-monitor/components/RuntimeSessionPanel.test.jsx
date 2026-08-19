import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

const { sessions } = vi.hoisted(() => ({ sessions: vi.fn() }));

vi.mock('@/lib/api', () => ({ runtimeAPI: { sessions } }));

import { RuntimeSessionPanel } from './RuntimeSessionPanel.jsx';

describe('RuntimeSessionPanel', () => {
  beforeEach(() => sessions.mockReset());

  it('shows persistent Paper runtime health without Live claims', async () => {
    sessions.mockResolvedValue({ data: [{
      id: 1, name: 'continuous', symbol: 'BTC/USDT', interval: '1m', policy_version: 'runtime-v1',
      status: 'RUNNING', heartbeat_at: '2026-08-19T20:00:00Z', last_cycle_at: '2026-08-19T19:59:00Z',
      consecutive_failures: 0, max_consecutive_failures: 5, last_error: null,
    }] });

    render(<RuntimeSessionPanel />);
    expect(await screen.findByText('continuous')).toBeTruthy();
    expect(screen.getByText('RUNNING')).toBeTruthy();
    expect(screen.getByText(/capital virtual/i)).toBeTruthy();
    expect(screen.queryByText(/Live \(Binance\)/i)).toBeNull();
  });
});
