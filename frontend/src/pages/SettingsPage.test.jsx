import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

const { health, activeProfile, evolutionPolicy } = vi.hoisted(() => ({
  health: vi.fn(),
  activeProfile: vi.fn(),
  evolutionPolicy: vi.fn(),
}));

vi.mock('@/lib/api', () => ({
  healthAPI: { health },
  riskAPI: { activeProfile },
  evolutionAPI: { activePolicy: evolutionPolicy },
}));

import SettingsPage from './SettingsPage.jsx';

describe('SettingsPage Phase 6 runtime contract', () => {
  beforeEach(() => {
    health.mockReset();
    activeProfile.mockReset();
    evolutionPolicy.mockReset();
  });

  it('shows evidence-gated evolution while automation and Live remain disabled', async () => {
    health.mockResolvedValue({ data: {
      status: 'ok', runtime_mode: 'transition', synthetic_engine: 'disabled',
      market_data: 'real_contract_available', accounting: 'authoritative_phase_2',
      risk: 'authoritative_phase_4', paper_trading: 'operator_only_phase_4',
      backtesting: 'evidence_phase_5', agent_evolution: 'evidence_phase_6',
      automated_trading: 'blocked_until_phase_7_runtime', live_execution: 'disabled',
    }});
    activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });
    evolutionPolicy.mockResolvedValue({ data: { version: 'evolution-v1', active: true, child_allocation_fraction: '0.25' } });

    render(<SettingsPage />);

    expect(await screen.findByText('risk-v1')).toBeTruthy();
    expect(screen.getByText('evolution-v1')).toBeTruthy();
    expect(screen.getByText('evidence_phase_6')).toBeTruthy();
    expect(screen.getByText('blocked_until_phase_7_runtime')).toBeTruthy();
    expect(screen.getByText(/transfiere capital financiado/i)).toBeTruthy();
    expect(screen.getByText(/no implica rentabilidad validada/i)).toBeTruthy();
  });

  it('does not expose automatic replication, automatic trading, optimizer or Live controls', async () => {
    health.mockResolvedValue({ data: {
      status: 'ok', runtime_mode: 'transition', synthetic_engine: 'disabled',
      backtesting: 'evidence_phase_5', agent_evolution: 'evidence_phase_6',
      automated_trading: 'blocked_until_phase_7_runtime', live_execution: 'disabled',
    }});
    activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });
    evolutionPolicy.mockResolvedValue({ data: { version: 'evolution-v1', active: true, child_allocation_fraction: '0.25' } });

    render(<SettingsPage />);
    await waitFor(() => expect(health).toHaveBeenCalledTimes(1));

    expect(screen.queryByText('Iniciar trading automático')).toBeNull();
    expect(screen.queryByText('Auto-replicar')).toBeNull();
    expect(screen.queryByText('Optimizar estrategias')).toBeNull();
    expect(screen.queryByText('Live (Binance)')).toBeNull();
  });

  it('does not claim runtime state when dependencies cannot be read', async () => {
    health.mockRejectedValue({ message: 'offline' });
    activeProfile.mockRejectedValue({ message: 'offline' });
    evolutionPolicy.mockRejectedValue({ message: 'offline' });

    render(<SettingsPage />);
    expect(await screen.findByText('Desconocido')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('offline');
  });
});
