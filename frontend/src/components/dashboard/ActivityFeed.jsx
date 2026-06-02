import { ScrollArea } from '@/components/ui/scroll-area';
import { Activity, AlertCircle, Database, CheckCircle2 } from 'lucide-react';

/**
 * @typedef {import('@/lib/types.js').ActivityItem} ActivityItem
 * @param {{ items: ActivityItem[] }} props
 */
export default function ActivityFeed({ items = [] }) {
  const getIcon = (type) => {
    switch (type) {
      case 'agent_start':
      case 'task_complete':
        return <CheckCircle2 className="h-4 w-4 text-[var(--accent)]" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-[var(--destructive)]" />;
      case 'memory_write':
        return <Database className="h-4 w-4 text-[var(--info)]" />;
      default:
        return <Activity className="h-4 w-4 text-[var(--text-muted)]" />;
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  return (
    <div className="app-card h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Recent Activity</h3>
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent)] opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--accent)]"></span>
        </span>
      </div>
      
      <ScrollArea className="h-[280px]">
        <div className="space-y-0">
          {items.map((item, index) => (
            <div key={item.id}>
              <div className="flex items-start gap-3 py-3">
                <div className="mt-0.5 flex-shrink-0">{getIcon(item.type)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-[var(--text-primary)] truncate">{item.message}</p>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    {item.agent_id && <span className="font-mono">{item.agent_id}</span>}
                  </p>
                </div>
                <span className="text-xs text-[var(--text-muted)] flex-shrink-0">
                  {formatTime(item.timestamp)}
                </span>
              </div>
              {index < items.length - 1 && (
                <div className="border-b border-[var(--border-subtle)]" />
              )}
            </div>
          ))}
          
          {items.length === 0 && (
            <p className="text-sm text-[var(--text-muted)] text-center py-8">No recent activity</p>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
