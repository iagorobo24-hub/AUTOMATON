import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

const { health } = vi.hoisted(() => ({ health: vi.fn() }));

vi.mock('@/lib/api', () => ({
  healthAPI: { health },
}));

import SettingsPage from './SettingsPage.jsx';

describe('SettingsPage Phase 3 runtime contract', () => {
  beforeEach(() => {
    health.mockReset();
  });

  it('shows synthetic isolation, authoritative accounting and operator-only Paper', async () => {
    health.mockResolvedValue({
      data: {
        status: 'ok',
        runtime_mode: 'transition',
        synthetic_engine: 'disabled',
        market_data: 'real_contract_available',
        accounting: 'authoritative_phase_2',
        paper_trading: 'operator_only_phase_3',
        automated_trading: 'blocked_until_risk',
        live_execution: 'disabled',
      },
    });

    render(<SettingsPage />);

    expect(await screen.findByText('Sintético desactivado')).toBeTruthy();
    expect(screen.getByText('SQLModel + SQLite')).toBeTruthy();
    expect(screen.getByText('operator_only_phase_3')).toBeTruthy();
    expect(screen.getByText('blocked_until_risk')).toBeTruthy();
    expect(screen.getByText('disabled')).toBeTruthy();
    expect(health).toHaveBeenCalledTimes(1);
  });

  it('does not expose live controls, automatic trading or simulated pnl controls', async () => {
    health.mockResolvedValue({
      data: {
        status: 'ok',
        runtime_mode: 'transition',
        synthetic_engine: 'disabled',
        paper_trading: 'operator_only_phase_3',
        automated_trading: 'blocked_until_risk',
        live_execution: 'disabled',
      },
    });

    render(<SettingsPage />);
    await waitFor(() => expect(health).toHaveBeenCalledTimes(1));

    expect(screen.queryByText('Live (Binance)')).toBeNull();
    expect(screen.queryByText('Guardar')).toBeNull();
    expect(screen.queryByText('Simular PnL')).toBeNull();
    expect(screen.queryByText('Iniciar trading automático')).toBeNull();
    expect(screen.queryByText('Borrar Todos los Datos')).toBeNull();
  });

  it('does not claim a runtime state when health cannot be read', async () => {
    health.mockRejectedValue({ message: 'offline' });

    render(<SettingsPage />);

    expect(await screen.findByText('Desconocido')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('offline');
  });
});
