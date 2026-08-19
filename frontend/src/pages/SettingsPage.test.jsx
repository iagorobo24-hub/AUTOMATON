import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

const { health, activeProfile, evolutionPolicy, runtimeStatus, runtimeSessions } = vi.hoisted(() => ({
  health: vi.fn(),
  activeProfile: vi.fn(),
  evolutionPolicy: vi.fn(),
  runtimeStatus: vi.fn(),
  runtimeSessions: vi.fn(),
}));

vi.mock('@/lib/api', () => ({
  healthAPI: { health },
  riskAPI: { activeProfile },
  evolutionAPI: { activePolicy: evolutionPolicy },
  runtimeAPI: { status: runtimeStatus, sessions: runtimeSessions },
}));

import SettingsPage from './SettingsPage.jsx';

describe('SettingsPage Phase 7 runtime contract', () => {
  beforeEach(() => {
    health.mockReset(); activeProfile.mockReset(); evolutionPolicy.mockReset(); runtimeStatus.mockReset(); runtimeSessions.mockReset();
  });

  it('shows autonomous Paper runtime while Live and auto-replication remain disabled', async () => {
    health.mockResolvedValue({ data: {
      status: 'ok', runtime_mode: 'transition', synthetic_engine: 'disabled',
      market_data: 'real_contract_available', accounting: 'authoritative_phase_2', risk: 'authoritative_phase_4',
      paper_trading: 'autonomous_phase_7', backtesting: 'evidence_phase_5', agent_evolution: 'evidence_phase_6',
      paper_runtime: 'runtime_phase_7', automated_trading: 'paper_enabled_phase_7', live_execution: 'disabled',
    }});
    activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });
    evolutionPolicy.mockResolvedValue({ data: { version: 'evolution-v1', active: true, child_allocation_fraction: '0.25' } });
    runtimeStatus.mockResolvedValue({ data: { policy_version: 'runtime-v1', live_execution_capability: false, auto_replication: false } });
    runtimeSessions.mockResolvedValue({ data: [{ id: 1, status: 'RUNNING' }] });

    render(<SettingsPage />);

    expect(await screen.findByText('risk-v1')).toBeTruthy();
    expect(screen.getByText(/Phase 7 · 1 activas/i)).toBeTruthy();
    expect(screen.getByText('runtime_phase_7')).toBeTruthy();
    expect(screen.getByText('paper_enabled_phase_7')).toBeTruthy();
    expect(screen.getByText(/nunca se reanudan silenciosamente/i)).toBeTruthy();
  });

  it('does not expose Live or automatic replication controls', async () => {
    health.mockResolvedValue({ data: {
      status: 'ok', synthetic_engine: 'disabled', backtesting: 'evidence_phase_5', agent_evolution: 'evidence_phase_6',
      paper_runtime: 'runtime_phase_7', automated_trading: 'paper_enabled_phase_7', live_execution: 'disabled',
    }});
    activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });
    evolutionPolicy.mockResolvedValue({ data: { version: 'evolution-v1', active: true, child_allocation_fraction: '0.25' } });
    runtimeStatus.mockResolvedValue({ data: { policy_version: 'runtime-v1' } });
    runtimeSessions.mockResolvedValue({ data: [] });

    render(<SettingsPage />);
    await waitFor(() => expect(health).toHaveBeenCalledTimes(1));

    expect(screen.queryByText('Auto-replicar')).toBeNull();
    expect(screen.queryByText('Optimizar estrategias')).toBeNull();
    expect(screen.queryByText('Live (Binance)')).toBeNull();
  });

  it('does not claim runtime state when dependencies cannot be read', async () => {
    health.mockRejectedValue({ message: 'offline' });
    activeProfile.mockRejectedValue({ message: 'offline' });
    evolutionPolicy.mockRejectedValue({ message: 'offline' });
    runtimeStatus.mockRejectedValue({ message: 'offline' });
    runtimeSessions.mockRejectedValue({ message: 'offline' });

    render(<SettingsPage />);
    expect(await screen.findByText('Desconocido')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('offline');
  });
});
