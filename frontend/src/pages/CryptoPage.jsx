import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, RefreshCw, Search, Activity } from "lucide-react";
import { XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";
import { cryptoAPI } from "@/lib/api";

const GREEN = "#00FF88";
const RED = "#FF003C";
const CYAN = "#00F3FF";

const formatNumber = (num) => {
  if (num >= 1e12) return `€${(num / 1e12).toFixed(2)}T`;
  if (num >= 1e9) return `€${(num / 1e9).toFixed(2)}B`;
  if (num >= 1e6) return `€${(num / 1e6).toFixed(2)}M`;
  if (num >= 1e3) return `€${(num / 1e3).toFixed(2)}K`;
  return `€${num?.toFixed(2) || 0}`;
};

const formatPrice = (price) => {
  if (price == null) return "€0";
  if (price < 0.0001) return `€${price.toFixed(8)}`;
  if (price < 0.01) return `€${price.toFixed(6)}`;
  if (price < 1) return `€${price.toFixed(4)}`;
  return `€${price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
};

const PERIODS = [
  { label: "1D", days: 1 }, { label: "7D", days: 7 }, { label: "30D", days: 30 }, { label: "90D", days: 90 },
];

const CoinChart = ({ coinId }) => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(7);

  useEffect(() => {
    const fetchChart = async () => {
      setLoading(true);
      try {
        const response = await cryptoAPI.history(coinId, days);
        const prices = response.data.prices || [];
        setChartData(prices.map(([timestamp, price]) => ({ time: new Date(timestamp).toLocaleDateString(), price })));
      } catch (error) { console.error("Error fetching chart:", error); }
      finally { setLoading(false); }
    };
    if (coinId) fetchChart();
  }, [coinId, days]);

  if (loading) return <div className="flex h-72 items-center justify-center"><RefreshCw className="h-6 w-6 animate-spin text-cyan-400" /></div>;

  return (
    <div>
      <div className="mb-4 flex gap-1.5">
        {PERIODS.map(({ label, days: d }) => (
          <button key={d} onClick={() => setDays(d)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${days === d ? "bg-cyan-500/15 text-cyan-400 ring-1 ring-cyan-500/20" : "text-muted-foreground hover:text-foreground hover:bg-white/5"}`}>
            {label}
          </button>
        ))}
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CYAN} stopOpacity={0.15} />
                <stop offset="95%" stopColor={CYAN} stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: "#6B7280", fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: "#6B7280", fontSize: 11 }} tickFormatter={(v) => `€${v.toLocaleString()}`} domain={["auto", "auto"]} />
            <Tooltip contentStyle={{ background: "hsl(240 10% 6%)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10, boxShadow: "0 8px 24px rgba(0,0,0,0.4)", fontSize: 12 }} formatter={(value) => [formatPrice(value), "Price"]} />
            <Area type="monotone" dataKey="price" stroke={CYAN} strokeWidth={2} fillOpacity={1} fill="url(#cyanGradient)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

/* ─── Main Page ─── */
export default function CryptoPage() {
  const [coins, setCoins] = useState([]);
  const [trending, setTrending] = useState([]);
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    try {
      const [coinsRes, trendingRes] = await Promise.all([
        cryptoAPI.topCoins(),
        cryptoAPI.trending(),
      ]);
      setCoins(coinsRes.data.coins || []);
      setTrending(trendingRes.data.trending || []);
      if (!selectedCoin && coinsRes.data.coins?.length > 0) setSelectedCoin(coinsRes.data.coins[0]);
    } catch (error) { console.error("Error fetching crypto data:", error); }
    finally { setLoading(false); setRefreshing(false); }
  }, [selectedCoin]);

  useEffect(() => { fetchData(); const interval = setInterval(() => fetchData(true), 60000); return () => clearInterval(interval); }, [fetchData]);

  const filteredCoins = coins.filter((coin) => coin.name.toLowerCase().includes(searchQuery.toLowerCase()) || coin.symbol.toLowerCase().includes(searchQuery.toLowerCase()));

  const handleTrendingClick = (trendingCoin) => {
    const fullCoin = coins.find((c) => c.id === trendingCoin.id);
    if (fullCoin) setSelectedCoin(fullCoin);
    else setSelectedCoin({ id: trendingCoin.id, name: trendingCoin.name, symbol: trendingCoin.symbol, image: trendingCoin.thumb || trendingCoin.large, current_price: trendingCoin.price_btc, market_cap_rank: trendingCoin.market_cap_rank, price_change_24h: 0 });
  };

  const changeColor = (val) => (val >= 0 ? GREEN : RED);
  const ChangeIcon = ({ positive }) => positive ? <TrendingUp className="h-3.5 w-3.5" style={{ color: GREEN }} /> : <TrendingDown className="h-3.5 w-3.5" style={{ color: RED }} />;

  return (
    <div className="min-h-screen bg-background space-y-6 p-4 sm:p-6 lg:p-8" data-testid="crypto-page">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold uppercase tracking-wide text-foreground">Mercado Crypto</h1>
          <p className="mt-1 text-sm text-muted-foreground">Datos en tiempo real de CoinGecko</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input type="text" placeholder="Buscar monedas..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} data-testid="crypto-search-input" className="evo-input pl-9 py-2.5 rounded-full text-sm" />
          </div>
          <button onClick={() => fetchData(true)} disabled={refreshing} className="evo-button-outline px-4 py-2.5 text-sm rounded-full h-10">
            <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            <span className="ml-1.5 hidden sm:inline">Actualizar</span>
          </button>
        </div>
      </div>

      {/* Trending */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card rounded-xl p-5 overflow-hidden">
        <div className="mb-3 flex items-center gap-2">
          <Activity className="h-4 w-4 text-cyan-400" />
          <span className="evo-section-title">Trending Now</span>
        </div>
        <div className="flex gap-3 overflow-x-auto pb-1">
          {trending.map((coin) => (
            <button key={coin.id} onClick={() => handleTrendingClick(coin)} data-testid={`trending-coin-${coin.id}`}
              className={`flex shrink-0 items-center gap-2 rounded-lg px-4 py-2.5 text-sm transition-all hover:bg-white/5 active:scale-95 ${selectedCoin?.id === coin.id ? "bg-cyan-500/10 ring-1 ring-cyan-500/20" : "border border-white/5"}`}>
              <img src={coin.thumb} alt={coin.name} className="h-6 w-6 rounded-full" loading="lazy" />
              <span className="font-medium text-foreground uppercase">{coin.symbol}</span>
              <span className="text-xs text-muted-foreground">#{coin.market_cap_rank}</span>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Chart Panel */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card rounded-xl p-5 overflow-hidden lg:col-span-2">
          {selectedCoin ? (
            <>
              <div className="mb-5 flex items-center gap-4">
                <img src={selectedCoin.image} alt={selectedCoin.name} className="h-12 w-12 rounded-full" loading="lazy" />
                <div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-lg font-semibold text-foreground">{selectedCoin.name}</span>
                    <span className="text-sm uppercase text-muted-foreground">{selectedCoin.symbol}</span>
                  </div>
                  <div className="flex items-baseline gap-3">
                    <span className="text-2xl font-semibold text-foreground font-mono">{formatPrice(selectedCoin.current_price)}</span>
                    <span className="flex items-center gap-1 text-sm font-medium font-mono" style={{ color: changeColor(selectedCoin.price_change_24h) }}>
                      <ChangeIcon positive={selectedCoin.price_change_24h >= 0} />
                      {selectedCoin.price_change_24h >= 0 ? "+" : ""}{selectedCoin.price_change_24h?.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
              <CoinChart coinId={selectedCoin.id} />
            </>
          ) : (
            <div className="flex h-72 items-center justify-center text-sm text-muted-foreground">Selecciona una moneda para ver el gráfico</div>
          )}
        </motion.div>

        {/* Stats Panel */}
        {selectedCoin && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-card rounded-xl p-5 overflow-hidden">
            <span className="evo-section-title mb-4 block">Market Stats</span>
            <div className="space-y-0">
              {[
                { label: "Market Cap", value: formatNumber(selectedCoin.market_cap) },
                { label: "24h Volume", value: formatNumber(selectedCoin.volume_24h) },
                { label: "Rank", value: `#${selectedCoin.market_cap_rank}` },
                { label: "24h Change", value: `${selectedCoin.price_change_24h >= 0 ? "+" : ""}${selectedCoin.price_change_24h?.toFixed(2)}%`, color: changeColor(selectedCoin.price_change_24h) },
                ...(selectedCoin.price_change_7d ? [{ label: "7d Change", value: `${selectedCoin.price_change_7d >= 0 ? "+" : ""}${selectedCoin.price_change_7d?.toFixed(2)}%`, color: changeColor(selectedCoin.price_change_7d) }] : []),
              ].map((stat, i) => (
                <div key={stat.label} className={`flex items-center justify-between py-3 ${i < 4 ? "border-b border-white/5" : ""}`}>
                  <span className="text-sm text-muted-foreground">{stat.label}</span>
                  <span className="text-sm font-medium tabular-nums font-mono" style={{ color: stat.color || "var(--foreground)" }}>{stat.value}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Coin List */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card rounded-xl p-5 overflow-hidden">
        <div className="mb-4 flex items-center justify-between">
          <span className="evo-section-title">Top Cryptocurrencies</span>
          <span className="text-xs text-muted-foreground">{filteredCoins.length} coins</span>
        </div>
        {/* Header */}
        <div className="mb-2 hidden items-center gap-4 border-b border-white/5 px-4 py-2 text-xs font-medium uppercase tracking-wider text-muted-foreground md:flex">
          <span className="w-6">#</span><span className="w-8" /><span className="flex-1">Name</span>
          <span className="w-28 text-right">Price</span><span className="w-24 text-right">24h</span>
          <span className="hidden w-28 text-right md:block">Market Cap</span><span className="hidden w-28 text-right lg:block">Volume</span>
        </div>
        {/* Rows */}
        <div className="max-h-[500px] space-y-1 overflow-y-auto">
          {loading ? ([...Array(5)].map((_, i) => <div key={i} className="h-16 animate-pulse rounded-lg bg-white/5" />))
            : filteredCoins.length > 0 ? (
              filteredCoins.map((coin) => {
                const positive = coin.price_change_24h >= 0;
                const isSelected = selectedCoin?.id === coin.id;
                return (
                  <div key={coin.id} onClick={() => setSelectedCoin(coin)} data-testid={`coin-row-${coin.id}`}
                    className={`flex cursor-pointer items-center gap-4 rounded-lg px-4 py-3 text-sm transition-all hover:bg-white/[0.03] active:scale-[0.995] md:gap-4 ${isSelected ? "bg-cyan-500/10" : ""}`}>
                    <span className="hidden w-6 text-xs font-medium text-muted-foreground sm:block">{coin.market_cap_rank}</span>
                    <img src={coin.image} alt={coin.name} className="h-8 w-8 flex-shrink-0 rounded-full" loading="lazy" />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="truncate font-medium text-foreground">{coin.name}</span>
                        <span className="shrink-0 text-xs uppercase text-muted-foreground">{coin.symbol}</span>
                      </div>
                    </div>
                    <span className="w-28 shrink-0 text-right font-medium tabular-nums text-foreground font-mono">{formatPrice(coin.current_price)}</span>
                    <span className="flex w-24 shrink-0 items-center justify-end gap-1 text-sm font-medium tabular-nums font-mono" style={{ color: changeColor(coin.price_change_24h) }}>
                      <ChangeIcon positive={positive} />{positive ? "+" : ""}{coin.price_change_24h?.toFixed(2)}%
                    </span>
                    <span className="hidden w-28 shrink-0 text-right text-sm text-muted-foreground md:block">{formatNumber(coin.market_cap)}</span>
                    <span className="hidden w-28 shrink-0 text-right text-sm text-muted-foreground lg:block">{formatNumber(coin.volume_24h)}</span>
                  </div>
                );
              })
            ) : (<div className="py-12 text-center text-sm text-muted-foreground">No coins found</div>)}
        </div>
      </motion.div>
    </div>
  );
}
