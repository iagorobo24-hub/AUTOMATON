import { ChevronRight } from 'lucide-react';
import { useLocation } from 'react-router-dom';

const pageTitles = {
  '/': 'Dashboard',
  '/agents': 'Agents',
  '/memory': 'Memory Inspector',
  '/trades': 'Trades',
  '/settings': 'Settings',
};

export default function TopBar({ actions }) {
  const location = useLocation();
  const title = pageTitles[location.pathname] || 'AUTOMATON';

  return (
    <header className="h-14 border-b border-[var(--border)] bg-[var(--bg-surface)] flex items-center justify-between px-6">
      <div className="flex items-center gap-2">
        <h1 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h1>
      </div>
      
      {actions && (
        <div className="flex items-center gap-2">
          {actions}
        </div>
      )}
    </header>
  );
}
