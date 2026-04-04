import { useState, useEffect, useCallback } from "react";
import {
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Search,
  Activity,
} from "lucide-react";
import axios from "axios";
import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CORAL = "#D97757";
const CORAL_LIGHT = "rgba(217, 119, 87, 0.1)";
const CORAL_BORDER = "rgba(217, 119, 87, 0.25)";
const BG_WARM = "#F5F3EF";
const GREEN = "#2E9E5C";
const RED = "#E04F4F";

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
  { label: "1D", days: 1 },
  { label: "7D", days: 7 },
  { label: "30D", days: 30 },
  { label: "90D", days: 90 },
];

/* ─── Coin Chart ─── */

const CoinChart = ({ coinId }) => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(7);

  useEffect(() => {
    const fetchChart = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API}/crypto/history/${coinId}?days=${days}`);
        const prices = response.data.prices || [];
        const formattedData = prices.map(([timestamp, price]) => ({
          time: new Date(timestamp).toLocaleDateString(),
          price,
        }));
        setChartData(formattedData);
      } catch (error) {
        console.error("Error fetching chart:", error);
      } finally {
        setLoading(false);
      }
    };

    if (coinId) fetchChart();
  }, [coinId, days]);

  if (loading) {
    return (
      <div className="flex h-72 items-center justify-center">
        <RefreshCw className="h-6 w-6 animate-spin" style={{ color: CORAL }} />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex gap-2">
        {PERIODS.map(({ label, days: d }) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className="rounded-full px-4 py-1.5 text-xs font-medium transition-all"
            style={{
              background: days === d ? CORAL : "transparent",
              color: days === d ? "#fff" : "#888",
              border: days === d ? `1px solid ${CORAL}` : "1px solid #e0dcd7",
            }}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="coralGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CORAL} stopOpacity={0.2} />
                <stop offset="95%" stopColor={CORAL} stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="time"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#aaa", fontSize: 11 }}
              interval="preserveStartEnd"
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#aaa", fontSize: 11 }}
              tickFormatter={(v) => `€${v.toLocaleString()}`}
              domain={["auto", "auto"]}
            />
            <Tooltip
              contentStyle={{
                background: "#fff",
                border: `1px solid ${CORAL_BORDER}`,
                borderRadius: "12px",
                fontSize: "12px",
                boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
              }}
              formatter={(value) => [formatPrice(value), "Price"]}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke={CORAL}
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#coralGradient)"
            />
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
        axios.get(`${API}/crypto/top-coins?limit=50`),
        axios.get(`${API}/crypto/trending`),
      ]);

      setCoins(coinsRes.data.coins || []);
      setTrending(trendingRes.data.trending || []);

      if (!selectedCoin && coinsRes.data.coins?.length > 0) {
        setSelectedCoin(coinsRes.data.coins[0]);
      }
    } catch (error) {
      console.error("Error fetching crypto data:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [selectedCoin]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(true), 60000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const filteredCoins = coins.filter(
    (coin) =>
      coin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleTrendingClick = (trendingCoin) => {
    const fullCoin = coins.find((c) => c.id === trendingCoin.id);
    if (fullCoin) {
      setSelectedCoin(fullCoin);
    } else {
      setSelectedCoin({
        id: trendingCoin.id,
        name: trendingCoin.name,
        symbol: trendingCoin.symbol,
        image: trendingCoin.thumb || trendingCoin.large,
        current_price: trendingCoin.price_btc,
        market_cap_rank: trendingCoin.market_cap_rank,
        price_change_24h: 0,
      });
    }
  };

  const changeColor = (val) => (val >= 0 ? GREEN : RED);
  const ChangeIcon = ({ positive }) =>
    positive ? (
      <TrendingUp className="h-3.5 w-3.5" style={{ color: GREEN }} />
    ) : (
      <TrendingDown className="h-3.5 w-3.5" style={{ color: RED }} />
    );

  return (
    <div
      className="min-h-screen space-y-6 p-4 sm:p-6 lg:p-8"
      style={{ backgroundColor: BG_WARM }}
      data-testid="crypto-page"
    >
      {/* ─── Header ─── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
            Mercado Crypto
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time cryptocurrency data from CoinGecko
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search
              className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
            />
            <input
              type="text"
              placeholder="Search coins..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              data-testid="crypto-search-input"
              className="h-10 w-48 rounded-full border border-gray-200 bg-white pl-9 pr-4 text-sm text-gray-900 placeholder-gray-400 outline-none transition-shadow focus:shadow-md focus:ring-0"
            />
          </div>

          <button
            onClick={() => fetchData(true)}
            disabled={refreshing}
            className="flex h-10 items-center gap-2 rounded-full border border-gray-200 bg-white px-4 text-sm font-medium text-gray-700 shadow-sm transition-all hover:shadow-md active:scale-95 disabled:opacity-50"
          >
            <RefreshCw
              className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
            />
            Refresh
          </button>
        </div>
      </div>

      {/* ─── Trending ─── */}
      <div className="overflow-hidden rounded-2xl bg-white p-5 shadow-sm">
        <div className="mb-3 flex items-center gap-2">
          <Activity className="h-4 w-4" style={{ color: CORAL }} />
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Trending Now
          </span>
        </div>
        <div className="flex gap-3 overflow-x-auto pb-1">
          {trending.map((coin) => (
            <button
              key={coin.id}
              onClick={() => handleTrendingClick(coin)}
              data-testid={`trending-coin-${coin.id}`}
              className="flex shrink-0 items-center gap-2 rounded-xl border border-gray-100 bg-gray-50 px-4 py-2.5 text-sm transition-all hover:shadow-md active:scale-95"
              style={{
                borderColor:
                  selectedCoin?.id === coin.id ? CORAL_BORDER : undefined,
                background:
                  selectedCoin?.id === coin.id ? CORAL_LIGHT : undefined,
              }}
            >
              <img
                src={coin.thumb}
                alt={coin.name}
                className="h-6 w-6 rounded-full"
              />
              <span className="font-medium text-gray-900">{coin.symbol}</span>
              <span className="text-xs text-gray-400">
                #{coin.market_cap_rank}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* ─── Main Grid ─── */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Chart Panel */}
        <div
          className="overflow-hidden rounded-2xl bg-white p-5 shadow-sm lg:col-span-2"
        >
          {selectedCoin ? (
            <>
              <div className="mb-5 flex items-center gap-4">
                <img
                  src={selectedCoin.image}
                  alt={selectedCoin.name}
                  className="h-12 w-12 rounded-full"
                />
                <div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-lg font-semibold text-gray-900">
                      {selectedCoin.name}
                    </span>
                    <span className="text-sm uppercase text-gray-400">
                      {selectedCoin.symbol}
                    </span>
                  </div>
                  <div className="flex items-baseline gap-3">
                    <span className="text-2xl font-semibold text-gray-900">
                      {formatPrice(selectedCoin.current_price)}
                    </span>
                    <span
                      className="flex items-center gap-1 text-sm font-medium"
                      style={{ color: changeColor(selectedCoin.price_change_24h) }}
                    >
                      <ChangeIcon positive={selectedCoin.price_change_24h >= 0} />
                      {selectedCoin.price_change_24h >= 0 ? "+" : ""}
                      {selectedCoin.price_change_24h?.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
              <CoinChart coinId={selectedCoin.id} />
            </>
          ) : (
            <div className="flex h-72 items-center justify-center text-sm text-gray-400">
              Select a coin to view the chart
            </div>
          )}
        </div>

        {/* Stats Panel */}
        {selectedCoin && (
          <div className="overflow-hidden rounded-2xl bg-white p-5 shadow-sm">
            <span className="mb-4 block text-xs font-semibold uppercase tracking-wider text-gray-500">
              Market Stats
            </span>
            <div className="space-y-0">
              {[
                { label: "Market Cap", value: formatNumber(selectedCoin.market_cap) },
                { label: "24h Volume", value: formatNumber(selectedCoin.volume_24h) },
                { label: "Rank", value: `#${selectedCoin.market_cap_rank}` },
                {
                  label: "24h Change",
                  value: `${selectedCoin.price_change_24h >= 0 ? "+" : ""}${selectedCoin.price_change_24h?.toFixed(2)}%`,
                  color: changeColor(selectedCoin.price_change_24h),
                },
                ...(selectedCoin.price_change_7d
                  ? [
                      {
                        label: "7d Change",
                        value: `${selectedCoin.price_change_7d >= 0 ? "+" : ""}${selectedCoin.price_change_7d?.toFixed(2)}%`,
                        color: changeColor(selectedCoin.price_change_7d),
                      },
                    ]
                  : []),
              ].map((stat, i) => (
                <div
                  key={stat.label}
                  className={`flex items-center justify-between py-3 ${
                    i < 4 ? "border-b border-gray-100" : ""
                  }`}
                >
                  <span className="text-sm text-gray-500">{stat.label}</span>
                  <span
                    className="text-sm font-medium tabular-nums"
                    style={{ color: stat.color || "#111" }}
                  >
                    {stat.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ─── Coin List ─── */}
      <div className="overflow-hidden rounded-2xl bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Top Cryptocurrencies
          </span>
          <span className="text-xs text-gray-400">
            {filteredCoins.length} coins
          </span>
        </div>

        {/* Table Header */}
        <div className="mb-2 hidden items-center gap-4 border-b border-gray-100 px-4 py-2 text-xs font-medium uppercase tracking-wider text-gray-400 md:flex">
          <span className="w-6">#</span>
          <span className="w-8" />
          <span className="flex-1">Name</span>
          <span className="w-28 text-right">Price</span>
          <span className="w-24 text-right">24h</span>
          <span className="hidden w-28 text-right md:block">Market Cap</span>
          <span className="hidden w-28 text-right lg:block">Volume</span>
        </div>

        {/* Rows */}
        <div className="max-h-[500px] space-y-1 overflow-y-auto">
          {loading ? (
            [...Array(5)].map((_, i) => (
              <div
                key={i}
                className="h-16 animate-pulse rounded-xl bg-gray-100"
              />
            ))
          ) : filteredCoins.length > 0 ? (
            filteredCoins.map((coin) => {
              const positive = coin.price_change_24h >= 0;
              const isSelected = selectedCoin?.id === coin.id;
              return (
                <div
                  key={coin.id}
                  onClick={() => setSelectedCoin(coin)}
                  data-testid={`coin-row-${coin.id}`}
                  className={`flex cursor-pointer items-center gap-4 rounded-xl px-4 py-3 text-sm transition-all hover:bg-gray-50 active:scale-[0.995] md:gap-4`}
                  style={{
                    backgroundColor: isSelected ? CORAL_LIGHT : undefined,
                  }}
                >
                  <span className="hidden w-6 text-xs font-medium text-gray-400 sm:block">
                    {coin.market_cap_rank}
                  </span>

                  <img
                    src={coin.image}
                    alt={coin.name}
                    className="h-8 w-8 flex-shrink-0 rounded-full"
                  />

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="truncate font-medium text-gray-900">
                        {coin.name}
                      </span>
                      <span className="shrink-0 text-xs uppercase text-gray-400">
                        {coin.symbol}
                      </span>
                    </div>
                  </div>

                  <span className="w-28 shrink-0 text-right font-medium tabular-nums text-gray-900">
                    {formatPrice(coin.current_price)}
                  </span>

                  <span
                    className="flex w-24 shrink-0 items-center justify-end gap-1 text-sm font-medium tabular-nums"
                    style={{ color: changeColor(coin.price_change_24h) }}
                  >
                    <ChangeIcon positive={positive} />
                    {positive ? "+" : ""}
                    {coin.price_change_24h?.toFixed(2)}%
                  </span>

                  <span className="hidden w-28 shrink-0 text-right text-sm text-gray-500 md:block">
                    {formatNumber(coin.market_cap)}
                  </span>

                  <span className="hidden w-28 shrink-0 text-right text-sm text-gray-500 lg:block">
                    {formatNumber(coin.volume_24h)}
                  </span>
                </div>
              );
            })
          ) : (
            <div className="py-12 text-center text-sm text-gray-400">
              No coins found
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
