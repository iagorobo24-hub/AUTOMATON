import { useState } from 'react';
import { Search, Brain } from 'lucide-react';

import Layout from '../components/layout/Layout';
import MemoryList from '../components/memory/MemoryList';
import MemoryDetail from '../components/memory/MemoryDetail';
import EmptyState from '../components/shared/EmptyState';
import { mockMemoryEntries } from '../lib/mockData.js';

export default function Memory() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEntry, setSelectedEntry] = useState(null);

  // In production, this would fetch from API
  const entries = mockMemoryEntries;

  const filteredEntries = entries.filter(entry =>
    entry.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
    entry.value.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCopy = (value) => {
    navigator.clipboard.writeText(value);
    // Could show a toast here
  };

  const handleDelete = (entry) => {
    if (!confirm(`Delete memory entry "${entry.key}"?`)) return;
    // In production, call API to delete
    console.log('Delete entry:', entry.id);
    if (selectedEntry?.id === entry.id) {
      setSelectedEntry(null);
    }
  };

  return (
    <Layout>
      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Search by key..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="app-input pl-10"
          />
        </div>
      </div>

      {/* Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-[40%_1fr] gap-6 h-[calc(100vh-200px)]">
        <MemoryList
          entries={filteredEntries}
          selectedId={selectedEntry?.id || null}
          onSelect={setSelectedEntry}
        />
        <MemoryDetail
          entry={selectedEntry}
          onCopy={handleCopy}
          onDelete={handleDelete}
        />
      </div>

      {/* Empty State - shown when no entries at all */}
      {filteredEntries.length === 0 && (
        <EmptyState
          icon={Brain}
          title="No memory entries found"
          subtitle="Try adjusting your search query"
        />
      )}
    </Layout>
  );
}
