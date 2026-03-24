import { useState, useEffect, useCallback } from "react";
import { Outlet, NavLink, useLocation, useNavigate } from "react-router-dom";
import { 
  LayoutDashboard, 
  Bot, 
  TrendingUp, 
  Wallet, 
  MessageSquare,
  Menu,
  X,
  Zap,
  Activity,
  Bell,
  Settings,
  FileText,
  Search,
  ChevronDown,
  Check,
  Trash2,
  ExternalLink,
  AlertTriangle,
  Copy,
  Skull,
  Target,
  DollarSign,
  Command
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const navItems = [
  { path: "/dashboard", label: "DASHBOARD", icon: LayoutDashboard },
  { path: "/agents", label: "AGENTS", icon: Bot },
  { path: "/crypto", label: "CRYPTO", icon: TrendingUp },
  { path: "/wallet", label: "WALLET", icon: Wallet },
  { path: "/activity", label: "ACTIVITY", icon: Activity },
  { path: "/chat", label: "ORCHESTRATOR", icon: MessageSquare },
];

const secondaryNavItems = [
  { path: "/settings", label: "SETTINGS", icon: Settings },
];

// ==================== NOTIFICATION ICON MAPPING ====================
const notificationIcons = {
  agent_created: Bot,
  agent_replicated: Copy,
  agent_dying: AlertTriangle,
  agent_dead: Skull,
  trade_win: TrendingUp,
  trade_loss: TrendingUp,
  alert_low_balance: DollarSign,
  alert_replication_ready: Zap,
  opportunity_detected: Target,
  default: Bell
};

const notificationColors = {
  primary: "text-primary bg-primary/10",
  green: "text-cyber-green bg-cyber-green/10",
  red: "text-destructive bg-destructive/10",
  purple: "text-secondary bg-secondary/10",
  yellow: "text-yellow-400 bg-yellow-400/10"
};

// ==================== NOTIFICATION ITEM ====================
const NotificationItem = ({ notification, onRead, onDismiss, onNavigate }) => {
  const Icon = notificationIcons[notification.type] || notificationIcons.default;
  const colorClass = notificationColors[notification.color] || notificationColors.primary;
  
  const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const handleClick = () => {
    if (!notification.read) {
      onRead(notification.id);
    }
    if (notification.link) {
      onNavigate(notification.link);
    }
  };

  return (
    <div 
      className={cn(
        "flex items-start gap-3 p-3 rounded-sm border border-white/10 cursor-pointer transition-colors group",
        !notification.read && "bg-white/5",
        "hover:bg-white/10"
      )}
      onClick={handleClick}
    >
      <div className={cn("p-2 rounded-sm shrink-0", colorClass)}>
        <Icon className="w-4 h-4" />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className={cn(
            "text-sm font-medium",
            !notification.read && "text-white",
            notification.read && "text-muted-foreground"
          )}>
            {notification.title}
          </p>
          {!notification.read && (
            <div className="w-2 h-2 rounded-full bg-primary shrink-0 mt-1.5" />
          )}
        </div>
        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
          {notification.message}
        </p>
        <p className="text-[10px] text-muted-foreground/60 mt-1">
          {timeAgo(notification.created_at)}
        </p>
      </div>

      <button
        onClick={(e) => {
          e.stopPropagation();
          onDismiss(notification.id);
        }}
        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-opacity"
      >
        <X className="w-3 h-3 text-muted-foreground" />
      </button>
    </div>
  );
};

// ==================== NOTIFICATIONS DROPDOWN ====================
const NotificationsDropdown = ({ notifications, unreadCount, onRead, onReadAll, onDismiss, onDismissAll, onNavigate }) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size="icon" 
          className="relative"
          data-testid="notifications-btn"
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        align="end" 
        className="w-80 glass border-white/10"
        data-testid="notifications-dropdown"
      >
        <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
          <DropdownMenuLabel className="font-heading text-xs uppercase tracking-wider p-0">
            Notifications
          </DropdownMenuLabel>
          <div className="flex gap-1">
            {unreadCount > 0 && (
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 text-[10px] px-2"
                onClick={onReadAll}
              >
                <Check className="w-3 h-3 mr-1" />
                Read All
              </Button>
            )}
            {notifications.length > 0 && (
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 text-[10px] px-2 text-destructive hover:text-destructive"
                onClick={onDismissAll}
              >
                <Trash2 className="w-3 h-3 mr-1" />
                Clear
              </Button>
            )}
          </div>
        </div>
        
        <ScrollArea className="max-h-[400px]">
          <div className="p-2 space-y-2">
            {notifications.length > 0 ? (
              notifications.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onRead={onRead}
                  onDismiss={onDismiss}
                  onNavigate={onNavigate}
                />
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p className="text-sm">No notifications</p>
                <p className="text-xs">You're all caught up!</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

// ==================== COMMAND PALETTE ====================
const CommandPalette = ({ open, onClose }) => {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");

  const commands = [
    { label: "Go to Dashboard", action: () => navigate('/dashboard'), icon: LayoutDashboard },
    { label: "Go to Agents", action: () => navigate('/agents'), icon: Bot },
    { label: "Go to Crypto", action: () => navigate('/crypto'), icon: TrendingUp },
    { label: "Go to Wallet", action: () => navigate('/wallet'), icon: Wallet },
    { label: "Go to Activity", action: () => navigate('/activity'), icon: Activity },
    { label: "Go to Orchestrator", action: () => navigate('/chat'), icon: MessageSquare },
    { label: "Deploy New Agent", action: () => navigate('/agents'), icon: Zap },
  ];

  const filteredCommands = commands.filter(cmd => 
    cmd.label.toLowerCase().includes(search.toLowerCase())
  );

  const executeCommand = (cmd) => {
    cmd.action();
    onClose();
    setSearch("");
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onClose();
      }
    };
    
    if (open) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [open, onClose]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="glass border-white/10 p-0 max-w-lg">
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
          <Search className="w-5 h-5 text-muted-foreground" />
          <Input
            placeholder="Type a command or search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border-0 bg-transparent focus-visible:ring-0 px-0 text-base"
            autoFocus
          />
          <kbd className="px-2 py-1 text-[10px] font-mono bg-white/10 rounded">ESC</kbd>
        </div>
        <ScrollArea className="max-h-[300px]">
          <div className="p-2">
            {filteredCommands.map((cmd, i) => (
              <button
                key={i}
                onClick={() => executeCommand(cmd)}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-sm hover:bg-white/10 transition-colors text-left"
              >
                <cmd.icon className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm">{cmd.label}</span>
              </button>
            ))}
            {filteredCommands.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <p className="text-sm">No commands found</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

// ==================== SIDEBAR ====================
export const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const [agentCounts, setAgentCounts] = useState({ dying: 0, replicating: 0 });

  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const res = await axios.get(`${API}/dashboard/stats`);
        setAgentCounts({
          dying: res.data.agents?.dying || 0,
          replicating: res.data.agents?.replicating || 0
        });
      } catch (error) {
        console.error("Error fetching counts:", error);
      }
    };
    fetchCounts();
    const interval = setInterval(fetchCounts, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-30 lg:hidden"
          onClick={onClose}
        />
      )}
      
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
            <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center glow-cyan animate-pulse-slow">
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

        {/* Main Navigation */}
        <nav className="p-4 space-y-1">
          <p className="text-[10px] font-heading uppercase tracking-wider text-muted-foreground mb-2 px-4">
            Main
          </p>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const badge = item.path === '/agents' && agentCounts.dying > 0 ? agentCounts.dying : null;
            
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={cn(
                  "flex items-center justify-between px-4 py-2.5 rounded-sm",
                  "font-heading font-semibold text-sm tracking-wider",
                  "transition-colors duration-200",
                  isActive 
                    ? "bg-primary/10 text-primary border-l-2 border-primary" 
                    : "text-muted-foreground hover:text-white hover:bg-white/5"
                )}
                data-testid={`nav-${item.path.slice(1)}`}
              >
                <div className="flex items-center gap-3">
                  <item.icon className={cn("w-4 h-4", isActive && "text-primary")} />
                  {item.label}
                </div>
                {badge && (
                  <span className="px-1.5 py-0.5 text-[10px] font-mono bg-destructive/20 text-destructive rounded">
                    {badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Secondary Navigation */}
        <nav className="p-4 pt-0 space-y-1">
          <p className="text-[10px] font-heading uppercase tracking-wider text-muted-foreground mb-2 px-4">
            System
          </p>
          {secondaryNavItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 px-4 py-2.5 rounded-sm",
                  "font-heading font-semibold text-sm tracking-wider",
                  "transition-colors duration-200",
                  isActive 
                    ? "bg-primary/10 text-primary border-l-2 border-primary" 
                    : "text-muted-foreground hover:text-white hover:bg-white/5"
                )}
              >
                <item.icon className={cn("w-4 h-4", isActive && "text-primary")} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {/* Status indicator */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/10">
          <div className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-3">
              <div className="relative">
                <Activity className="w-4 h-4 text-cyber-green" />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-cyber-green rounded-full animate-pulse" />
              </div>
              <span className="text-xs font-mono text-muted-foreground">
                SYSTEM ONLINE
              </span>
            </div>
            <span className="text-[10px] font-mono text-muted-foreground/50">v2.0</span>
          </div>
        </div>
      </aside>
    </>
  );
};

// ==================== TOPBAR ====================
export const Topbar = ({ onMenuClick }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [commandOpen, setCommandOpen] = useState(false);

  // Get page title based on route
  const getPageTitle = () => {
    const titles = {
      '/dashboard': 'Dashboard',
      '/agents': 'Agent Management',
      '/crypto': 'Crypto Market',
      '/wallet': 'Wallet',
      '/activity': 'Activity Feed',
      '/chat': 'Orchestrator AI',
      '/settings': 'Settings'
    };
    return titles[location.pathname] || 'Control Center';
  };

  // Fetch notifications
  const fetchNotifications = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/notifications?limit=20`);
      setNotifications(res.data.notifications || []);
      setUnreadCount(res.data.unread_count || 0);
    } catch (error) {
      console.error("Error fetching notifications:", error);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 15000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  // Keyboard shortcut for command palette
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleMarkRead = async (id) => {
    try {
      await axios.post(`${API}/notifications/${id}/read`);
      fetchNotifications();
    } catch (error) {
      console.error("Error marking notification read:", error);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await axios.post(`${API}/notifications/read-all`);
      fetchNotifications();
    } catch (error) {
      console.error("Error marking all read:", error);
    }
  };

  const handleDismiss = async (id) => {
    try {
      await axios.delete(`${API}/notifications/${id}`);
      fetchNotifications();
    } catch (error) {
      console.error("Error dismissing notification:", error);
    }
  };

  const handleDismissAll = async () => {
    try {
      await axios.delete(`${API}/notifications`);
      fetchNotifications();
    } catch (error) {
      console.error("Error dismissing all:", error);
    }
  };

  const handleNavigate = (link) => {
    navigate(link);
  };

  return (
    <>
      <header className="sticky top-0 z-30 h-16 glass border-b border-white/10">
        <div className="h-full px-4 lg:px-6 flex items-center justify-between">
          {/* Left side */}
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={onMenuClick}
              data-testid="mobile-menu-btn"
            >
              <Menu className="w-5 h-5" />
            </Button>

            <div>
              <h1 className="font-heading font-bold text-lg tracking-wide uppercase">
                {getPageTitle()}
              </h1>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-2">
            {/* Search/Command Palette Trigger */}
            <Button
              variant="ghost"
              size="sm"
              className="hidden sm:flex items-center gap-2 text-muted-foreground hover:text-white"
              onClick={() => setCommandOpen(true)}
            >
              <Search className="w-4 h-4" />
              <span className="text-xs">Search</span>
              <kbd className="ml-2 px-1.5 py-0.5 text-[10px] font-mono bg-white/10 rounded">
                ⌘K
              </kbd>
            </Button>

            {/* Notifications */}
            <NotificationsDropdown
              notifications={notifications}
              unreadCount={unreadCount}
              onRead={handleMarkRead}
              onReadAll={handleMarkAllRead}
              onDismiss={handleDismiss}
              onDismissAll={handleDismissAll}
              onNavigate={handleNavigate}
            />

            {/* Status */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-sm bg-white/5 border border-white/10">
              <div className="w-2 h-2 rounded-full bg-cyber-green animate-pulse" />
              <span className="text-[10px] font-mono text-muted-foreground">
                CONNECTED
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Command Palette */}
      <CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} />
    </>
  );
};

// ==================== MAIN LAYOUT ====================
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
