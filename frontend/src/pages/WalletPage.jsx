import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Wallet as WalletIcon, CreditCard, Plus, ArrowDownRight, ArrowUpRight, CheckCircle, Clock, XCircle, RefreshCw, DollarSign, TrendingUp } from "lucide-react";
import { toast } from "sonner";
import { paymentsAPI, dashboardAPI } from "@/lib/api";

const FUNDING_PACKAGES = [
  { id: "starter", name: "Inicial", amount: 50, description: "Desplegar 1 agente" },
  { id: "growth", name: "Crecimiento", amount: 100, description: "Desplegar 2 agentes" },
  { id: "pro", name: "Pro", amount: 250, description: "Desplegar 5 agentes" },
  { id: "enterprise", name: "Empresa", amount: 500, description: "Agentes ilimitados" },
];

const StatusBadge = ({ status }) => {
  const config = {
    completed: { icon: CheckCircle, color: "evo-badge-success", label: "Completado" },
    paid: { icon: CheckCircle, color: "evo-badge-success", label: "Pagado" },
    pending: { icon: Clock, color: "evo-badge-warning", label: "Pendiente" },
    failed: { icon: XCircle, color: "evo-badge-danger", label: "Fallido" },
  };
  const cfg = config[status] || config.pending;
  const Icon = cfg.icon;
  return (
    <span className={cfg.color}>
      <Icon className="w-3 h-3" /> {cfg.label}
    </span>
  );
};

