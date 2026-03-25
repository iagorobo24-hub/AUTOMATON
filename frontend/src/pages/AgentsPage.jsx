import { useState, useEffect } from "react";
import { 
  Bot, 
  Plus, 
  Copy, 
  Trash2, 
  Activity,
  TrendingUp,
  TrendingDown,
  Zap,
  MoreVertical,
  Play,
  Pause,
  RefreshCw
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AgentCard = ({ agent, onReplicate, onDestroy, onSimulate }) => {
  const statusConfig = {
    active: { 
      class: "status-active", 
      label: "ACTIVO", 
      color: "text-primary",
      bgColor: "bg-primary/10"
    },
    replicating: { 
      class: "status-replicating", 
      label: "REPLICANDO", 
      color: "text-cyber-green",
      bgColor: "bg-cyber-green/10"
    },
    dying: { 
      class: "status-dying", 
      label: "EN RIESGO", 
      color: "text-destructive",
      bgColor: "bg-destructive/10"
    },
    dead: { 
      class: "status-dead", 
      label: "TERMINADO", 
      color: "text-muted-foreground",
      bgColor: "bg-white/5"
    },
    paused: {
      class: "status-active",
      label: "PAUSADO",
      color: "text-warning",
      bgColor: "bg-warning/10"
    },
    hibernating: {
      class: "status-active",
      label: "HIBERNANDO",
      color: "text-secondary",
      bgColor: "bg-secondary/10"
    }
  };

  // Extract data from new schema structure
  const finances = agent.finances || {};
  const performance = agent.performance || {};
  const tradingStats = agent.trading_stats || {};
  const lineage = agent.lineage || {};
  
  const balance = finances.current_balance ?? agent.balance ?? 0;
  const initialBalance = finances.initial_capital ?? agent.initial_balance ?? 100;
  const roi = performance.roi_percent ?? agent.roi ?? 0;
  const tradesCount = tradingStats.total_trades ?? agent.trades_count ?? 0;
  const successfulTrades = tradingStats.winning_trades ?? agent.successful_trades ?? 0;
  const childrenCount = lineage.children_ids?.length ?? agent.children_ids?.length ?? 0;
  const generation = agent.generation ?? 1;

  const config = statusConfig[agent.status] || statusConfig.active;
  const healthPercent = Math.max(0, Math.min(100, (balance / initialBalance) * 100));

  return (
    <Card className={cn(
      "glass border-white/10 card-hover agent-card",
      config.class
    )} data-testid={`agent-card-${agent.id}`}>
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={cn("p-2 rounded-sm", config.bgColor)}>
              <Bot className={cn("w-5 h-5", config.color)} />
            </div>
            <div>
              <h3 className="font-mono font-semibold text-sm">{agent.name}</h3>
              <p className="text-xs text-muted-foreground uppercase">{agent.type}</p>
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="glass border-white/10">
              <DropdownMenuItem 
                onClick={() => onSimulate(agent.id, 10)}
                className="gap-2"
              >
                <TrendingUp className="w-4 h-4 text-cyber-green" />
                Simular +€10
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => onSimulate(agent.id, -10)}
                className="gap-2"
              >
                <TrendingDown className="w-4 h-4 text-destructive" />
                Simular -€10
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => onReplicate(agent.id)}
                className="gap-2"
                disabled={balance < 50 || agent.status === 'dead'}
              >
                <Copy className="w-4 h-4 text-secondary" />
                Replicar
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => onDestroy(agent.id)}
                className="gap-2 text-destructive"
                disabled={agent.status === 'dead'}
              >
                <Trash2 className="w-4 h-4" />
                Destruir
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Status Badge */}
        <div className="mb-4">
          <span className={cn(
            "px-2 py-1 text-[10px] font-mono font-semibold rounded-sm border",
            config.color,
            config.bgColor,
            agent.status === 'active' && "border-primary/30",
            agent.status === 'replicating' && "border-cyber-green/30",
            agent.status === 'dying' && "border-destructive/30",
            agent.status === 'dead' && "border-white/10"
          )}>
            {config.label}
          </span>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-[10px] font-heading uppercase text-muted-foreground mb-1">Saldo</p>
            <p className="font-mono font-bold text-lg">€{balance.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-[10px] font-heading uppercase text-muted-foreground mb-1">ROI</p>
            <p className={cn(
              "font-mono font-bold text-lg",
              roi >= 0 ? "text-cyber-green" : "text-destructive"
            )}>
              {roi >= 0 ? "+" : ""}{roi.toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Health Bar */}
        <div>
          <div className="flex justify-between text-[10px] text-muted-foreground mb-1">
            <span>SALUD</span>
            <span>{healthPercent.toFixed(0)}%</span>
          </div>
          <Progress 
            value={healthPercent} 
            className="h-1.5 bg-white/10"
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-2 mt-4 pt-4 border-t border-white/10">
          <div className="text-center">
            <p className="text-[10px] text-muted-foreground">GEN</p>
            <p className="font-mono text-sm text-secondary">{generation}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-muted-foreground">TRADES</p>
            <p className="font-mono text-sm">{tradesCount}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-muted-foreground">GANADOS</p>
            <p className="font-mono text-sm text-cyber-green">{successfulTrades}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-muted-foreground">CLONES</p>
            <p className="font-mono text-sm">{childrenCount}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default function AgentsPage() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newAgent, setNewAgent] = useState({
    name: "",
    type: "crypto_analyzer",
    initial_balance: 100
  });

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${API}/agents`);
      setAgents(response.data.agents || []);
    } catch (error) {
      console.error("Error fetching agents:", error);
      toast.error("Error al cargar agentes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleCreateAgent = async () => {
    if (!newAgent.name) {
      toast.error("El nombre del agente es obligatorio");
      return;
    }

    try {
      await axios.post(`${API}/agents`, newAgent);
      toast.success("Agente creado correctamente");
      setCreateDialogOpen(false);
      setNewAgent({ name: "", type: "crypto_analyzer", initial_balance: 100 });
      fetchAgents();
    } catch (error) {
      toast.error("Error al crear agente");
    }
  };

  const handleReplicate = async (agentId) => {
    try {
      await axios.post(`${API}/agents/${agentId}/replicate`);
      toast.success("Agente replicado correctamente");
      fetchAgents();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al replicar agente");
    }
  };

  const handleDestroy = async (agentId) => {
    try {
      await axios.delete(`${API}/agents/${agentId}`);
      toast.success("Agente destruido");
      fetchAgents();
    } catch (error) {
      toast.error("Error al destruir agente");
    }
  };

  const handleSimulate = async (agentId, profit) => {
    try {
      await axios.post(`${API}/agents/${agentId}/simulate-trade?profit=${profit}`);
      toast.success(`Trade simulado: ${profit >= 0 ? '+' : ''}€${profit}`);
      fetchAgents();
    } catch (error) {
      toast.error("Error al simular trade");
    }
  };

  const activeCount = agents.filter(a => a.status === 'active').length;
  const replicatingCount = agents.filter(a => a.status === 'replicating').length;
  const dyingCount = agents.filter(a => a.status === 'dying').length;
  const deadCount = agents.filter(a => a.status === 'dead').length;

  return (
    <div className="space-y-6" data-testid="agents-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide uppercase">
            Gestión de Agentes
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Despliega, replica y gestiona agentes autónomos
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            size="sm"
            onClick={fetchAgents}
            className="border-white/20"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualizar
          </Button>
          
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                className="bg-primary text-black hover:bg-primary/90 font-bold uppercase tracking-widest text-xs"
                data-testid="create-agent-btn"
              >
                <Plus className="w-4 h-4 mr-2" />
                Desplegar Agente
              </Button>
            </DialogTrigger>
            <DialogContent className="glass border-white/10">
              <DialogHeader>
                <DialogTitle className="font-heading uppercase tracking-wider">
                  Desplegar Nuevo Agente
                </DialogTitle>
                <DialogDescription>
                  Crea un nuevo agente autónomo con financiación inicial
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider">Nombre del Agente</Label>
                  <Input
                    placeholder="Alpha-001"
                    value={newAgent.name}
                    onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                    className="bg-black/50 border-white/10"
                    data-testid="agent-name-input"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider">Tipo de Agente</Label>
                  <Select
                    value={newAgent.type}
                    onValueChange={(value) => setNewAgent({ ...newAgent, type: value })}
                  >
                    <SelectTrigger className="bg-black/50 border-white/10" data-testid="agent-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="glass border-white/10">
                      <SelectItem value="crypto_analyzer">Analizador Crypto</SelectItem>
                      <SelectItem value="business_scout">Explorador de Negocios</SelectItem>
                      <SelectItem value="trader">Trader</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider">Saldo Inicial ($)</Label>
                  <Input
                    type="number"
                    min="10"
                    step="10"
                    value={newAgent.initial_balance}
                    onChange={(e) => setNewAgent({ ...newAgent, initial_balance: parseFloat(e.target.value) })}
                    className="bg-black/50 border-white/10"
                    data-testid="agent-balance-input"
                  />
                </div>
              </div>
              
              <DialogFooter>
                <Button 
                  variant="outline" 
                  onClick={() => setCreateDialogOpen(false)}
                  className="border-white/20"
                >
                  Cancelar
                </Button>
                <Button 
                  onClick={handleCreateAgent}
                  className="bg-primary text-black hover:bg-primary/90"
                  data-testid="confirm-create-agent-btn"
                >
                  Desplegar
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-sm border border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary" />
            <span className="text-xs text-muted-foreground">ACTIVOS</span>
          </div>
          <p className="font-mono text-2xl font-bold mt-1">{activeCount}</p>
        </div>
        <div className="glass p-4 rounded-sm border border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-cyber-green animate-pulse" />
            <span className="text-xs text-muted-foreground">REPLICANDO</span>
          </div>
          <p className="font-mono text-2xl font-bold mt-1 text-cyber-green">{replicatingCount}</p>
        </div>
        <div className="glass p-4 rounded-sm border border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
            <span className="text-xs text-muted-foreground">EN RIESGO</span>
          </div>
          <p className="font-mono text-2xl font-bold mt-1 text-destructive">{dyingCount}</p>
        </div>
        <div className="glass p-4 rounded-sm border border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-white/30" />
            <span className="text-xs text-muted-foreground">TERMINADOS</span>
          </div>
          <p className="font-mono text-2xl font-bold mt-1 text-muted-foreground">{deadCount}</p>
        </div>
      </div>

      {/* Agents Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-64 bg-white/5 rounded-sm animate-pulse" />
          ))}
        </div>
      ) : agents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onReplicate={handleReplicate}
              onDestroy={handleDestroy}
              onSimulate={handleSimulate}
            />
          ))}
        </div>
      ) : (
        <Card className="glass border-white/10">
          <CardContent className="py-16 text-center">
            <Bot className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="font-heading text-lg mb-2">Sin Agentes Desplegados</h3>
            <p className="text-sm text-muted-foreground mb-6">
              Despliega tu primer agente autónomo para comenzar
            </p>
            <Button 
              onClick={() => setCreateDialogOpen(true)}
              className="bg-primary text-black hover:bg-primary/90"
            >
              <Plus className="w-4 h-4 mr-2" />
              Desplegar Primer Agente
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
