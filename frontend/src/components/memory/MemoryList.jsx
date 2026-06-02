import { ScrollArea } from '@/components/ui/scroll-area';

/**
 * @typedef {import('@/lib/types.js').MemoryEntry} MemoryEntry
 * @param {{ 
 *   entries: MemoryEntry[], 
 *   selectedId: string | null,
 *   onSelect: (entry: MemoryEntry) => void 
 * }} props
 */
export default function MemoryList({ entries, selectedId, onSelect }) {
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateValue = (value, maxLength = 60) => {
    if (value.length <= maxLength) return value;
    return value.substring(0, maxLength) + '...';
  };

  return (
    <div className="app-card h-full flex flex-col">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">
          Memory Entries ({entries.length})
        </h3>
      </div>
      
      <ScrollArea className="flex-1 -mx-4 px-4">
        <div className="space-y-1">
          {entries.map((entry) => (
            <button
              key={entry.id}
              onClick={() => onSelect(entry)}
              className={`
                w-full text-left p-3 rounded-lg transition-all duration-150
                ${selectedId === entry.id 
                  ? 'bg-[var(--accent-dim)] border-l-2 border-l-[var(--accent)]' 
                  : 'hover:bg-[var(--bg-hover)] border-l-2 border-l-transparent'
                }
              `}
            >
              <div className="font-mono text-sm text-[var(--accent)] truncate">
                {entry.key}
              </div>
              <div className="mt-1 text-xs text-[var(--text-muted)] truncate">
                {truncateValue(entry.value)}
              </div>
              <div className="mt-2 text-xs text-[var(--text-muted)]">
                {formatTime(entry.updated_at)}
              </div>
            </button>
          ))}
          
          {entries.length === 0 && (
            <p className="text-sm text-[var(--text-muted)] text-center py-8">
              No entries found
            </p>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