const TransactionRow = ({ tx }) => {
  const isDeposit = tx.type === 'stripe' || tx.type === 'deposit';
  return (
    <div className="flex items-center gap-4 p-4 hover:bg-white/[0.02] transition-colors rounded-lg">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${isDeposit ? "bg-green-500/10" : "bg-red-500/10"}`}>
        {isDeposit ? <ArrowDownRight className="w-5 h-5 text-green-400" /> : <ArrowUpRight className="w-5 h-5 text-red-400" />}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground">{tx.type === 'stripe' ? 'Pago con Tarjeta' : tx.type.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</p>
        <p className="text-xs text-muted-foreground mt-0.5 font-mono">
          {new Date(tx.created_at).toLocaleDateString('es-ES', { month: 'short', day: 'numeric', year: 'numeric' })} {new Date(tx.created_at).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
      <div className="text-right shrink-0">
        <p className={`text-sm font-semibold font-mono ${isDeposit ? "text-green-400" : "text-red-400"}`}>
          {isDeposit ? "+" : "-"}${tx.amount.toFixed(2)}
        </p>
        <div className="mt-1"><StatusBadge status={tx.status} /></div>
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

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) checkPaymentStatus(sessionId);
  }, [searchParams]);

  const checkPaymentStatus = async (sessionId) => {
    try {
      const response = await paymentsAPI.status(sessionId);
      if (response.data.payment_status === 'paid') toast.success(`¡Pago de $${response.data.amount} exitoso!`);
      else toast.info(`Estado del pago: ${response.data.payment_status}`);
    } catch (error) { console.error("Error al verificar pago:", error); }
  };

  const fetchData = async () => {
    try {
      const [txRes, statsRes] = await Promise.all([paymentsAPI.transactions(), dashboardAPI.stats()]);
      setTransactions(txRes.data.transactions || []);
      setStats(statsRes.data);
    } catch (error) { console.error("Error al obtener datos de billetera:", error); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const handleFund = async () => {
    const amount = customAmount ? parseFloat(customAmount) : selectedPackage.amount;
    if (!amount || amount < 1) { toast.error("Monto inválido"); return; }
    setProcessing(true);
    try {
      const response = await paymentsAPI.createSession(amount, selectedPackage?.id || 'custom');
      if (response.data.checkout_url) window.location.href = response.data.checkout_url;
    } catch (error) { toast.error("Error al crear la sesión de pago"); setProcessing(false); }
  };

  const totalFunded = transactions.filter(t => t.status === 'completed' || t.status === 'paid').reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="min-h-screen bg-background" data-testid="wallet-page">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl font-bold uppercase tracking-wide text-foreground">Billetera</h1>
            <p className="text-sm text-muted-foreground mt-1">Gestiona tu saldo y financia tus agentes</p>
          </div>
          <button onClick={() => setFundDialogOpen(true)} className="evo-button-primary px-5 py-2.5 text-sm rounded-lg" data-testid="fund-wallet-btn">
            <Plus className="w-4 h-4" /> <span className="ml-1.5">Agregar Fondos</span>
          </button>
        </div>

        {/* Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: "Saldo Total", value: `$${(stats?.finances?.total_balance || 0).toFixed(2)}`, sub: "En todos los agentes", icon: <WalletIcon className="w-5 h-5 text-cyan-400" />, iconBg: "bg-cyan-500/10", color: "text-foreground" },
            { label: "Total Financiado", value: `$${totalFunded.toFixed(2)}`, sub: "Depósitos totales", icon: <ArrowDownRight className="w-5 h-5 text-green-400" />, iconBg: "bg-green-500/10", color: "text-green-400" },
            { label: "ROI", value: `${(stats?.finances?.avg_roi || 0) >= 0 ? "+" : ""}${(stats?.finances?.avg_roi || 0).toFixed(1)}%`, sub: "Retorno promedio", icon: <TrendingUp className="w-5 h-5 text-purple-400" />, iconBg: "bg-purple-500/10", color: (stats?.finances?.avg_roi || 0) >= 0 ? "text-green-400" : "text-red-400" },
          ].map((card, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className="glass-card rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${card.iconBg}`}>{card.icon}</div>
                <span className="evo-section-title">{card.label}</span>
              </div>
              <p className={`text-3xl font-semibold tracking-tight font-mono ${card.color}`}>{card.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{card.sub}</p>
            </motion.div>
          ))}
        </div>

        {/* Funding Packages */}
        <div>
          <h2 className="evo-section-title mb-4 text-sm">Paquetes de Financiamiento</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {FUNDING_PACKAGES.map((pkg) => (
              <motion.button key={pkg.id} whileHover={{ borderColor: "rgba(0,243,255,0.3)" }} onClick={() => { setSelectedPackage(pkg); setCustomAmount(""); setFundDialogOpen(true); }}
                className="glass-card rounded-xl p-5 text-left transition-all hover:border-cyan-500/30">
                <p className="evo-section-title">{pkg.name}</p>
                <p className="text-2xl font-semibold text-foreground mt-1 font-mono">${pkg.amount}</p>
                <p className="text-xs text-muted-foreground mt-1">{pkg.description}</p>
                <div className="mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="evo-section-title text-cyan-400">Seleccionar →</span>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Transactions */}
        <div className="glass-card rounded-xl">
          <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
            <h2 className="text-base font-semibold text-foreground">Historial de Transacciones</h2>
            <button onClick={fetchData} className="p-2 rounded-lg hover:bg-white/5 transition-colors" aria-label="Actualizar">
              <RefreshCw className={`w-4 h-4 text-muted-foreground ${loading && "animate-spin"}`} />
            </button>
          </div>
          {loading ? (<div className="p-6 space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-16 bg-white/5 rounded-lg animate-pulse" />)}</div>)
            : transactions.length > 0 ? (<div className="divide-y divide-white/5 max-h-[480px] overflow-y-auto">{transactions.map((tx) => <TransactionRow key={tx.id} tx={tx} />)}</div>)
            : (<div className="text-center py-16 px-6">
                <div className="w-16 h-16 rounded-lg bg-white/5 flex items-center justify-center mx-auto mb-4"><WalletIcon className="w-8 h-8 text-muted-foreground" /></div>
                <h3 className="text-base font-semibold text-foreground mb-1">Sin Transacciones</h3>
                <p className="text-sm text-muted-foreground mb-6">Agrega fondos para comenzar</p>
                <button onClick={() => setFundDialogOpen(true)} className="evo-button-primary px-5 py-2.5 text-sm"><Plus className="w-4 h-4" /> Agregar Fondos</button>
              </div>)}
        </div>
      </div>

      {/* Fund Dialog */}
      {fundDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={() => setFundDialogOpen(false)} role="dialog" aria-modal="true" aria-label="Financiar billetera">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="relative glass-card rounded-xl w-full max-w-lg overflow-hidden">
            <div className="px-6 py-5 border-b border-white/5">
              <h2 className="text-lg font-semibold text-foreground">Financiar Billetera</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Elige un paquete o ingresa un monto personalizado</p>
            </div>
            <div className="p-6 space-y-5">
              <div className="grid grid-cols-2 gap-3">
                {FUNDING_PACKAGES.map((pkg) => (
                  <button key={pkg.id} onClick={() => { setSelectedPackage(pkg); setCustomAmount(""); }}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${selectedPackage?.id === pkg.id ? "border-cyan-500/50 bg-cyan-500/5" : "border-white/5 hover:border-white/10"}`}>
                    <p className="evo-section-title">{pkg.name}</p>
                    <p className="text-xl font-semibold text-foreground mt-0.5 font-mono">${pkg.amount}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{pkg.description}</p>
                  </button>
                ))}
              </div>
              <div className="space-y-2">
                <label className="evo-section-title block">Monto personalizado</label>
                <div className="relative">
                  <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input type="number" min="1" step="1" placeholder="0.00" value={customAmount} onChange={(e) => { setCustomAmount(e.target.value); setSelectedPackage(null); }} className="evo-input pl-10" data-testid="custom-amount-input" />
                </div>
              </div>
              <div className="pt-4 border-t border-white/5">
                <p className="evo-section-title mb-3 block">Métodos de Pago</p>
                <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-white/5 border border-white/5">
                  <CreditCard className="w-4 h-4 text-cyan-400" /><span className="text-sm text-foreground">Tarjeta vía Stripe</span>
                </div>
              </div>
            </div>
            <div className="px-6 py-4 flex gap-2.5 border-t border-white/5 bg-white/[0.02]">
              <button onClick={() => setFundDialogOpen(false)} className="evo-button-outline flex-1 py-2.5 text-sm">Cancelar</button>
              <button onClick={handleFund} disabled={processing || (!selectedPackage && !customAmount)} className="evo-button-primary flex-1 py-2.5 text-sm disabled:opacity-50" data-testid="confirm-fund-btn">
                {processing ? <span className="flex items-center justify-center gap-2"><RefreshCw className="w-4 h-4 animate-spin" /> Procesando...</span> : `Pay $${customAmount || selectedPackage?.amount || 0}`}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
