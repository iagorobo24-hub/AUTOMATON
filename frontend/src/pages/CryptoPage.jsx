import { useState, useEffect } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  RefreshCw,
  Search,
  Star,
  ExternalLink,
  BarChart2,
  Activity
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const formatNumber = (num) => {
  if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
  if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
  if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
  if (num >= 1e3) return `$${(num / 1e3).toFixed(2)}K`;
  return `$${num?.toFixed(2) || 0}`;
};

const CoinRow = ({ coin, onSelect, isSelected }) => {
  const isPositive = coin.price_change_24h >= 0;
  
  return (
    <div 
      className={cn(
        "flex items-center gap-4 p-4 rounded-sm border border-white/10 cursor-pointer",
        "transition-colors hover:bg-white/5",
        isSelected && "bg-primary/10 border-primary/30"
      )}
      onClick={() => onSelect(coin)}
      data-testid={`coin-row-${coin.id}`}
    >
      <span className="text-xs text-muted-foreground w-6 font-mono">
        {coin.market_cap_rank}
      </span>
      
      <img 
        src={coin.image} 
        alt={coin.name} 
        className="w-8 h-8 rounded-full"
      />
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-semibold">{coin.name}</span>
          <span className="text-xs text-muted-foreground uppercase">{coin.symbol}</span>
        </div>
      </div>
      
      <div className="text-right">
        <p className="font-mono font-semibold">
          ${coin.current_price?.toLocaleString(undefined, { maximumFractionDigits: 6 })}
        </p>
      </div>
      
      <div className={cn(
        "w-24 text-right font-mono text-sm",
        isPositive ? "text-cyber-green" : "text-destructive"
      )}>
        <div className="flex items-center justify-end gap-1">
          {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          {isPositive ? "+" : ""}{coin.price_change_24h?.toFixed(2)}%
        </div>
      </div>
      
      <div className="hidden md:block text-right w-28">
        <p className="text-sm text-muted-foreground">{formatNumber(coin.market_cap)}</p>
      </div>
      
      <div className="hidden lg:block text-right w-28">
        <p className="text-sm text-muted-foreground">{formatNumber(coin.volume_24h)}</p>
      </div>
    </div>
  );
};

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
          price: price
        }));
        setChartData(formattedData);
      } catch (error) {
        console.error("Error fetching chart:", error);
      } finally {
        setLoading(false);
      }
    };

    if (coinId) {
      fetchChart();
    }
  }, [coinId, days]);

  if (loading) {
    return (
      <div className="h-[300px] flex items-center justify-center">
        <RefreshCw className="w-6 h-6 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex gap-2 mb-4">
        {[1, 7, 30, 90].map((d) => (
          <Button
            key={d}
            variant={days === d ? "default" : "outline"}
            size="sm"
            onClick={() => setDays(d)}
            className={cn(
              "text-xs",
              days === d ? "bg-primary text-black" : "border-white/20"
            )}
          >
            {d}D
          </Button>
        ))}
      </div>
      
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00F3FF" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#00F3FF" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="time" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#666', fontSize: 10 }}
              interval="preserveStartEnd"
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#666', fontSize: 10 }}
              tickFormatter={(v) => `$${v.toLocaleString()}`}
              domain={['auto', 'auto']}
            />
            <Tooltip
              contentStyle={{
                background: 'rgba(0,0,0,0.9)',
                border: '1px solid rgba(0,243,255,0.3)',
                borderRadius: '4px',
                fontSize: '12px'
              }}
              formatter={(value) => [`$${value.toLocaleString()}`, 'Price']}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#00F3FF"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorPrice)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default function CryptoPage() {
  const [coins, setCoins] = useState([]);
  const [trending, setTrending] = useState([]);
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const [coinsRes, trendingRes] = await Promise.all([
        axios.get(`${API}/crypto/top-coins?limit=20`),
        axios.get(`${API}/crypto/trending`)
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
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  const filteredCoins = coins.filter(coin => 
    coin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    coin.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6" data-testid="crypto-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl tracking-wide uppercase">
            Crypto Market
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time cryptocurrency data from CoinGecko
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search coins..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-black/50 border-white/10 w-48"
              data-testid="crypto-search-input"
            />
          </div>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={fetchData}
            className="border-white/20"
          >
            <RefreshCw className={cn("w-4 h-4 mr-2", loading && "animate-spin")} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Trending */}
      <Card className="glass border-white/10">
        <CardHeader className="pb-2">
          <CardTitle className="font-heading text-sm tracking-wider uppercase text-muted-foreground flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary" />
            Trending Now
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3 overflow-x-auto pb-2">
            {trending.map((coin) => (
              <div
                key={coin.id}
                className="flex items-center gap-2 px-4 py-2 rounded-sm bg-white/5 border border-white/10 hover:border-primary/30 cursor-pointer transition-colors shrink-0"
              >
                <img src={coin.thumb} alt={coin.name} className="w-6 h-6 rounded-full" />
                <span className="font-mono text-sm">{coin.symbol}</span>
                <span className="text-xs text-muted-foreground">#{coin.market_cap_rank}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart */}
        <Card className="glass border-white/10 lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-sm tracking-wider uppercase text-muted-foreground flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-primary" />
              {selectedCoin ? `${selectedCoin.name} (${selectedCoin.symbol.toUpperCase()})` : 'Price Chart'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedCoin ? (
              <>
                <div className="flex items-center gap-4 mb-6">
                  <img src={selectedCoin.image} alt={selectedCoin.name} className="w-10 h-10 rounded-full" />
                  <div>
                    <p className="font-mono text-2xl font-bold">
                      ${selectedCoin.current_price?.toLocaleString(undefined, { maximumFractionDigits: 6 })}
                    </p>
                    <p className={cn(
                      "text-sm font-mono",
                      selectedCoin.price_change_24h >= 0 ? "text-cyber-green" : "text-destructive"
                    )}>
                      {selectedCoin.price_change_24h >= 0 ? "+" : ""}
                      {selectedCoin.price_change_24h?.toFixed(2)}% (24h)
                    </p>
                  </div>
                </div>
                <CoinChart coinId={selectedCoin.id} />
              </>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                Select a coin to view chart
              </div>
            )}
          </CardContent>
        </Card>

        {/* Coin Stats */}
        {selectedCoin && (
          <Card className="glass border-white/10">
            <CardHeader className="pb-2">
              <CardTitle className="font-heading text-sm tracking-wider uppercase text-muted-foreground">
                Market Stats
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-sm text-muted-foreground">Market Cap</span>
                <span className="font-mono">{formatNumber(selectedCoin.market_cap)}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-sm text-muted-foreground">24h Volume</span>
                <span className="font-mono">{formatNumber(selectedCoin.volume_24h)}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-sm text-muted-foreground">Rank</span>
                <span className="font-mono">#{selectedCoin.market_cap_rank}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-sm text-muted-foreground">24h Change</span>
                <span className={cn(
                  "font-mono",
                  selectedCoin.price_change_24h >= 0 ? "text-cyber-green" : "text-destructive"
                )}>
                  {selectedCoin.price_change_24h >= 0 ? "+" : ""}
                  {selectedCoin.price_change_24h?.toFixed(2)}%
                </span>
              </div>
              {selectedCoin.price_change_7d && (
                <div className="flex justify-between items-center py-2">
                  <span className="text-sm text-muted-foreground">7d Change</span>
                  <span className={cn(
                    "font-mono",
                    selectedCoin.price_change_7d >= 0 ? "text-cyber-green" : "text-destructive"
                  )}>
                    {selectedCoin.price_change_7d >= 0 ? "+" : ""}
                    {selectedCoin.price_change_7d?.toFixed(2)}%
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Coin List */}
      <Card className="glass border-white/10">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="font-heading text-sm tracking-wider uppercase text-muted-foreground">
              Top Cryptocurrencies
            </CardTitle>
            <span className="text-xs text-muted-foreground">
              {filteredCoins.length} coins
            </span>
          </div>
        </CardHeader>
        <CardContent>
          {/* Table Header */}
          <div className="hidden md:flex items-center gap-4 px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider border-b border-white/10 mb-2">
            <span className="w-6">#</span>
            <span className="w-8"></span>
            <span className="flex-1">Name</span>
            <span className="w-24 text-right">Price</span>
            <span className="w-24 text-right">24h</span>
            <span className="hidden md:block w-28 text-right">Market Cap</span>
            <span className="hidden lg:block w-28 text-right">Volume</span>
          </div>
          
          {/* Coins */}
          <div className="space-y-2 max-h-[500px] overflow-y-auto">
            {loading ? (
              [...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-white/5 rounded-sm animate-pulse" />
              ))
            ) : filteredCoins.length > 0 ? (
              filteredCoins.map((coin) => (
                <CoinRow 
                  key={coin.id} 
                  coin={coin} 
                  onSelect={setSelectedCoin}
                  isSelected={selectedCoin?.id === coin.id}
                />
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No coins found
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
