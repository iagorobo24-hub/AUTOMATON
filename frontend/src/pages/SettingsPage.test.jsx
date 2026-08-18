import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

const { health } = vi.hoisted(() => ({ health: vi.fn() }));

vi.mock('@/lib/api', () => ({
  healthAPI: { health },
}));

import SettingsPage from './SettingsPage.jsx';

describe('SettingsPage active runtime contract', () => {
  beforeEach(() => {
    health.mockReset();
  });

  it('shows the SQLModel AgentEngine status from the active health endpoint', async () => {
    health.mockResolvedValue({ data: { status: 'ok', agent_engine: 'running' } });

    render(<SettingsPage />);

    expect(await screen.findByText('En ejecución')).toBeTruthy();
    expect(screen.getByText('SQLModel + SQLite')).toBeTruthy();
    expect(health).toHaveBeenCalledTimes(1);
  });

  it('does not expose unsupported live trading or legacy settings controls', async () => {
    health.mockResolvedValue({ data: { status: 'ok', agent_engine: 'stopped' } });

    render(<SettingsPage />);
    await waitFor(() => expect(health).toHaveBeenCalledTimes(1));

    expect(screen.queryByText('Live (Binance)')).toBeNull();
    expect(screen.queryByText('Guardar')).toBeNull();
    expect(screen.queryByText('Restablecer Configuración')).toBeNull();
    expect(screen.queryByText('Borrar Todos los Datos')).toBeNull();
    expect(screen.queryByText('Terminar Todos los Agentes')).toBeNull();
  });

  it('does not claim the engine is stopped when health cannot be read', async () => {
    health.mockRejectedValue({ message: 'offline' });

    render(<SettingsPage />);

    expect(await screen.findByText('Desconocido')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('offline');
  });
});
