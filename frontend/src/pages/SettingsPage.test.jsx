import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

const { health, activeProfile } = vi.hoisted(() => ({
  health: vi.fn(),
  activeProfile: vi.fn(),
}));

vi.mock('@/lib/api', () => ({
  healthAPI: { health },
  riskAPI: { activeProfile },
}));

import SettingsPage from './SettingsPage.jsx';

describe('SettingsPage Phase 5 runtime contract', () => {
  beforeEach(() => {
    health.mockReset();
    activeProfile.mockReset();
  });

  it('shows Risk, operator-only Paper and backtesting evidence without profitability claims', async () => {
    health.mockResolvedValue({
      data: {
        status: 'ok',
        runtime_mode: 'transition',
        synthetic_engine: 'disabled',
        market_data: 'real_contract_available',
        accounting: 'authoritative_phase_2',
        risk: 'authoritative_phase_4',
        paper_trading: 'operator_only_phase_4',
        backtesting: 'evidence_phase_5',
        automated_trading: 'blocked_until_strategy_integration',
        live_execution: 'disabled',
      },
    });
    activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });

    render(<SettingsPage />);

    expect(await screen.findByText('risk-v1')).toBeTruthy();
    expect(screen.getByText('authoritative_phase_4')).toBeTruthy();
    expect(screen.getByText('operator_only_phase_4')).toBeTruthy();
    expect(screen.getByText('evidence_phase_5')).toBeTruthy();
    expect(screen.getByText('blocked_until_strategy_integration')).toBeTruthy();
    expect(screen.getByText('disabled')).toBeTruthy();
    expect(screen.getByText(/no implica rentabilidad validada/i)).toBeTruthy();
    expect(health).toHaveBeenCalledTimes(1);
    expect(activeProfile).toHaveBeenCalledTimes(1);
  });

  it('does not expose live automatic trading or optimizer controls', async () => {
    health.mockResolvedValue({ data: {
      status: 'ok', runtime_mode: 'transition', synthetic_engine: 'disabled',
      risk: 'authoritative_phase_4', paper_trading: 'operator_only_phase_4',
      backtesting: 'evidence_phase_5',
      automated_trading: 'blocked_until_strategy_integration', live_execution: 'disabled',
    }});
    activeProfile.mockResolvedValue({ data: { version: 'risk-v1', paused: false } });

    render(<SettingsPage />);
    await waitFor(() => expect(health).toHaveBeenCalledTimes(1));

    expect(screen.queryByText('Live (Binance)')).toBeNull();
    expect(screen.queryByText('Iniciar trading automático')).toBeNull();
    expect(screen.queryByText('Optimizar estrategias')).toBeNull();
    expect(screen.queryByText('Simular PnL')).toBeNull();
  });

  it('does not claim a runtime state when health or Risk cannot be read', async () => {
    health.mockRejectedValue({ message: 'offline' });
    activeProfile.mockRejectedValue({ message: 'offline' });

    render(<SettingsPage />);

    expect(await screen.findByText('Desconocido')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('offline');
  });
});
