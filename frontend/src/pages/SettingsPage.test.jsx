import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

const { health, activeProfile, evolutionPolicy, runtimeStatus, runtimeSessions, researchPolicy } = vi.hoisted(() => ({
  health: vi.fn(),
  activeProfile: vi.fn(),
  evolutionPolicy: vi.fn(),
  runtimeStatus: vi.fn(),
  runtimeSessions: vi.fn(),
  researchPolicy: vi.fn(),
}));

vi.mock('@/lib/api', () => ({
  healthAPI: { health },
  riskAPI: { activeProfile },
  evolutionAPI: { activePolicy: evolutionPolicy },
  runtimeAPI: { status: runtimeStatus, sessions: runtimeSessions },
  researchAPI: { activePolicy: researchPolicy },
}));

import SettingsPage from './SettingsPage.jsx';

describe('SettingsPage Phase 8 research contract', () => {
  beforeEach(() => {
    health.mockReset(); activeProfile.mockReset(); evolutionPolicy.mockReset(); runtimeStatus.mockReset(); runtimeSessions.mockReset(); researchPolicy.mockReset();
  });

  it('shows evidence-gated Strategy Research without claiming deployment or Live', async () => {
    health.mockResolvedValue({ data: {
      status: 'ok', runtime_mode: 'transition', synthetic_engine: 'disabled',
      market_data: 'real_contract_available', accounting: 'authoritative_phase_2', risk: 'authoritative_phase_4',
      paper_trading: 'autonomous_phase_7', backtesting: 'evidence_phase_5', agent_evolution: 'evidence_phase_6',
      paper_runtime: 'runtime_phase_7', strategy_research: 'evidence_phase_8', automated_trading: 'paper_enabled_phase_7', live_execution: 'disabled',
    }});
    activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });
    evolutionPolicy.mockResolvedValue({ data: { version: 'evolution-v1', active: true, child_allocation_fraction: '0.25' } });
    runtimeStatus.mockResolvedValue({ data: { policy_version: 'runtime-v1', live_execution_capability: false, auto_replication: false } });
    runtimeSessions.mockResolvedValue({ data: [{ id: 1, status: 'RUNNING' }] });
    researchPolicy.mockResolvedValue({ data: { version: 'research-v1', active: true } });

    render(<SettingsPage />);

    expect(await screen.findByText('risk-v1')).toBeTruthy();
    expect(screen.getByText('research-v1')).toBeTruthy();
    expect(screen.getByText('evidence_phase_8')).toBeTruthy();
    expect(screen.getAllByText(/TRAIN\/VALIDATION\/OOS/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/no cambia automáticamente ninguna sesión/i)).toBeTruthy();
  });

  it('does not expose optimizer, automatic mutation or Live controls', async () => {
    health.mockResolvedValue({ data: { status: 'ok', synthetic_engine: 'disabled', paper_runtime: 'runtime_phase_7', strategy_research: 'evidence_phase_8', live_execution: 'disabled' } });
    activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });
    evolutionPolicy.mockResolvedValue({ data: { version: 'evolution-v1', active: true, child_allocation_fraction: '0.25' } });
    runtimeStatus.mockResolvedValue({ data: { policy_version: 'runtime-v1' } });
    runtimeSessions.mockResolvedValue({ data: [] });
    researchPolicy.mockResolvedValue({ data: { version: 'research-v1', active: true } });

    render(<SettingsPage />);
    await waitFor(() => expect(health).toHaveBeenCalledTimes(1));

    expect(screen.queryByText('Optimizar estrategias')).toBeNull();
    expect(screen.queryByText('Mutar estrategia')).toBeNull();
    expect(screen.queryByText('Live (Binance)')).toBeNull();
  });

  it('does not claim runtime state when dependencies cannot be read', async () => {
    health.mockRejectedValue({ message: 'offline' });
    activeProfile.mockRejectedValue({ message: 'offline' });
    evolutionPolicy.mockRejectedValue({ message: 'offline' });
    runtimeStatus.mockRejectedValue({ message: 'offline' });
    runtimeSessions.mockRejectedValue({ message: 'offline' });
    researchPolicy.mockRejectedValue({ message: 'offline' });

    render(<SettingsPage />);
    expect(await screen.findByText('Desconocido')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('offline');
  });
});
