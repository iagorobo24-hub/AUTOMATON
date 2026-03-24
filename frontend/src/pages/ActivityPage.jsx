import { useState, useEffect, useCallback } from "react";
import { 
  Activity, 
  Bot, 
  TrendingUp, 
  TrendingDown, 
  Copy, 
  Skull, 
  AlertTriangle,
  Target,
  DollarSign,
  Zap,
  RefreshCw,
  Filter,
  Calendar,
  Search
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ==================== ICON MAPPING ====================
const eventIcons = {
  agent_created: Bot,
  agent_replicated: Copy,
  agent_dying: AlertTriangle,
  agent_dead: Skull,
  trade_opened: TrendingUp,
  trade_closed: TrendingUp,
  trade_win: TrendingUp,
  trade_loss: TrendingDown,
  payment_received: DollarSign,
  alert_low_balance: AlertTriangle,
  alert_high_drawdown: AlertTriangle,
  alert_replication_ready: Zap,
  opportunity_detected: Target,
  system_info: Activity,
  default: Activity
};

const eventColors = {
  agent_created: "primary",
  agent_replicated: "green",
  agent_dying: "red",
  agent_dead: "red",
  trade_win: "green",
  trade_loss: "red",
  trade_opened: "primary",
  trade_closed: "purple",
  payment_received: "green",
  alert_low_balance: "yellow",
  alert_replication_ready: "purple",
  opportunity_detected: "yellow",
  default: "primary"
};

const colorClasses = {
  primary: "text-primary bg-primary/10 border-primary/30",
  green: "text-cyber-green bg-cyber-green/10 border-cyber-green/30",
  red: "text-destructive bg-destructive/10 border-destructive/30",
  purple: "text-secondary bg-secondary/10 border-secondary/30",
  yellow: "text-yellow-400 bg-yellow-400/10 border-yellow-400/30"
};

// ==================== ACTIVITY EVENT CARD ====================
const ActivityEventCard = ({ event, onClick }) => {
  const Icon = eventIcons[event.type] || eventIcons.default;
  const color = eventColors[event.type] || eventColors.default;
  const colorClass = colorClasses[color];
  
  const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;
    return date.toLocaleDateString();
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div 
      className={cn(
        "flex gap-4 p-4 rounded-sm border border-white/10 hover:border-white/20 transition-colors cursor-pointer group",
        event.link && "hover:bg-white/5"
      )}
      onClick={() => event.link && onClick(event.link)}
    >
      {/* Icon */}
      <div className={cn(
        "w-10 h-10 rounded-sm flex items-center justify-center shrink-0 border",
        colorClass
      )}>
        <Icon className="w-5 h-5" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-semibold text-sm">{event.title}</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              {event.description}
            </p>
          </div>
          {event.amount !== null && event.amount !== undefined && (
            <span className={cn(
              "font-mono text-sm font-semibold shrink-0",
              event.amount >= 0 ? "text-cyber-green" : "text-destructive"
            )}>
              {event.amount >= 0 ? "+" : ""}${Math.abs(event.amount).toFixed(2)}
            </span>
          )}
        </div>
        
        {/* Footer */}
        <div className="flex items-center gap-4 mt-2">
          {event.agent_name && (
            <div className="flex items-center gap-1.5">
              <Bot className="w-3 h-3 text-muted-foreground" />
              <span className="text-[10px] font-mono text-muted-foreground">
                {event.agent_name}
              </span>
            </div>
          )}
          <span className="text-[10px] text-muted-foreground/60">
            {timeAgo(event.created_at)} • {formatTime(event.created_at)}
          </span>
        </div>
      </div>
    </div>
  );
};

