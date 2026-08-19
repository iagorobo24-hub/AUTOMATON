import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

const { health } = vi.hoisted(() => ({ health: vi.fn() }));

vi.mock('@/lib/api', () => ({
  healthAPI: { health },
}));

import SettingsPage from './SettingsPage.jsx';

describe('SettingsPage transition runtime contract', () => {
  beforeEach(() => {
    health.mockReset();
  });

  it('shows synthetic isolation and Paper as not implemented', async () => {
    health.mockResolvedValue({
      data: {
        status: 'ok',
        runtime_mode: 'transition',
        synthetic_engine: 'disabled',
        paper_trading: 'not_implemented',
      },
    });

    render(<SettingsPage />);

    expect(await screen.findByText('Sintético desactivado')).toBeTruthy();
    expect(screen.getByText('SQLModel + SQLite')).toBeTruthy();
    expect(screen.getByText('not_implemented')).toBeTruthy();
    expect(health).toHaveBeenCalledTimes(1);
  });

  it('does not expose unsupported live trading or simulated pnl controls', async () => {
    health.mockResolvedValue({
      data: {
        status: 'ok',
        runtime_mode: 'transition',
        synthetic_engine: 'disabled',
        paper_trading: 'not_implemented',
      },
    });

    render(<SettingsPage />);
    await waitFor(() => expect(health).toHaveBeenCalledTimes(1));

    expect(screen.queryByText('Live (Binance)')).toBeNull();
    expect(screen.queryByText('Guardar')).toBeNull();
    expect(screen.queryByText('Simular PnL')).toBeNull();
    expect(screen.queryByText('Borrar Todos los Datos')).toBeNull();
  });

  it('does not claim a runtime state when health cannot be read', async () => {
    health.mockRejectedValue({ message: 'offline' });

    render(<SettingsPage />);

    expect(await screen.findByText('Desconocido')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('offline');
  });
});
