import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { 
  Wallet as WalletIcon, 
  CreditCard, 
  Bitcoin, 
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle,
  Clock,
  XCircle,
  RefreshCw,
  DollarSign
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

const FUNDING_PACKAGES = [
  { id: "starter", name: "Starter", amount: 50, description: "Deploy 1 agent" },
  { id: "growth", name: "Growth", amount: 100, description: "Deploy 2 agents" },
  { id: "pro", name: "Pro", amount: 250, description: "Deploy 5 agents" },
  { id: "enterprise", name: "Enterprise", amount: 500, description: "Unlimited agents" },
];

const StatusBadge = ({ status }) => {
  const config = {
    completed: { icon: CheckCircle, color: "text-cyber-green", bg: "bg-cyber-green/10", label: "COMPLETED" },
    paid: { icon: CheckCircle, color: "text-cyber-green", bg: "bg-cyber-green/10", label: "PAID" },
    pending: { icon: Clock, color: "text-warning", bg: "bg-warning/10", label: "PENDING" },
    failed: { icon: XCircle, color: "text-destructive", bg: "bg-destructive/10", label: "FAILED" },
  };
  
  const cfg = config[status] || config.pending;
  const Icon = cfg.icon;
  
  return (
    <span className={cn(
      "inline-flex items-center gap-1 px-2 py-1 text-[10px] font-mono rounded-sm",
      cfg.color, cfg.bg
    )}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
};

const TransactionRow = ({ tx }) => {
  const isDeposit = tx.type === 'stripe' || tx.type === 'deposit';
  
  return (
    <div className="flex items-center gap-4 p-4 rounded-sm bg-white/5 border border-white/10">
      <div className={cn(
        "p-2 rounded-sm",
        isDeposit ? "bg-cyber-green/10" : "bg-destructive/10"
      )}>
        {isDeposit ? (
          <ArrowDownRight className="w-4 h-4 text-cyber-green" />
        ) : (
          <ArrowUpRight className="w-4 h-4 text-destructive" />
        )}
      </div>
      
      <div className="flex-1">
        <p className="font-mono text-sm">
          {tx.type === 'stripe' ? 'Card Payment' : tx.type.replace('_', ' ').toUpperCase()}
        </p>
        <p className="text-xs text-muted-foreground">
          {new Date(tx.created_at).toLocaleString()}
        </p>
      </div>
      
      <div className="text-right">
        <p className={cn(
          "font-mono font-semibold",
          isDeposit ? "text-cyber-green" : "text-destructive"
        )}>
          {isDeposit ? "+" : "-"}${tx.amount.toFixed(2)}
        </p>
        <StatusBadge status={tx.status} />
      </div>
    </div>
  );
};

export default function WalletPage() {
  const [searchParams] = useSearchParams();
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fundDialogOpen, setFundDialogOpen] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState(FUNDING_PACKAGES[1]);
  const [customAmount, setCustomAmount] = useState("");
  const [processing, setProcessing] = useState(false);

  // Check for returning from Stripe
  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, [searchParams]);

  const checkPaymentStatus = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      if (response.data.payment_status === 'paid') {
        toast.success(`Payment of $${response.data.amount} successful!`);
      } else {
        toast.info(`Payment status: ${response.data.payment_status}`);
      }
    } catch (error) {
      console.error("Error checking payment:", error);
    }
  };

  const fetchData = async () => {
    try {
      const [txRes, statsRes] = await Promise.all([
        axios.get(`${API}/payments/transactions`),
        axios.get(`${API}/dashboard/stats`)
      ]);
      setTransactions(txRes.data.transactions || []);
      setStats(statsRes.data);
    } catch (error) {
      console.error("Error fetching wallet data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Poll for payment status
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      const pollInterval = setInterval(() => {
        checkPaymentStatus(sessionId);
        fetchData();
      }, 2000);
      
      setTimeout(() => clearInterval(pollInterval), 10000);
      return () => clearInterval(pollInterval);
    }
  }, [searchParams]);

  const handleFund = async () => {
    const amount = customAmount ? parseFloat(customAmount) : selectedPackage.amount;
    
    if (!amount || amount < 1) {
      toast.error("Please enter a valid amount");
      return;
    }

    setProcessing(true);
    try {
      const response = await axios.post(`${API}/payments/create-session`, null, {
        params: { amount, package_type: selectedPackage?.id || 'custom' },
        headers: { origin: window.location.origin }
      });
      
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      toast.error("Failed to create payment session");
      setProcessing(false);
    }
  };

  const totalFunded = transactions
    .filter(t => t.status === 'completed' || t.status === 'paid')
    .reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="space-y-6" data-testid="wallet-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide uppercase">
            Wallet
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Fund your agents with card or crypto
          </p>
        </div>
        
        <Dialog open={fundDialogOpen} onOpenChange={setFundDialogOpen}>
          <DialogTrigger asChild>
            <Button 
              className="bg-primary text-black hover:bg-primary/90 font-bold uppercase tracking-widest text-xs"
              data-testid="fund-wallet-btn"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Funds
            </Button>
          </DialogTrigger>
          <DialogContent className="glass border-white/10 max-w-lg">
            <DialogHeader>
              <DialogTitle className="font-heading uppercase tracking-wider">
                Fund Your Wallet
              </DialogTitle>
              <DialogDescription>
                Choose a package or enter a custom amount
              </DialogDescription>
            </DialogHeader>
            
            <div className="py-4 space-y-4">
              {/* Packages */}
              <div className="grid grid-cols-2 gap-3">
                {FUNDING_PACKAGES.map((pkg) => (
                  <div
                    key={pkg.id}
                    className={cn(
                      "p-4 rounded-sm border cursor-pointer transition-colors",
                      selectedPackage?.id === pkg.id
                        ? "border-primary bg-primary/10"
                        : "border-white/10 hover:border-white/30"
                    )}
                    onClick={() => {
                      setSelectedPackage(pkg);
                      setCustomAmount("");
                    }}
                  >
                    <p className="font-heading font-bold">{pkg.name}</p>
                    <p className="font-mono text-xl text-primary">${pkg.amount}</p>
                    <p className="text-xs text-muted-foreground mt-1">{pkg.description}</p>
                  </div>
                ))}
              </div>
              
              {/* Custom Amount */}
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider">Or enter custom amount</Label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    type="number"
                    min="1"
                    step="1"
                    placeholder="0.00"
                    value={customAmount}
                    onChange={(e) => {
                      setCustomAmount(e.target.value);
                      setSelectedPackage(null);
                    }}
                    className="pl-9 bg-black/50 border-white/10"
                    data-testid="custom-amount-input"
                  />
                </div>
              </div>

              {/* Payment Methods */}
              <div className="pt-4 border-t border-white/10">
                <p className="text-xs text-muted-foreground mb-3">PAYMENT METHODS</p>
                <div className="flex gap-3">
                  <div className="flex items-center gap-2 px-3 py-2 rounded-sm bg-white/5 border border-white/10">
                    <CreditCard className="w-4 h-4 text-primary" />
                    <span className="text-sm">Card</span>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-2 rounded-sm bg-white/5 border border-white/10">
                    <Bitcoin className="w-4 h-4 text-warning" />
                    <span className="text-sm">Crypto</span>
                  </div>
                </div>
              </div>
            </div>
            
            <DialogFooter>
              <Button 
                variant="outline" 
                onClick={() => setFundDialogOpen(false)}
                className="border-white/20"
              >
                Cancel
              </Button>
              <Button 
                onClick={handleFund}
                disabled={processing || (!selectedPackage && !customAmount)}
                className="bg-primary text-black hover:bg-primary/90"
                data-testid="confirm-fund-btn"
              >
                {processing ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Processing...
                  </span>
                ) : (
                  `Pay $${customAmount || selectedPackage?.amount || 0}`
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Balance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="glass border-white/10 glow-cyan">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-sm bg-primary/10">
                <WalletIcon className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xs font-heading uppercase tracking-wider text-muted-foreground">
                Total Balance
              </span>
            </div>
            <p className="font-mono text-3xl font-bold text-primary">
              ${(stats?.finances?.total_balance || 0).toFixed(2)}
            </p>
            <p className="text-xs text-muted-foreground mt-2">
              Across all agents
            </p>
          </CardContent>
        </Card>
        
        <Card className="glass border-white/10">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-sm bg-cyber-green/10">
                <ArrowDownRight className="w-5 h-5 text-cyber-green" />
              </div>
              <span className="text-xs font-heading uppercase tracking-wider text-muted-foreground">
                Total Funded
              </span>
            </div>
            <p className="font-mono text-3xl font-bold text-cyber-green">
              ${totalFunded.toFixed(2)}
            </p>
            <p className="text-xs text-muted-foreground mt-2">
              All time deposits
            </p>
          </CardContent>
        </Card>
        
        <Card className="glass border-white/10">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-sm bg-secondary/10">
                <ArrowUpRight className="w-5 h-5 text-secondary" />
              </div>
              <span className="text-xs font-heading uppercase tracking-wider text-muted-foreground">
                ROI
              </span>
            </div>
            <p className={cn(
              "font-mono text-3xl font-bold",
              (stats?.finances?.avg_roi || 0) >= 0 ? "text-cyber-green" : "text-destructive"
            )}>
              {(stats?.finances?.avg_roi || 0) >= 0 ? "+" : ""}
              {(stats?.finances?.avg_roi || 0).toFixed(1)}%
            </p>
            <p className="text-xs text-muted-foreground mt-2">
              Average return
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Transactions */}
      <Card className="glass border-white/10">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="font-heading text-sm tracking-wider uppercase text-muted-foreground">
              Transaction History
            </CardTitle>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={fetchData}
              className="text-muted-foreground"
            >
              <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 bg-white/5 rounded-sm animate-pulse" />
              ))}
            </div>
          ) : transactions.length > 0 ? (
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {transactions.map((tx) => (
                <TransactionRow key={tx.id} tx={tx} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <WalletIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="font-heading text-lg mb-2">No Transactions Yet</h3>
              <p className="text-sm text-muted-foreground mb-6">
                Add funds to start deploying agents
              </p>
              <Button 
                onClick={() => setFundDialogOpen(true)}
                className="bg-primary text-black hover:bg-primary/90"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Funds
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