// ==================== ACTIVITY STATS ====================
const ActivityStats = ({ events }) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const todayEvents = events.filter(e => new Date(e.created_at) >= today);
  const trades = events.filter(e => e.type.includes('trade'));
  const wins = events.filter(e => e.type === 'trade_win');
  const replications = events.filter(e => e.type === 'agent_replicated');
  
  const stats = [
    { label: "Today's Events", value: todayEvents.length, color: "primary" },
    { label: "Total Trades", value: trades.length, color: "purple" },
    { label: "Winning Trades", value: wins.length, color: "green" },
    { label: "Replications", value: replications.length, color: "green" }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {stats.map((stat) => (
        <Card key={stat.label} className="glass border-white/10">
          <CardContent className="p-4">
            <p className="text-[10px] font-heading uppercase tracking-wider text-muted-foreground">
              {stat.label}
            </p>
            <p className={cn(
              "text-2xl font-mono font-bold mt-1",
              stat.color === "primary" && "text-primary",
              stat.color === "green" && "text-cyber-green",
              stat.color === "purple" && "text-secondary"
            )}>
              {stat.value}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

// ==================== TIMELINE VIEW ====================
const TimelineView = ({ events, onNavigate }) => {
  // Group events by date
  const groupedEvents = events.reduce((groups, event) => {
    const date = new Date(event.created_at).toLocaleDateString();
    if (!groups[date]) groups[date] = [];
    groups[date].push(event);
    return groups;
  }, {});

  return (
    <div className="space-y-6">
      {Object.entries(groupedEvents).map(([date, dateEvents]) => (
        <div key={date}>
          <div className="flex items-center gap-3 mb-3">
            <div className="flex items-center gap-2 px-3 py-1 rounded-sm bg-white/5 border border-white/10">
              <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-xs font-mono text-muted-foreground">{date}</span>
            </div>
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-[10px] text-muted-foreground">
              {dateEvents.length} events
            </span>
          </div>
          <div className="space-y-2 pl-4 border-l border-white/10">
            {dateEvents.map((event) => (
              <ActivityEventCard 
                key={event.id} 
                event={event} 
                onClick={onNavigate}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

// ==================== MAIN ACTIVITY PAGE ====================
export default function ActivityPage() {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState("list"); // list, timeline

  const fetchActivity = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter !== "all") {
        params.type_filter = filter;
      }
      const res = await axios.get(`${API}/activity`, { params });
      setEvents(res.data.events || []);
    } catch (error) {
      console.error("Error fetching activity:", error);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchActivity();
  }, [fetchActivity]);

  // Filter by search
  const filteredEvents = events.filter(event => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      event.title?.toLowerCase().includes(query) ||
      event.description?.toLowerCase().includes(query) ||
      event.agent_name?.toLowerCase().includes(query)
    );
  });

  // Filter tabs
  const filterTabs = [
    { value: "all", label: "All Activity" },
    { value: "agent", label: "Agents" },
    { value: "trade", label: "Trades" },
    { value: "alert", label: "Alerts" }
  ];

  const getFilteredByTab = (events, tab) => {
    if (tab === "all") return events;
    if (tab === "agent") return events.filter(e => e.type.startsWith('agent_'));
    if (tab === "trade") return events.filter(e => e.type.startsWith('trade_'));
    if (tab === "alert") return events.filter(e => e.type.startsWith('alert_'));
    return events;
  };

  return (
    <div className="space-y-6" data-testid="activity-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide uppercase">
            Activity Feed
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            System events and notifications history
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-black/50 border-white/10 w-48"
            />
          </div>
          
          <Select value={viewMode} onValueChange={setViewMode}>
            <SelectTrigger className="w-32 bg-black/50 border-white/10">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="glass border-white/10">
              <SelectItem value="list">List View</SelectItem>
              <SelectItem value="timeline">Timeline</SelectItem>
            </SelectContent>
          </Select>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={fetchActivity}
            className="border-white/20"
          >
            <RefreshCw className={cn("w-4 h-4 mr-2", loading && "animate-spin")} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats */}
      <ActivityStats events={events} />

      {/* Tabs and Content */}
      <Card className="glass border-white/10">
        <CardContent className="p-0">
          <Tabs defaultValue="all" className="w-full">
            <div className="border-b border-white/10 px-4">
              <TabsList className="bg-transparent h-12">
                {filterTabs.map((tab) => (
                  <TabsTrigger 
                    key={tab.value} 
                    value={tab.value}
                    className="data-[state=active]:bg-white/10 data-[state=active]:text-white"
                  >
                    {tab.label}
                    <span className="ml-2 text-[10px] font-mono text-muted-foreground">
                      ({getFilteredByTab(filteredEvents, tab.value).length})
                    </span>
                  </TabsTrigger>
                ))}
              </TabsList>
            </div>

            {filterTabs.map((tab) => (
              <TabsContent key={tab.value} value={tab.value} className="p-4 mt-0">
                {loading ? (
                  <div className="space-y-3">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="h-20 bg-white/5 rounded-sm animate-pulse" />
                    ))}
                  </div>
                ) : getFilteredByTab(filteredEvents, tab.value).length > 0 ? (
                  viewMode === "timeline" ? (
                    <TimelineView 
                      events={getFilteredByTab(filteredEvents, tab.value)} 
                      onNavigate={navigate}
                    />
                  ) : (
                    <div className="space-y-2">
                      {getFilteredByTab(filteredEvents, tab.value).map((event) => (
                        <ActivityEventCard 
                          key={event.id} 
                          event={event} 
                          onClick={navigate}
                        />
                      ))}
                    </div>
                  )
                ) : (
                  <div className="text-center py-16">
                    <Activity className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-30" />
                    <h3 className="font-heading text-lg mb-2">No Activity Yet</h3>
                    <p className="text-sm text-muted-foreground">
                      {tab.value === "all" 
                        ? "Events will appear here as your agents operate"
                        : `No ${tab.label.toLowerCase()} events found`
                      }
                    </p>
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
