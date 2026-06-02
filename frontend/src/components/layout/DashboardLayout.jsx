import { useState, useEffect, useCallback } from "react";
import { Outlet, NavLink, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, Bot, TrendingUp, Wallet, MessageSquare,
  Menu, X, Zap, Activity, Bell, Settings, Search, ChevronRight,
  AlertTriangle, Copy, DollarSign, Target, FlaskConical, Coins
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuTrigger, DropdownMenuSeparator, DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import {
  Dialog, DialogContent,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { notificationsAPI, dashboardAPI } from "@/lib/api";
import { useAppMode } from "@/hooks/useAppMode";

const navItems = [
  { path: "/dashboard", label: "Panel", icon: LayoutDashboard },
  { path: "/agents", label: "Agentes", icon: Bot },
  { path: "/crypto", label: "Crypto", icon: TrendingUp },
  { path: "/simulation", label: "Simulación", icon: Zap },
  { path: "/wallet", label: "Cartera", icon: Wallet },
  { path: "/activity", label: "Actividad", icon: Activity },
  { path: "/chat", label: "Orquestador", icon: MessageSquare },
];

const secondaryNavItems = [
  { path: "/settings", label: "Ajustes", icon: Settings },
];

const notificationIcons = {
  agent_created: Bot, agent_replicated: Copy, agent_dying: AlertTriangle,
  agent_dead: X, trade_win: TrendingUp, trade_loss: TrendingUp,
  alert_low_balance: DollarSign, alert_replication_ready: Zap,
  opportunity_detected: Target, default: Bell
};

const NotificationItem = ({ notification, onRead, onDismiss, onNavigate }) => {
  const Icon = notificationIcons[notification.type] || notificationIcons.default;

  const timeAgo = (dateString) => {
    const seconds = Math.floor((Date.now() - new Date(dateString)) / 1000);
    if (seconds < 60) return 'Ahora';
    if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)}h`;
    return `Hace ${Math.floor(seconds / 86400)}d`;
  };

  return (
    <div
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all group",
        !notification.read ? "bg-white/5" : "hover:bg-white/[0.02]"
      )}
      role="button"
      tabIndex={0}
      aria-label={`${notification.title} — ${notification.message}`}
      onClick={() => { if (!notification.read) onRead(notification.id); if (notification.link) onNavigate(notification.link); }}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onRead(notification.id); } }}
    >
      <div className="p-2 rounded-lg shrink-0 bg-blue-500/10 text-blue-400">
        <Icon className="w-4 h-4" aria-hidden="true" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className={cn("text-sm", !notification.read ? "font-semibold text-foreground" : "text-muted-foreground")}>
            {notification.title}
          </p>
          {!notification.read && <div className="w-2 h-2 rounded-full bg-blue-500 shrink-0 mt-2" aria-label="No leída" />}
        </div>
        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{notification.message}</p>
        <p className="text-[10px] text-muted-foreground/50 mt-1 font-mono">{timeAgo(notification.created_at)}</p>
      </div>
      <button
        onClick={(e) => { e.stopPropagation(); onDismiss(notification.id); }}
        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/10 rounded-lg transition-all"
        aria-label="Descartar notificación"
      >
        <X className="w-3 h-3 text-muted-foreground" />
      </button>
    </div>
  );
};

const NotificationsDropdown = ({ notifications, unreadCount, onRead, onReadAll, onDismiss, onDismissAll, onNavigate }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative rounded-lg h-10 w-10" aria-label={`${unreadCount} notificaciones sin leer`}>
          <Bell className="w-[18px] h-[18px]" aria-hidden="true" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 min-w-4 h-4 px-1 bg-red-600 text-white text-[9px] font-bold rounded-full flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80 rounded-xl p-0 shadow-xl shadow-black/40 border-white/10 bg-black/80 backdrop-blur-xl" onCloseAutoFocus={(e) => e.preventDefault()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <DropdownMenuLabel className="font-semibold text-sm p-0">Notificaciones</DropdownMenuLabel>
          <div className="flex gap-1">
            {unreadCount > 0 && <button onClick={(e) => { e.preventDefault(); onReadAll(); }} className="text-xs text-blue-400 hover:underline px-2 py-1 rounded-lg">Marcar leídas</button>}
            {notifications.length > 0 && <button onClick={(e) => { e.preventDefault(); onDismissAll(); setIsOpen(false); }} className="text-xs text-muted-foreground hover:text-red-400 px-2 py-1 rounded-lg">Limpiar</button>}
          </div>
        </div>
        <ScrollArea className="max-h-[400px]">
          <div className="p-2 space-y-1">
            {notifications.length > 0 ? notifications.slice(0, 10).map((n) => (
              <NotificationItem key={n.id} notification={n} onRead={onRead} onDismiss={onDismiss} onNavigate={(link) => { onNavigate(link); setIsOpen(false); }} />
            )) : (
              <div className="text-center py-10 text-muted-foreground">
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-20" />
                <p className="text-sm">Sin notificaciones</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

const CommandPalette = ({ open, onClose }) => {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const commands = [
    { label: "Ir al Panel", action: () => navigate('/dashboard'), icon: LayoutDashboard },
    { label: "Ir a Agentes", action: () => navigate('/agents'), icon: Bot },
    { label: "Ir a Crypto", action: () => navigate('/crypto'), icon: TrendingUp },
    { label: "Ir a Cartera", action: () => navigate('/wallet'), icon: Wallet },
    { label: "Ir a Actividad", action: () => navigate('/activity'), icon: Activity },
    { label: "Ir al Orquestador", action: () => navigate('/chat'), icon: MessageSquare },
    { label: "Ir a Ajustes", action: () => navigate('/settings'), icon: Settings },
  ];
  const filtered = commands.filter(c => c.label.toLowerCase().includes(search.toLowerCase()));

  useEffect(() => {
    const handler = (e) => { if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); onClose(); } if (e.key === 'Escape') onClose(); };
    if (open) window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, onClose]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="p-0 max-w-lg rounded-xl shadow-2xl shadow-black/50 border-white/10 bg-black/90 backdrop-blur-xl" onCloseAutoFocus={(e) => e.preventDefault()}>
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
          <Search className="w-[18px] h-[18px] text-muted-foreground" aria-hidden="true" />
          <Input placeholder="Buscar comandos..." value={search} onChange={(e) => setSearch(e.target.value)}
            className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-blue-500 px-0 text-base placeholder:text-muted-foreground"
            autoFocus aria-label="Buscar comandos" data-testid="command-search-input" />
        </div>
        <ScrollArea className="max-h-[300px]">
          <div className="p-2" role="listbox" aria-label="Comandos disponibles">
            {filtered.map((cmd, i) => (
              <button key={i} onClick={() => { cmd.action(); onClose(); setSearch(""); }}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/[0.06] transition-colors text-left"
                role="option" aria-selected={i === 0}>
                <cmd.icon className="w-[18px] h-[18px] text-muted-foreground" aria-hidden="true" />
                <span className="text-sm">{cmd.label}</span>
              </button>
            ))}
            {filtered.length === 0 && (
              <div className="text-center py-6 text-muted-foreground text-sm">Sin resultados</div>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const [counts, setCounts] = useState({ dying: 0, replicating: 0 });

  useEffect(() => {
    const fetch = async () => {
      try {
        const r = await dashboardAPI.stats();
        setCounts({ dying: r.data.agents?.dying || 0, replicating: r.data.agents?.replicating || 0 });
      } catch {}
    };
    fetch();
    const i = setInterval(fetch, 30000);
    return () => clearInterval(i);
  }, []);

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 bg-black/60 z-30 lg:hidden backdrop-blur-sm"
            onClick={onClose} aria-hidden="true"
          />
        )}
      </AnimatePresence>
      <motion.aside
        initial={false}
        animate={{ x: isOpen || typeof window !== 'undefined' && window.innerWidth >= 1024 ? 0 : -256 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="fixed left-0 top-0 h-full w-64 z-40 bg-black/80 backdrop-blur-xl border-r border-white/10"
        role="navigation"
        aria-label="Navegación principal"
      >
        <div className="h-16 flex items-center px-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center glow-blue">
              <Zap className="w-4 h-4 text-blue-400" aria-hidden="true" />
            </div>
            <span className="font-heading font-bold text-lg tracking-wider text-foreground uppercase">Automaton</span>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden ml-auto text-muted-foreground hover:text-foreground transition-colors p-1"
            aria-label="Cerrar menú"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="p-3 space-y-0.5 mt-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink key={item.path} to={item.path} onClick={onClose}
                className={cn(
                  "flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20"
                    : "text-muted-foreground hover:bg-white/[0.04] hover:text-foreground"
                )}
                aria-current={isActive ? "page" : undefined}
                data-testid={`nav-${item.path.slice(1)}`}
              >
                <div className="flex items-center gap-3">
                  <item.icon className="w-[18px] h-[18px]" aria-hidden="true" />
                  {item.label}
                </div>
                {item.path === '/agents' && counts.dying > 0 && (
                  <span className="px-1.5 py-0.5 text-[10px] font-medium bg-red-500/15 text-red-400 rounded-full ring-1 ring-red-500/20" aria-label={`${counts.dying} agentes muriendo`}>
                    {counts.dying}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-white/10">
          {secondaryNavItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink key={item.path} to={item.path} onClick={onClose}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20"
                    : "text-muted-foreground hover:bg-white/[0.04] hover:text-foreground"
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <item.icon className="w-[18px] h-[18px]" aria-hidden="true" />
                {item.label}
              </NavLink>
            );
          })}
        </div>
      </motion.aside>
    </>
  );
};

const Topbar = ({ onMenuClick }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { mode, toggleMode, isSimulation } = useAppMode();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [commandOpen, setCommandOpen] = useState(false);
  const [connected, setConnected] = useState(true);

  const titles = { '/dashboard': 'Panel', '/agents': 'Agentes', '/crypto': 'Crypto', '/wallet': 'Cartera', '/activity': 'Actividad', '/chat': 'Orquestador', '/settings': 'Ajustes' };
  const breadcrumbMap = {
    '/dashboard': [{ label: 'Panel' }],
    '/agents': [{ label: 'Panel', href: '/dashboard' }, { label: 'Agentes' }],
    '/crypto': [{ label: 'Panel', href: '/dashboard' }, { label: 'Crypto' }],
    '/wallet': [{ label: 'Panel', href: '/dashboard' }, { label: 'Cartera' }],
    '/activity': [{ label: 'Panel', href: '/dashboard' }, { label: 'Actividad' }],
    '/chat': [{ label: 'Panel', href: '/dashboard' }, { label: 'Orquestador' }],
    '/settings': [{ label: 'Panel', href: '/dashboard' }, { label: 'Ajustes' }]
  };

  const fetchNotifications = useCallback(async () => {
    try {
      const r = await notificationsAPI.list(false, 20);
      setNotifications(r.data.notifications || []);
      setUnreadCount(r.data.unread_count || 0);
      setConnected(true);
    } catch {
      setConnected(false);
    }
  }, []);

  useEffect(() => { fetchNotifications(); const i = setInterval(fetchNotifications, 15000); return () => clearInterval(i); }, [fetchNotifications]);
  useEffect(() => { const h = (e) => { if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setCommandOpen(true); } }; window.addEventListener('keydown', h); return () => window.removeEventListener('keydown', h); }, []);

  const handleMarkRead = async (id) => { try { await notificationsAPI.markRead(id); fetchNotifications(); } catch {} };
  const handleMarkAllRead = async () => { try { await notificationsAPI.markAllRead(); fetchNotifications(); } catch {} };
  const handleDismiss = async (id) => { try { await notificationsAPI.dismiss(id); fetchNotifications(); } catch {} };
  const handleDismissAll = async () => { try { await notificationsAPI.dismissAll(); fetchNotifications(); } catch {} };

  return (
    <>
      <header className="sticky top-0 z-30 h-16 bg-black/60 backdrop-blur-xl border-b border-white/10" role="banner">
        <div className="h-full px-4 lg:px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="lg:hidden rounded-lg" onClick={onMenuClick} aria-label="Abrir menú">
              <Menu className="w-5 h-5" aria-hidden="true" />
            </Button>
            <div>
              <nav className="flex items-center gap-1 text-xs text-muted-foreground mb-0.5" aria-label="Migas de pan">
                {(breadcrumbMap[location.pathname] || [{ label: 'Automaton' }]).map((item, i, arr) => (
                  <span key={i} className="flex items-center gap-1">
                    {item.href ? <button onClick={() => navigate(item.href)} className="hover:text-foreground transition-colors">{item.label}</button> : <span className="text-foreground font-medium">{item.label}</span>}
                    {i < arr.length - 1 && <ChevronRight className="w-3 h-3" aria-hidden="true" />}
                  </span>
                ))}
              </nav>
              <h1 className="font-heading font-semibold text-lg tracking-wide text-foreground uppercase">{titles[location.pathname] || 'Automaton'}</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="hidden sm:flex items-center gap-2 text-muted-foreground rounded-lg hover:bg-white/5" onClick={() => setCommandOpen(true)}>
              <Search className="w-4 h-4" aria-hidden="true" /><span className="text-xs">Buscar</span>
              <kbd className="ml-2 px-1.5 py-0.5 text-[10px] font-mono bg-white/5 rounded border border-white/10">⌘K</kbd>
            </Button>
            <NotificationsDropdown notifications={notifications} unreadCount={unreadCount} onRead={handleMarkRead} onReadAll={handleMarkAllRead} onDismiss={handleDismiss} onDismissAll={handleDismissAll} onNavigate={navigate} />
            {/* Mode Toggle */}
            <button
              onClick={toggleMode}
              className={cn(
                "hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all cursor-pointer",
                isSimulation
                  ? "bg-purple-500/10 border-purple-500/20 hover:bg-purple-500/15"
                  : "bg-blue-500/10 border-blue-500/20 hover:bg-blue-500/15"
              )}
              aria-label={`Cambiar a modo ${isSimulation ? "normal" : "simulación"}`}
            >
              {isSimulation ? (
                <FlaskConical className="w-3.5 h-3.5 text-purple-400" aria-hidden="true" />
              ) : (
                <Coins className="w-3.5 h-3.5 text-blue-400" aria-hidden="true" />
              )}
              <span className={cn(
                "text-[11px] font-medium",
                isSimulation ? "text-purple-400" : "text-blue-400"
              )}>{isSimulation ? "Simulación" : "Real"}</span>
            </button>
            <div className={cn(
              "hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg border",
              connected
                ? "bg-blue-500/10 border-blue-500/20"
                : "bg-red-500/10 border-red-500/20"
            )}>
              <div className={cn(
                "w-1.5 h-1.5 rounded-full",
                connected ? "bg-blue-500 animate-pulse" : "bg-red-500"
              )} aria-hidden="true" />
              <span className={cn(
                "text-[11px] font-medium",
                connected ? "text-blue-400" : "text-red-400"
              )}>{connected ? 'Conectado' : 'Desconectado'}</span>
            </div>
          </div>
        </div>
      </header>
      <CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} />
    </>
  );
};

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="min-h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="lg:ml-64">
        <Topbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="p-4 lg:p-6 max-w-[1400px] mx-auto" role="main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
