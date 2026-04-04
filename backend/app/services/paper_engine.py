"""
Paper Trading Engine - Real market data, simulated execution
Uses Binance PUBLIC endpoints (no API key needed) for real market data
Executes real strategies with simulated money tracking
"""

import random
import asyncio
import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from .database import DatabaseService
from .notifications import NotificationService
from .strategy_alpha import AlphaMomentumRider
from .strategy_beta import BetaRangeScalper
from .strategy_gamma import GammaBreakoutHunter
from .regime_detector import RegimeDetector, MarketRegime
from .risk_manager import RiskManager
from .replication import ReplicationService
from ..models.enums import AgentStatus

logger = logging.getLogger(__name__)

BINANCE_PUBLIC = "https://api.binance.com/api/v3"


class PaperTradingEngine:
    """
    Paper trading engine that uses REAL market data from Binance public API
    and executes REAL strategies with simulated money.

    No API keys needed - uses public endpoints only.
    """

    def __init__(
        self,
        db_service: DatabaseService,
        notification_service: NotificationService,
    ):
        self.db_service = db_service
        self.notification_service = notification_service

        self.strategies = {
            "alpha": AlphaMomentumRider(),
            "beta": BetaRangeScalper(),
            "gamma": GammaBreakoutHunter(),
        }

        self.regime_detector = RegimeDetector()
        self.risk_manager = RiskManager(db_service)
        self.replication_service = ReplicationService(db_service, notification_service)

        self.is_running = False
        self.scan_interval = 120  # Scan every 2 minutes
        self.regime_check_interval = 3600  # Check regime every hour
        self.last_regime_check = None
        self.replication_check_interval = 600  # Check replication every 10 min
        self.last_replication_check = None

        self.active_positions: Dict[str, Dict] = {}
        self.total_trades = 0
        self.total_pnl = 0.0
        self.winning_trades = 0

        self.symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
            "BNBUSDT",
            "ADAUSDT",
            "DOTUSDT",
        ]
        self.btc_symbol = "BTCUSDT"
        self.kline_cache: Dict[str, tuple] = {}
        self.cache_ttl = 120  # 2 minutes

    async def start(self):
        """Start the paper trading engine"""
        self.is_running = True
        logger.info(
            "Paper Trading Engine started (REAL market data, SIMULATED execution)"
        )

        agents = await self.db_service.get_agents(status=AgentStatus.ACTIVE)
        total_capital = sum(
            a.get("finances", {}).get("current_balance", 0) for a in agents
        )
        self.risk_manager.set_portfolio_start_value(total_capital)
        logger.info(
            f"Portfolio start value: ${total_capital:.2f} ({len(agents)} agents)"
        )

        asyncio.create_task(self._trading_loop())
        asyncio.create_task(self._position_monitor_loop())
        asyncio.create_task(self._replication_loop())

    async def stop(self):
        """Stop the paper trading engine"""
        self.is_running = False
        logger.info("Paper Trading Engine stopped")

    async def _trading_loop(self):
        """Main trading loop - scans for opportunities using real market data"""
        while self.is_running:
            try:
                await self._scan_for_opportunities()
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
            await asyncio.sleep(self.scan_interval)

    async def _position_monitor_loop(self):
        """Monitor open positions for exits"""
        while self.is_running:
            try:
                await self._monitor_positions()
            except Exception as e:
                logger.error(f"Error in position monitor: {e}")
            await asyncio.sleep(60)

    async def _replication_loop(self):
        """Check for agents ready to replicate"""
        while self.is_running:
            try:
                await self._check_replications()
            except Exception as e:
                logger.error(f"Error in replication loop: {e}")
            await asyncio.sleep(self.replication_check_interval)

    async def _scan_for_opportunities(self):
        """Scan all symbols for trading opportunities with REAL market data"""
        agents = await self.db_service.get_agents(status=AgentStatus.ACTIVE)
        if not agents:
            return

        total_capital = sum(
            a.get("finances", {}).get("current_balance", 0) for a in agents
        )

        if self.risk_manager.check_circuit_breaker(total_capital):
            logger.warning("Circuit breaker active - skipping scan")
            return

        if self.risk_manager.check_daily_loss(total_capital):
            logger.warning("Daily loss limit reached - skipping scan")
            return

        now = datetime.now(timezone.utc)
        if (
            self.last_regime_check is None
            or (now - self.last_regime_check).total_seconds()
            > self.regime_check_interval
        ):
            btc_klines = await self._get_klines(self.btc_symbol, "1h", 200)
            if btc_klines:
                self.regime_detector.detect(btc_klines, {})
                self.last_regime_check = now
                regime = self.regime_detector.get_status()
                logger.info(
                    f"Market regime: {regime['regime']} -> {regime['recommended_strategy']}"
                )

        recommended = self.regime_detector.get_recommended_strategy()
        if recommended == "none":
            return

        position_size_mult = self.regime_detector.get_position_size_multiplier()
        open_positions = len(self.active_positions)
        if not self.risk_manager.can_open_position(open_positions):
            return

        for symbol in self.symbols:
            if symbol in self.active_positions:
                continue

            klines = await self._get_klines(symbol, "1h", 200)
            btc_klines = await self._get_klines(self.btc_symbol, "1h", 200)
            if not klines or not btc_klines:
                continue

            current_price = klines[-1]["close"]

            signal = None
            if recommended == "alpha":
                signal = self.strategies["alpha"].evaluate(
                    symbol, klines, btc_klines, current_price, 1000
                )
            elif recommended == "beta":
                signal = self.strategies["beta"].evaluate(
                    symbol, klines, btc_klines, current_price, 1000
                )
            elif recommended == "gamma_watch":
                signal = self.strategies["gamma"].evaluate(
                    symbol, klines, btc_klines, current_price, 1000
                )

            if signal and signal["position_size"] > 0:
                signal["position_size"] *= position_size_mult
                signal["position_value"] *= position_size_mult

                for agent in agents:
                    agent_capital = agent.get("finances", {}).get("current_balance", 0)
                    if agent_capital >= signal["risk_usd"] * 2:
                        await self._execute_signal(agent, signal)
                        break

    async def _execute_signal(self, agent: Dict, signal: Dict):
        """Execute a trading signal - simulated with real market data"""
        agent_id = agent["id"]
        agent_name = agent["name"]
        symbol = signal["symbol"]

        logger.info(
            f"PAPER TRADE: {agent_name} -> {signal['type']} {symbol} @ ${signal['entry_price']:.2f} "
            f"(Strategy: {signal['strategy']}, Score: {signal['score']})"
        )

        position = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "symbol": symbol,
            "type": signal["type"],
            "entry_price": signal["entry_price"],
            "stop_loss": signal["stop_loss"],
            "take_profit": signal.get("take_profit", 0),
            "position_size": signal["position_size"],
            "strategy": signal["strategy"],
            "score": signal["score"],
            "atr": signal.get("atr", 0),
            "highest_price": signal["entry_price"],
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "partial_closed": False,
        }
        self.active_positions[symbol] = position

        await self.notification_service.notify_opportunity(
            symbol, f"{signal['strategy']} - {signal['type']}", signal["score"] / 10
        )

    async def _monitor_positions(self):
        """Monitor open positions for exit conditions using real prices"""
        symbols_to_remove = []

        for symbol, position in self.active_positions.items():
            try:
                klines = await self._get_klines(symbol, "1h", 100)
                if not klines:
                    continue

                current_price = klines[-1]["close"]

                if current_price > position["highest_price"]:
                    position["highest_price"] = current_price

                strategy_name = position.get("strategy", "")
                exit_signal = None
                if "Alpha" in strategy_name:
                    exit_signal = self.strategies["alpha"].check_exit(
                        position, klines, current_price
                    )
                elif "Beta" in strategy_name:
                    exit_signal = self.strategies["beta"].check_exit(
                        position, klines, current_price
                    )
                elif "Gamma" in strategy_name:
                    exit_signal = self.strategies["gamma"].check_exit(
                        position, klines, current_price
                    )

                if exit_signal:
                    pnl = exit_signal["pnl_percent"]
                    is_win = pnl > 0

                    agent = await self.db_service.get_agent(position["agent_id"])
                    if agent:
                        capital = agent.get("finances", {}).get("current_balance", 1000)
                        pnl_usd = capital * (pnl / 100)
                        await self.db_service.simulate_trade(
                            position["agent_id"], pnl_usd
                        )

                    self.total_trades += 1
                    self.total_pnl += pnl_usd
                    if is_win:
                        self.winning_trades += 1

                    logger.info(
                        f"POSITION CLOSED: {symbol} - {exit_signal['reason']} "
                        f"PnL: {pnl:.2f}% (${pnl_usd:+.2f})"
                    )

                    await self.notification_service.notify_trade_result(
                        position["agent_id"],
                        position["agent_name"],
                        "paper",
                        symbol,
                        pnl,
                        is_win,
                    )

                    symbols_to_remove.append(symbol)

            except Exception as e:
                logger.error(f"Error monitoring position {symbol}: {e}")

        for symbol in symbols_to_remove:
            del self.active_positions[symbol]

    async def _check_replications(self):
        """Auto-replicate agents with ROI > 50%"""
        agents = await self.db_service.get_agents(status=AgentStatus.ACTIVE)

        for agent in agents:
            roi = agent.get("performance", {}).get("roi_percent", 0)
            trades = agent.get("trading_stats", {}).get("total_trades", 0)
            balance = agent.get("finances", {}).get("current_balance", 0)

            if roi > 50 and trades >= 20 and balance > 200:
                try:
                    parent = await self.db_service.get_agent(agent["id"])
                    child = await self.db_service.replicate_agent(agent["id"])
                    if child:
                        logger.info(
                            f"AUTO-REPLICATION: {agent['name']} (ROI: {roi:.1f}%, "
                            f"trades: {trades}) -> {child.name}"
                        )
                        await self.notification_service.notify_agent_replicated(
                            agent["name"],
                            child.name,
                            child.id,
                            child.finances.current_balance,
                        )
                except Exception as e:
                    logger.error(f"Replication failed for {agent['name']}: {e}")

    async def _get_klines(
        self, symbol: str, interval: str, limit: int
    ) -> Optional[List[Dict]]:
        """Fetch klines from Binance PUBLIC API (no auth needed)"""
        cache_key = f"{symbol}_{interval}_{limit}"
        now = datetime.now(timezone.utc)

        if cache_key in self.kline_cache:
            cached_data, cached_time = self.kline_cache[cache_key]
            if (now - cached_time).total_seconds() < self.cache_ttl:
                return cached_data

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{BINANCE_PUBLIC}/klines",
                    params={"symbol": symbol, "interval": interval, "limit": limit},
                )
                resp.raise_for_status()
                data = resp.json()

            klines = [
                {
                    "timestamp": datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "close_time": datetime.fromtimestamp(k[6] / 1000, tz=timezone.utc),
                    "quote_volume": float(k[7]),
                    "trades": k[8],
                }
                for k in data
            ]

            self.kline_cache[cache_key] = (klines, now)
            return klines
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return None

    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            "is_running": self.is_running,
            "mode": "paper_trading",
            "data_source": "binance_public",
            "regime": self.regime_detector.get_status(),
            "risk": self.risk_manager.get_status(
                sum(
                    p.get("position_size", 0) * p.get("entry_price", 0)
                    for p in self.active_positions.values()
                )
            ),
            "active_positions": len(self.active_positions),
            "positions": list(self.active_positions.values()),
            "total_trades": self.total_trades,
            "total_pnl": round(self.total_pnl, 2),
            "winning_trades": self.winning_trades,
            "win_rate": round(self.winning_trades / max(self.total_trades, 1) * 100, 1),
            "symbols_monitored": self.symbols,
        }
