import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

const { health, activeProfile, evolutionPolicy, runtimeStatus, runtimeSessions, researchPolicy, liveStatus, livePolicy } = vi.hoisted(() => ({
  health: vi.fn(), activeProfile: vi.fn(), evolutionPolicy: vi.fn(), runtimeStatus: vi.fn(), runtimeSessions: vi.fn(), researchPolicy: vi.fn(), liveStatus: vi.fn(), livePolicy: vi.fn(),
}));

vi.mock('@/lib/api', () => ({
  healthAPI: { health }, riskAPI: { activeProfile }, evolutionAPI: { activePolicy: evolutionPolicy },
  runtimeAPI: { status: runtimeStatus, sessions: runtimeSessions }, researchAPI: { activePolicy: researchPolicy },
  liveAPI: { status: liveStatus, policy: livePolicy },
}));

import SettingsPage from './SettingsPage.jsx';

function resolveHealthy() {
  health.mockResolvedValue({ data: {
    status: 'ok', runtime_mode: 'transition', synthetic_engine: 'disabled', market_data: 'real_contract_available',
    accounting: 'authoritative_phase_2', risk: 'authoritative_phase_4', paper_trading: 'autonomous_phase_7',
    backtesting: 'evidence_phase_5', agent_evolution: 'evidence_phase_6', paper_runtime: 'runtime_phase_7',
    strategy_research: 'evidence_phase_8', legacy_pruning: 'pruned_phase_9', live_readiness: 'readiness_phase_10',
    live_adapter: 'disabled_adapter', live_execution: 'disabled', real_capital_execution: 'disabled',
    automated_trading: 'paper_enabled_phase_7',
  }});
  activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });
  evolutionPolicy.mockResolvedValue({ data: { version: 'evolution-v1', active: true, child_allocation_fraction: '0.25' } });
  runtimeStatus.mockResolvedValue({ data: { policy_version: 'runtime-v1' } });
  runtimeSessions.mockResolvedValue({ data: [{ id: 1, status: 'RUNNING' }] });
  researchPolicy.mockResolvedValue({ data: { version: 'research-v1', active: true } });
  liveStatus.mockResolvedValue({ data: {
    mode: 'readiness_phase_10', architecture_ready: false, live_execution: 'disabled',
    real_capital_execution: 'disabled', adapter: 'disabled_adapter', emergency_stop: false,
    latest_reconciliation: 'CLEAN',
  }});
  livePolicy.mockResolvedValue({ data: { version: 'live-v1', active: true, max_deployable_capital: '100' } });
}

describe('SettingsPage Phase 10 Live Readiness contract', () => {
  beforeEach(() => { [health, activeProfile, evolutionPolicy, runtimeStatus, runtimeSessions, researchPolicy, liveStatus, livePolicy].forEach((fn) => fn.mockReset()); });

  it('shows Live Readiness while explicitly keeping Live and real capital execution disabled', async () => {
    resolveHealthy(); render(<SettingsPage />);
    expect(await screen.findByText('live-v1')).toBeTruthy();
    expect(screen.getByText('readiness_phase_10')).toBeTruthy();
    expect(screen.getAllByText(/REAL CAPITAL/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/disabled/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/no existe transmisión de órdenes reales/i)).toBeTruthy();
    expect(screen.getByText(/live execution/i)).toBeTruthy();
  });

  it('does not expose a Live activation or trade button', async () => {
    resolveHealthy(); render(<SettingsPage />);
    await waitFor(() => expect(liveStatus).toHaveBeenCalledTimes(1));
    expect(screen.queryByRole('button', { name: /activar live/i })).toBeNull();
    expect(screen.queryByRole('button', { name: /enviar orden/i })).toBeNull();
    expect(screen.queryByRole('button', { name: /trade live/i })).toBeNull();
  });

  it('does not claim runtime state when dependencies cannot be read', async () => {
    [health, activeProfile, evolutionPolicy, runtimeStatus, runtimeSessions, researchPolicy, liveStatus, livePolicy].forEach((fn) => fn.mockRejectedValue({ message: 'offline' }));
    render(<SettingsPage />);
    expect(await screen.findByText('Desconocido')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('offline');
  });
});
