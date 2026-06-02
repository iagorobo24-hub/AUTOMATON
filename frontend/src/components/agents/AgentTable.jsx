import { useState } from 'react';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Eye, Square, Trash2 } from 'lucide-react';
import StatusBadge from '../shared/StatusBadge';
import { Progress } from '@/components/ui/progress';

/**
 * @typedef {import('@/lib/types.js').Agent} Agent
 * @param {{ 
 *   agents: Agent[], 
 *   selectedAgent: Agent | null, 
 *   onSelect: (agent: Agent) => void,
 *   onStop: (agent: Agent) => void,
 *   onDelete: (agent: Agent) => void
 * }} props
 */
export default function AgentTable({ agents, selectedAgent, onSelect, onStop, onDelete }) {
  const [hoveredRow, setHoveredRow] = useState(null);

  const formatLastActive = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMins = Math.floor((now - date) / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-surface)]">
      <Table>
        <TableHeader>
          <TableRow className="border-b border-[var(--border)] hover:bg-transparent">
            <TableHead className="text-[var(--text-secondary)] font-medium">Name</TableHead>
            <TableHead className="text-[var(--text-secondary)] font-medium">Type</TableHead>
            <TableHead className="text-[var(--text-secondary)] font-medium">Status</TableHead>
            <TableHead className="text-[var(--text-secondary)] font-medium">Memory</TableHead>
            <TableHead className="text-[var(--text-secondary)] font-medium">Tasks</TableHead>
            <TableHead className="text-[var(--text-secondary)] font-medium">Last Active</TableHead>
            <TableHead className="text-[var(--text-secondary)] font-medium text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {agents.map((agent) => (
            <TableRow
              key={agent.id}
              onClick={() => onSelect(agent)}
              onMouseEnter={() => setHoveredRow(agent.id)}
              onMouseLeave={() => setHoveredRow(null)}
              className={`
                border-b border-[var(--border-subtle)] cursor-pointer transition-all duration-150
                ${selectedAgent?.id === agent.id 
                  ? 'bg-[var(--accent-dim)] border-l-2 border-l-[var(--accent)]' 
                  : 'hover:bg-[var(--bg-elevated)]'
                }
              `}
            >
              <TableCell className="font-mono font-medium text-[var(--text-primary)]">
                {agent.nombre}
              </TableCell>
              <TableCell className="text-[var(--text-secondary)] capitalize">
                {agent.estrategia}
              </TableCell>
              <TableCell>
                <StatusBadge status={agent.estado} />
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Progress 
                    value={agent.memory_usage || 0} 
                    className="w-[50px] h-1.5 bg-[var(--bg-elevated)]"
                  />
                  <span className="text-xs text-[var(--text-muted)]">{agent.memory_usage || 0}%</span>
                </div>
              </TableCell>
              <TableCell className="text-[var(--text-secondary)]">
                {agent.tasks_completed || 0}
              </TableCell>
              <TableCell className="text-[var(--text-muted)] text-sm">
                {formatLastActive(agent.last_active)}
              </TableCell>
              <TableCell className="text-right">
                <div className={`
                  flex items-center justify-end gap-1 transition-opacity duration-150
                  ${hoveredRow === agent.id || selectedAgent?.id === agent.id ? 'opacity-100' : 'opacity-0'}
                `}>
                  <button 
                    onClick={(e) => { e.stopPropagation(); onSelect(agent); }}
                    className="btn-icon text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    title="View details"
                  >
                    <Eye size={16} />
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); onStop(agent); }}
                    className="btn-icon text-[var(--text-secondary)] hover:text-[var(--warning)]"
                    title="Stop agent"
                    disabled={agent.estado === 'MUERTO'}
                  >
                    <Square size={16} />
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); onDelete(agent); }}
                    className="btn-icon text-[var(--text-secondary)] hover:text-[var(--destructive)]"
                    title="Delete agent"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </TableCell>
            </TableRow>
          ))}
          
          {agents.length === 0 && (
            <TableRow>
              <TableCell colSpan={7} className="text-center py-8 text-[var(--text-muted)]">
                No agents found. Create a new agent to get started.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
