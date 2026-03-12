import { useState } from "react";
import { Outlet, NavLink, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  Bot, 
  TrendingUp, 
  Wallet, 
  MessageSquare,
  Menu,
  X,
  Zap,
  Activity
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const navItems = [
  { path: "/dashboard", label: "DASHBOARD", icon: LayoutDashboard },
  { path: "/agents", label: "AGENTS", icon: Bot },
  { path: "/crypto", label: "CRYPTO", icon: TrendingUp },
  { path: "/wallet", label: "WALLET", icon: Wallet },
  { path: "/chat", label: "ORCHESTRATOR", icon: MessageSquare },
];

export const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-30 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside className={cn(
        "fixed left-0 top-0 h-full w-64 z-40",
        "glass border-r border-white/10",
        "transform transition-transform duration-300 ease-out",
        "lg:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center glow-cyan">
              <Zap className="w-5 h-5 text-primary" />
            </div>
            <span className="font-display font-bold text-lg tracking-wider text-primary">
              AUTOMATON
            </span>
          </div>
          <button 
            onClick={onClose}
            className="lg:hidden text-muted-foreground hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-sm",
                  "font-heading font-semibold text-sm tracking-wider",
                  "transition-colors duration-200",
                  isActive 
                    ? "bg-primary/10 text-primary border-l-2 border-primary" 
                    : "text-muted-foreground hover:text-white hover:bg-white/5"
                )}
                data-testid={`nav-${item.path.slice(1)}`}
              >
                <item.icon className={cn(
                  "w-5 h-5",
                  isActive && "text-primary"
                )} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {/* Status indicator */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/10">
          <div className="flex items-center gap-3 px-4 py-2">
            <div className="relative">
              <Activity className="w-4 h-4 text-cyber-green" />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-cyber-green rounded-full animate-pulse" />
            </div>
            <span className="text-xs font-mono text-muted-foreground">
              SYSTEM ONLINE
            </span>
          </div>
        </div>
      </aside>
    </>
  );
};

export const Topbar = ({ onMenuClick }) => {
  return (
    <header className="sticky top-0 z-30 h-16 glass border-b border-white/10">
      <div className="h-full px-4 lg:px-6 flex items-center justify-between">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
          data-testid="mobile-menu-btn"
        >
          <Menu className="w-5 h-5" />
        </Button>

        {/* Page title area - can be dynamic */}
        <div className="flex-1 lg:ml-0">
          <h1 className="font-heading font-bold text-lg tracking-wide uppercase text-muted-foreground">
            CONTROL CENTER
          </h1>
        </div>

        {/* Right side actions */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-sm bg-white/5 border border-white/10">
            <div className="w-2 h-2 rounded-full bg-cyber-green animate-pulse" />
            <span className="text-xs font-mono text-muted-foreground">
              CONNECTED
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background grid-bg">
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} 
      />
      
      <div className="lg:ml-64">
        <Topbar onMenuClick={() => setSidebarOpen(true)} />
        
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
