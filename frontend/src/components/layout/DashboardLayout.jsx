import { useState, useEffect, useCallback } from "react";
import { Outlet, NavLink, useLocation, useNavigate } from "react-router-dom";
import { 
  LayoutDashboard, Bot, TrendingUp, Wallet, MessageSquare,
  Menu, X, Zap, Activity, Bell, Settings, Search, ChevronRight,
  AlertTriangle, Copy, DollarSign, Target
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
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL || ''}/api`;

const navItems = [
  { path: "/dashboard", label: "Panel", icon: LayoutDashboard },
  { path: "/agents", label: "Agentes", icon: Bot },
  { path: "/crypto", label: "Crypto", icon: TrendingUp },
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

const notificationColors = {
  primary: "text-claude-coral bg-claude-coral/10",
  green: "text-apple-green bg-green-50",
  red: "text-apple-red bg-red-50",
  purple: "text-apple-purple bg-purple-50",
  yellow: "text-apple-orange bg-amber-50"
};

const NotificationItem = ({ notification, onRead, onDismiss, onNavigate }) => {
  const Icon = notificationIcons[notification.type] || notificationIcons.default;
  const colorClass = notificationColors[notification.color] || notificationColors.primary;
  
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
        "flex items-start gap-3 p-3 rounded-xl cursor-pointer transition-all group",
        !notification.read ? "bg-claude-warm/50" : "hover:bg-black/[0.02]"
      )}
      onClick={() => { if (!notification.read) onRead(notification.id); if (notification.link) onNavigate(notification.link); }}
    >
      <div className={cn("p-2 rounded-xl shrink-0", colorClass)}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className={cn("text-sm", !notification.read ? "font-semibold text-foreground" : "text-muted-foreground")}>
            {notification.title}
          </p>
          {!notification.read && <div className="w-2 h-2 rounded-full bg-claude-coral shrink-0 mt-2" />}
        </div>
        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{notification.message}</p>
        <p className="text-[10px] text-muted-foreground/50 mt-1">{timeAgo(notification.created_at)}</p>
      </div>
      <button onClick={(e) => { e.stopPropagation(); onDismiss(notification.id); }}
        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-50 rounded-lg transition-all">
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
        <Button variant="ghost" size="icon" className="relative rounded-full h-10 w-10">
          <Bell className="w-[18px] h-[18px]" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-apple-red text-white text-[9px] font-bold rounded-full flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80 rounded-2xl p-0 shadow-lg border-black/5" onCloseAutoFocus={(e) => e.preventDefault()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-black/5">
          <DropdownMenuLabel className="font-semibold text-sm p-0">Notificaciones</DropdownMenuLabel>
          <div className="flex gap-1">
            {unreadCount > 0 && <button onClick={(e) => { e.preventDefault(); onReadAll(); }} className="text-xs text-claude-coral hover:underline px-2 py-1 rounded-lg">Marcar leídas</button>}
            {notifications.length > 0 && <button onClick={(e) => { e.preventDefault(); onDismissAll(); setIsOpen(false); }} className="text-xs text-muted-foreground hover:text-apple-red px-2 py-1 rounded-lg">Limpiar</button>}
          </div>
        </div>
        <ScrollArea className="max-h-[400px]">
          <div className="p-2 space-y-1">
            {notifications.length > 0 ? notifications.map((n) => (
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
      <DialogContent className="p-0 max-w-lg rounded-2xl shadow-2xl border-0">
        <div className="flex items-center gap-3 px-4 py-3 border-b border-black/5">
          <Search className="w-[18px] h-[18px] text-muted-foreground" />
          <Input placeholder="Buscar..." value={search} onChange={(e) => setSearch(e.target.value)}
            className="border-0 bg-transparent focus-visible:ring-0 px-0 text-base" autoFocus />
        </div>
        <ScrollArea className="max-h-[300px]">
          <div className="p-2">
            {filtered.map((cmd, i) => (
              <button key={i} onClick={() => { cmd.action(); onClose(); setSearch(""); }}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-black/[0.04] transition-colors text-left">
                <cmd.icon className="w-[18px] h-[18px] text-muted-foreground" />
                <span className="text-sm">{cmd.label}</span>
              </button>
            ))}
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
      try { const r = await axios.get(`${API}/dashboard/stats`); setCounts({ dying: r.data.agents?.dying || 0, replicating: r.data.agents?.replicating || 0 }); } catch {}
    };
    fetch();
    const i = setInterval(fetch, 30000);
    return () => clearInterval(i);
  }, []);

  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-black/20 z-30 lg:hidden backdrop-blur-sm" onClick={onClose} />}
      <aside className={cn(
        "fixed left-0 top-0 h-full w-64 z-40 bg-white/80 backdrop-blur-xl border-r border-black/5",
        "transform transition-transform duration-300 ease-out lg:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="h-16 flex items-center px-6 border-b border-black/5">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-claude-coral/10 flex items-center justify-center">
              <Zap className="w-4 h-4 text-claude-coral" />
            </div>
            <span className="font-semibold text-lg tracking-tight">Automaton</span>
          </div>
          <button onClick={onClose} className="lg:hidden ml-auto text-muted-foreground"><X className="w-5 h-5" /></button>
        </div>

        <nav className="p-3 space-y-0.5 mt-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink key={item.path} to={item.path} onClick={onClose}
                className={cn("flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium transition-all",
                  isActive ? "bg-claude-coral/10 text-claude-coral" : "text-muted-foreground hover:bg-black/[0.04] hover:text-foreground")}>
                <div className="flex items-center gap-3">
                  <item.icon className="w-[18px] h-[18px]" />
                  {item.label}
                </div>
                {item.path === '/agents' && counts.dying > 0 && (
                  <span className="px-1.5 py-0.5 text-[10px] font-medium bg-apple-red/10 text-apple-red rounded-full">{counts.dying}</span>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-black/5">
          {secondaryNavItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink key={item.path} to={item.path} onClick={onClose}
                className={cn("flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all",
                  isActive ? "bg-claude-coral/10 text-claude-coral" : "text-muted-foreground hover:bg-black/[0.04] hover:text-foreground")}>
                <item.icon className="w-[18px] h-[18px]" />
                {item.label}
              </NavLink>
            );
          })}
        </div>
      </aside>
    </>
  );
};

const Topbar = ({ onMenuClick }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [commandOpen, setCommandOpen] = useState(false);

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
    try { const r = await axios.get(`${API}/notifications?limit=20`); setNotifications(r.data.notifications || []); setUnreadCount(r.data.unread_count || 0); } catch {}
  }, []);

  useEffect(() => { fetchNotifications(); const i = setInterval(fetchNotifications, 15000); return () => clearInterval(i); }, [fetchNotifications]);
  useEffect(() => { const h = (e) => { if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setCommandOpen(true); } }; window.addEventListener('keydown', h); return () => window.removeEventListener('keydown', h); }, []);

  const handleMarkRead = async (id) => { try { await axios.post(`${API}/notifications/${id}/read`); fetchNotifications(); } catch {} };
  const handleMarkAllRead = async () => { try { await axios.post(`${API}/notifications/read-all`); fetchNotifications(); } catch {} };
  const handleDismiss = async (id) => { try { await axios.delete(`${API}/notifications/${id}`); fetchNotifications(); } catch {} };
  const handleDismissAll = async () => { try { await axios.delete(`${API}/notifications`); fetchNotifications(); } catch {} };

  return (
    <>
      <header className="sticky top-0 z-30 h-16 bg-white/60 backdrop-blur-xl border-b border-black/5">
        <div className="h-full px-4 lg:px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="lg:hidden rounded-full" onClick={onMenuClick}><Menu className="w-5 h-5" /></Button>
            <div>
              <nav className="flex items-center gap-1 text-xs text-muted-foreground mb-0.5">
                {(breadcrumbMap[location.pathname] || [{ label: 'Automaton' }]).map((item, i, arr) => (
                  <span key={i} className="flex items-center gap-1">
                    {item.href ? <button onClick={() => navigate(item.href)} className="hover:text-foreground transition-colors">{item.label}</button> : <span className="text-foreground font-medium">{item.label}</span>}
                    {i < arr.length - 1 && <ChevronRight className="w-3 h-3" />}
                  </span>
                ))}
              </nav>
              <h1 className="font-semibold text-lg tracking-tight">{titles[location.pathname] || 'Automaton'}</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="hidden sm:flex items-center gap-2 text-muted-foreground rounded-full" onClick={() => setCommandOpen(true)}>
              <Search className="w-4 h-4" /><span className="text-xs">Buscar</span>
              <kbd className="ml-2 px-1.5 py-0.5 text-[10px] font-mono bg-black/5 rounded-md">⌘K</kbd>
            </Button>
            <NotificationsDropdown notifications={notifications} unreadCount={unreadCount} onRead={handleMarkRead} onReadAll={handleMarkAllRead} onDismiss={handleDismiss} onDismissAll={handleDismissAll} onNavigate={navigate} />
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50">
              <div className="w-1.5 h-1.5 rounded-full bg-apple-green animate-pulse" />
              <span className="text-[11px] font-medium text-apple-green">Conectado</span>
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
    <div className="min-h-screen bg-[#F5F3EF]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="lg:ml-64">
        <Topbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="p-4 lg:p-6 max-w-[1400px] mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
