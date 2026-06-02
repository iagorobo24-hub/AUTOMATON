import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Bot, 
  Brain, 
  Receipt, 
  Settings,
  Activity,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/agents', label: 'Agents', icon: Bot },
  { path: '/memory', label: 'Memory', icon: Brain },
  { path: '/trades', label: 'Trades', icon: Receipt },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebarContent = (
    <>
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <span className="text-xl font-bold text-[var(--text-primary)]">AUTOMATON</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--accent-dim)] text-[var(--accent)] font-medium">
            v2.2
          </span>
        </div>
        <button 
          onClick={() => setMobileOpen(false)}
          className="md:hidden btn-icon text-[var(--text-secondary)]"
        >
          <X size={20} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) => 
                `nav-item ${isActive ? 'nav-item-active' : 'nav-item-inactive'}`
              }
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* System Status */}
      <div className="px-4 py-4 border-t border-[var(--border)]">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent)] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[var(--accent)]"></span>
          </span>
          <span className="text-xs text-[var(--text-secondary)]">System Online</span>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-14 bg-[var(--bg-surface)] border-b border-[var(--border)] z-40 flex items-center justify-between px-4">
        <span className="text-lg font-bold text-[var(--text-primary)]">AUTOMATON</span>
        <button onClick={() => setMobileOpen(true)} className="btn-icon text-[var(--text-secondary)]">
          <Menu size={20} />
        </button>
      </div>

      {/* Mobile Overlay */}
      {mobileOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/60 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex w-[220px] flex-col bg-[var(--bg-surface)] border-r border-[var(--border)] min-h-screen sticky top-0">
        {sidebarContent}
      </aside>

      {/* Sidebar - Mobile Drawer */}
      <aside className={`md:hidden fixed inset-y-0 left-0 w-[220px] flex-col bg-[var(--bg-surface)] border-r border-[var(--border)] z-50 transition-transform duration-200 ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        {sidebarContent}
      </aside>
    </>
  );
}
