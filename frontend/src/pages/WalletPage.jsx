import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Wallet as WalletIcon,
  CreditCard,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle,
  Clock,
  XCircle,
  RefreshCw,
  DollarSign,
  TrendingUp
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const FUNDING_PACKAGES = [
  { id: "starter", name: "Inicial", amount: 50, description: "Desplegar 1 agente" },
  { id: "growth", name: "Crecimiento", amount: 100, description: "Desplegar 2 agentes" },
  { id: "pro", name: "Pro", amount: 250, description: "Desplegar 5 agentes" },
  { id: "enterprise", name: "Empresa", amount: 500, description: "Agentes ilimitados" },
];

const StatusBadge = ({ status }) => {
  const config = {
    completed: { icon: CheckCircle, color: "text-[#34C759]", bg: "bg-[#34C759]/10", label: "Completado" },
    paid: { icon: CheckCircle, color: "text-[#34C759]", bg: "bg-[#34C759]/10", label: "Pagado" },
    pending: { icon: Clock, color: "text-[#FF9500]", bg: "bg-[#FF9500]/10", label: "Pendiente" },
    failed: { icon: XCircle, color: "text-[#FF3B30]", bg: "bg-[#FF3B30]/10", label: "Fallido" },
  };

  const cfg = config[status] || config.pending;
  const Icon = cfg.icon;

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium rounded-full ${cfg.color} ${cfg.bg}`}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
};

const TransactionRow = ({ tx }) => {
  const isDeposit = tx.type === 'stripe' || tx.type === 'deposit';

  return (
    <div className="flex items-center gap-4 p-4 hover:bg-[#F5F3EF] transition-colors rounded-xl">
      <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${isDeposit ? "bg-[#34C759]/10" : "bg-[#FF3B30]/10"}`}>
        {isDeposit ? (
          <ArrowDownRight className="w-5 h-5 text-[#34C759]" />
        ) : (
          <ArrowUpRight className="w-5 h-5 text-[#FF3B30]" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-[15px] font-medium text-[#1a1a1a]">
          {tx.type === 'stripe' ? 'Pago con Tarjeta' : tx.type.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
        </p>
        <p className="text-[13px] text-[#86868b] mt-0.5">
          {new Date(tx.created_at).toLocaleDateString('es-ES', { month: 'short', day: 'numeric', year: 'numeric' })} a las {new Date(tx.created_at).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>

      <div className="text-right shrink-0">
        <p className={`text-[15px] font-semibold ${isDeposit ? "text-[#34C759]" : "text-[#FF3B30]"}`}>
          {isDeposit ? "+" : "-"}${tx.amount.toFixed(2)}
        </p>
        <div className="mt-1">
          <StatusBadge status={tx.status} />
        </div>
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
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, [searchParams]);

  const checkPaymentStatus = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      if (response.data.payment_status === 'paid') {
        toast.success(`¡Pago de $${response.data.amount} exitoso!`);
      } else {
        toast.info(`Estado del pago: ${response.data.payment_status}`);
      }
    } catch (error) {
      console.error("Error al verificar pago:", error);
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
      console.error("Error al obtener datos de billetera:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
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
      toast.error("Por favor ingresa un monto válido");
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
      toast.error("Error al crear la sesión de pago");
      setProcessing(false);
    }
  };

  const totalFunded = transactions
    .filter(t => t.status === 'completed' || t.status === 'paid')
    .reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="min-h-screen bg-[#F5F3EF]" data-testid="wallet-page">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-[28px] font-semibold text-[#1a1a1a] tracking-tight">
              Billetera
            </h1>
            <p className="text-[15px] text-[#86868b] mt-1">
              Gestiona tu saldo y financia tus agentes
            </p>
          </div>

          <button
            onClick={() => setFundDialogOpen(true)}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#D97757] text-white rounded-full text-[14px] font-medium hover:bg-[#D97757]/90 transition-colors shadow-sm shadow-[#D97757]/20"
            data-testid="fund-wallet-btn"
          >
            <Plus className="w-4 h-4" />
            Add Funds
          </button>
        </div>

        {/* Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-black/5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-[#D97757]/10 flex items-center justify-center">
                <WalletIcon className="w-5 h-5 text-[#D97757]" />
              </div>
              <span className="text-[13px] font-medium text-[#86868b]">
                Saldo Total
              </span>
            </div>
            <p className="text-[32px] font-semibold text-[#1a1a1a] tracking-tight">
              ${(stats?.finances?.total_balance || 0).toFixed(2)}
            </p>
            <p className="text-[13px] text-[#86868b] mt-1">
              En todos los agentes
            </p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-black/5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-[#34C759]/10 flex items-center justify-center">
                <ArrowDownRight className="w-5 h-5 text-[#34C759]" />
              </div>
              <span className="text-[13px] font-medium text-[#86868b]">
                Total Financiado
              </span>
            </div>
            <p className="text-[32px] font-semibold text-[#34C759] tracking-tight">
              ${totalFunded.toFixed(2)}
            </p>
            <p className="text-[13px] text-[#86868b] mt-1">
              Depósitos totales
            </p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-black/5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-[#D97757]/10 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-[#D97757]" />
              </div>
              <span className="text-[13px] font-medium text-[#86868b]">
                ROI
              </span>
            </div>
            <p className={`text-[32px] font-semibold tracking-tight ${(stats?.finances?.avg_roi || 0) >= 0 ? "text-[#34C759]" : "text-[#FF3B30]"}`}>
              {(stats?.finances?.avg_roi || 0) >= 0 ? "+" : ""}
              {(stats?.finances?.avg_roi || 0).toFixed(1)}%
            </p>
            <p className="text-[13px] text-[#86868b] mt-1">
              Retorno promedio
            </p>
          </div>
        </div>

        {/* Funding Packages */}
        <div>
          <h2 className="text-[20px] font-semibold text-[#1a1a1a] mb-4">Paquetes de Financiamiento</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {FUNDING_PACKAGES.map((pkg) => (
              <button
                key={pkg.id}
                onClick={() => {
                  setSelectedPackage(pkg);
                  setCustomAmount("");
                  setFundDialogOpen(true);
                }}
                className="bg-white rounded-2xl p-5 shadow-sm border border-black/5 hover:border-[#D97757]/30 hover:shadow-md transition-all text-left group"
              >
                <p className="text-[13px] font-medium text-[#86868b] uppercase tracking-wide">{pkg.name}</p>
                <p className="text-[28px] font-semibold text-[#1a1a1a] mt-1 tracking-tight">${pkg.amount}</p>
                <p className="text-[13px] text-[#86868b] mt-1">{pkg.description}</p>
                <div className="mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="text-[13px] font-medium text-[#D97757]">Seleccionar →</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Transactions */}
        <div className="bg-white rounded-2xl shadow-sm border border-black/5">
          <div className="flex items-center justify-between px-6 py-4 border-b border-black/5">
            <h2 className="text-[17px] font-semibold text-[#1a1a1a]">
              Historial de Transacciones
            </h2>
            <button
              onClick={fetchData}
              className="p-2 rounded-full hover:bg-[#F5F3EF] transition-colors"
            >
              <RefreshCw className={`w-4 h-4 text-[#86868b] ${loading && "animate-spin"}`} />
            </button>
          </div>

          {loading ? (
            <div className="p-6 space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 bg-[#F5F3EF] rounded-xl animate-pulse" />
              ))}
            </div>
          ) : transactions.length > 0 ? (
            <div className="divide-y divide-black/5 max-h-[480px] overflow-y-auto">
              {transactions.map((tx) => (
                <TransactionRow key={tx.id} tx={tx} />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 px-6">
              <div className="w-16 h-16 rounded-full bg-[#F5F3EF] flex items-center justify-center mx-auto mb-4">
                <WalletIcon className="w-8 h-8 text-[#86868b]" />
              </div>
              <h3 className="text-[17px] font-semibold text-[#1a1a1a] mb-1">Sin Transacciones</h3>
              <p className="text-[15px] text-[#86868b] mb-6">
                Agrega fondos para comenzar a desplegar agentes
              </p>
              <button
                onClick={() => setFundDialogOpen(true)}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#D97757] text-white rounded-full text-[14px] font-medium hover:bg-[#D97757]/90 transition-colors"
              >
                <Plus className="w-4 h-4" />
            Agregar Fondos
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Fund Wallet Modal */}
      {fundDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setFundDialogOpen(false)} />
          <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden">
            <div className="px-6 py-5 border-b border-black/5">
              <h2 className="text-[20px] font-semibold text-[#1a1a1a]">Financiar Billetera</h2>
              <p className="text-[13px] text-[#86868b] mt-0.5">Elige un paquete o ingresa un monto personalizado</p>
            </div>

            <div className="p-6 space-y-5">
              {/* Packages */}
              <div className="grid grid-cols-2 gap-3">
                {FUNDING_PACKAGES.map((pkg) => (
                  <button
                    key={pkg.id}
                    onClick={() => {
                      setSelectedPackage(pkg);
                      setCustomAmount("");
                    }}
                    className={`p-4 rounded-xl border-2 text-left transition-all ${
                      selectedPackage?.id === pkg.id
                        ? "border-[#D97757] bg-[#D97757]/5"
                        : "border-black/5 hover:border-black/10"
                    }`}
                  >
                    <p className="text-[13px] font-medium text-[#86868b]">{pkg.name}</p>
                    <p className="text-[22px] font-semibold text-[#1a1a1a] mt-0.5">${pkg.amount}</p>
                    <p className="text-[12px] text-[#86868b] mt-0.5">{pkg.description}</p>
                  </button>
                ))}
              </div>

              {/* Custom Amount */}
              <div className="space-y-2">
                <label className="text-[13px] font-medium text-[#86868b]">O ingresa un monto personalizado</label>
                <div className="relative">
                  <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#86868b]" />
                  <input
                    type="number"
                    min="1"
                    step="1"
                    placeholder="0.00"
                    value={customAmount}
                    onChange={(e) => {
                      setCustomAmount(e.target.value);
                      setSelectedPackage(null);
                    }}
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all"
                    data-testid="custom-amount-input"
                  />
                </div>
              </div>

              {/* Payment Methods */}
              <div className="pt-4 border-t border-black/5">
                <p className="text-[12px] font-medium text-[#86868b] uppercase tracking-wide mb-3">Métodos de Pago</p>
                <div className="flex gap-3">
                  <div className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-[#F5F3EF] border border-black/5">
                    <CreditCard className="w-4 h-4 text-[#D97757]" />
                    <span className="text-[14px] text-[#1a1a1a]">Tarjeta vía Stripe</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-[#F5F3EF] flex gap-3">
              <button
                onClick={() => setFundDialogOpen(false)}
                className="flex-1 py-3 rounded-full border border-black/10 text-[15px] font-medium text-[#1a1a1a] hover:bg-black/5 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleFund}
                disabled={processing || (!selectedPackage && !customAmount)}
                className="flex-1 py-3 rounded-full bg-[#D97757] text-white text-[15px] font-medium hover:bg-[#D97757]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="confirm-fund-btn"
              >
                {processing ? (
                  <span className="flex items-center justify-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Procesando...
                  </span>
                ) : (
                  `Pay $${customAmount || selectedPackage?.amount || 0}`
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
