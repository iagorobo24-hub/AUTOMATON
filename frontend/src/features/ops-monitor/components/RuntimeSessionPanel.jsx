import { useCallback, useEffect, useState } from 'react';
import { runtimeAPI } from '@/lib/api';

function fmt(value) {
  if (!value) return '—';
  try { return new Date(value).toLocaleString(); } catch { return value; }
}

export function RuntimeSessionPanel() {
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      const response = await runtimeAPI.sessions({ limit: 20 });
      setSessions(Array.isArray(response.data) ? response.data : []);
      setError(null);
    } catch (err) {
      setSessions([]);
      setError(err?.message || 'No se pudo consultar Paper Runtime');
    }
  }, []);

  useEffect(() => {
    load();
    const timer = setInterval(load, 10000);
    return () => clearInterval(timer);
  }, [load]);

  const active = sessions.filter((item) => ['RUNNING', 'DEGRADED', 'RECOVERY_REQUIRED', 'PAUSED'].includes(item.status));

  return (
    <section className="glass-card rounded-xl p-5" data-testid="runtime-session-panel">
      <div className="flex items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-foreground">Paper Runtime · Phase 7</h2>
          <p className="text-xs text-muted-foreground mt-1">Sesiones autónomas Paper; capital virtual, Market Data real y Risk obligatorio.</p>
        </div>
        <button onClick={load} className="evo-button-outline px-3 py-2 text-xs">Actualizar</button>
      </div>

      {error && <p className="text-xs text-red-400" role="alert">{error}</p>}
      {!error && active.length === 0 && <p className="text-xs text-muted-foreground">No hay sesiones Paper runtime activas o pausadas.</p>}

      <div className="space-y-3">
        {active.map((session) => (
          <div key={session.id} className="rounded-lg border border-white/5 p-4 bg-white/[0.02]">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-foreground">{session.name}</p>
                <p className="text-xs text-muted-foreground font-mono">{session.symbol} · {session.interval} · {session.policy_version}</p>
              </div>
              <span className="text-xs font-mono text-cyan-400">{session.status}</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-xs">
              <div><p className="text-muted-foreground">Heartbeat</p><p className="text-foreground">{fmt(session.heartbeat_at)}</p></div>
              <div><p className="text-muted-foreground">Último ciclo</p><p className="text-foreground">{fmt(session.last_cycle_at)}</p></div>
              <div><p className="text-muted-foreground">Fallos seguidos</p><p className="text-foreground font-mono">{session.consecutive_failures}/{session.max_consecutive_failures}</p></div>
              <div><p className="text-muted-foreground">Último error</p><p className="text-foreground truncate" title={session.last_error || ''}>{session.last_error || '—'}</p></div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
