import { Copy, Trash2 } from 'lucide-react';
import CodeBlock from '../shared/CodeBlock';

/**
 * @typedef {import('@/lib/types.js').MemoryEntry} MemoryEntry
 * @param {{ 
 *   entry: MemoryEntry | null,
 *   onCopy: (value: string) => void,
 *   onDelete: (entry: MemoryEntry) => void
 * }} props
 */
export default function MemoryDetail({ entry, onCopy, onDelete }) {
  if (!entry) {
    return (
      <div className="app-card h-full flex items-center justify-center">
        <p className="text-sm text-[var(--text-muted)]">Select an entry to view details</p>
      </div>
    );
  }

  const isJson = (() => {
    try {
      JSON.parse(entry.value);
      return true;
    } catch {
      return false;
    }
  })();

  return (
    <div className="app-card h-full flex flex-col">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-lg font-mono font-semibold text-[var(--accent)] break-all">
            {entry.key}
          </h2>
          <p className="text-xs text-[var(--text-muted)] mt-1">ID: {entry.id}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onCopy(entry.value)}
            className="btn-icon text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            title="Copy to clipboard"
          >
            <Copy size={16} />
          </button>
          <button
            onClick={() => onDelete(entry)}
            className="btn-icon text-[var(--text-secondary)] hover:text-[var(--destructive)]"
            title="Delete entry"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* Value */}
      <div className="flex-1 min-h-0 mb-4">
        <h4 className="text-xs text-[var(--text-muted)] uppercase mb-2">Value</h4>
        <CodeBlock code={entry.value} language={isJson ? 'json' : 'text'} />
      </div>

      {/* Metadata */}
      <div className="border-t border-[var(--border-subtle)] pt-4">
        <h4 className="text-xs text-[var(--text-muted)] uppercase mb-3">Metadata</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-[var(--text-muted)]">Created:</span>
            <p className="text-[var(--text-primary)]">
              {new Date(entry.created_at).toLocaleString()}
            </p>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Updated:</span>
            <p className="text-[var(--text-primary)]">
              {new Date(entry.updated_at).toLocaleString()}
            </p>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Agent ID:</span>
            <p className="font-mono text-[var(--text-primary)]">{entry.agent_id}</p>
          </div>
          <div>
            <span className="text-[var(--text-muted)]">Session ID:</span>
            <p className="font-mono text-[var(--text-primary)]">{entry.session_id}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
