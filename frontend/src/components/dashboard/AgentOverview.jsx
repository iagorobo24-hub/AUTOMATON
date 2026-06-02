import { ScrollArea } from '@/components/ui/scroll-area';
import StatusBadge from '../shared/StatusBadge';
import { ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

/**
 * @typedef {import('@/lib/types.js').Agent} Agent
 * @param {{ agents: Agent[] }} props
 */
export default function AgentOverview({ agents = [] }) {
  const formatLastActive = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <div className="app-card h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Agent Status</h3>
        <span className="text-xs text-[var(--text-muted)]">
          {agents.filter(a => a.estado === 'ACTIVO').length}/{agents.length} active
        </span>
      </div>
      
      <ScrollArea className="h-[280px]">
        <div className="space-y-2">
          {agents.map((agent) => (
            <div 
              key={agent.id} 
              className="flex items-center justify-between p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
            >
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium font-mono text-[var(--text-primary)] truncate">
                  {agent.nombre}
                </p>
                <p className="text-xs text-[var(--text-muted)]">
                  {formatLastActive(agent.last_active)}
                </p>
              </div>
              <StatusBadge status={agent.estado} />
            </div>
          ))}
          
          {agents.length === 0 && (
            <p className="text-sm text-[var(--text-muted)] text-center py-8">No agents found</p>
          )}
        </div>
      </ScrollArea>
      
      <div className="mt-4 pt-4 border-t border-[var(--border-subtle)]">
        <Link 
          to="/agents" 
          className="flex items-center text-sm text-[var(--accent)] hover:opacity-80 transition-opacity"
        >
          View all agents
          <ChevronRight className="h-4 w-4 ml-1" />
        </Link>
      </div>
    </div>
  );
}
