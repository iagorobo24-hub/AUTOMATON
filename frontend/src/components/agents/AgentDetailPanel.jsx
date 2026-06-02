import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetClose } from '@/components/ui/sheet';
import { X } from 'lucide-react';
import StatusBadge from '../shared/StatusBadge';
import CodeBlock from '../shared/CodeBlock';
import { getMockAgentLogs, getMockMemoryDump } from '@/lib/mockData.js';

/**
 * @typedef {import('@/lib/types.js').Agent} Agent
 * @param {{ 
 *   agent: Agent | null, 
 *   open: boolean, 
 *   onClose: () => void 
 * }} props
 */
export default function AgentDetailPanel({ agent, open, onClose }) {
  if (!agent) return null;

  const logs = getMockAgentLogs(agent.id);
  const memoryDump = getMockMemoryDump(agent.id);
  const profit = agent.presupuesto_actual - agent.presupuesto_inicial;
  const profitPercent = ((profit / agent.presupuesto_inicial) * 100).toFixed(2);

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-[380px] bg-[var(--bg-surface)] border-l border-[var(--border)] p-0">
        <SheetHeader className="px-4 py-4 border-b border-[var(--border)]">
          <div className="flex items-center justify-between">
            <SheetTitle className="text-lg font-semibold text-[var(--text-primary)]">
              {agent.nombre}
            </SheetTitle>
            <SheetClose className="btn-icon text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
              <X size={18} />
            </SheetClose>
          </div>
        </SheetHeader>

        <div className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-80px)]">
          {/* Basic Info */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-[var(--text-muted)]">ID</span>
              <span className="text-sm font-mono text-[var(--text-primary)]">{agent.id}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-[var(--text-muted)]">Type</span>
              <span className="text-sm text-[var(--text-primary)] capitalize">{agent.estrategia}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-[var(--text-muted)]">Status</span>
              <StatusBadge status={agent.estado} />
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-[var(--text-muted)]">Created</span>
              <span className="text-sm text-[var(--text-primary)]">
                {new Date(agent.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          {/* Budget */}
          <div className="app-card">
            <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">Budget</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-[var(--text-muted)]">Initial</span>
                <span className="text-xs font-mono text-[var(--text-primary)]">
                  ${agent.presupuesto_inicial.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-[var(--text-muted)]">Current</span>
                <span className="text-xs font-mono text-[var(--text-primary)]">
                  ${agent.presupuesto_actual.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between pt-2 border-t border-[var(--border-subtle)]">
                <span className="text-xs text-[var(--text-muted)]">Profit/Loss</span>
                <span className={`text-xs font-mono font-medium ${profit >= 0 ? 'text-[var(--accent)]' : 'text-[var(--destructive)]'}`}>
                  {profit >= 0 ? '+' : ''}{profit.toFixed(2)} ({profitPercent}%)
                </span>
              </div>
            </div>
          </div>

          {/* Memory Dump */}
          <div>
            <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">Memory State</h4>
            <CodeBlock code={memoryDump} language="json" />
          </div>

          {/* Recent Logs */}
          <div>
            <h4 className="text-sm font-medium text-[var(--text-primary)] mb-3">Recent Logs</h4>
            <div className="code-block">
              {logs.map((log, i) => (
                <div key={i} className="text-xs font-mono text-[var(--text-secondary)]">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
