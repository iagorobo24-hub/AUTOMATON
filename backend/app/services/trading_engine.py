"""
Trading Engine - Main orchestrator for real-time trading
Connects Binance data, strategies, risk management, and database
"""

import logging
import asyncio
import random
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

from .binance_service import BinanceService
from .regime_detector import RegimeDetector, MarketRegime
from .strategy_alpha import AlphaMomentumRider
from .strategy_beta import BetaRangeScalper
from .strategy_gamma import GammaBreakoutHunter
from .risk_manager import RiskManager
from .database import DatabaseService
from .notifications import NotificationService
from ..models.enums import AgentStatus

logger = logging.getLogger(__name__)


class TradingEngine:
    """
    Main trading engine that:
    1. Fetches real market data from Binance
    2. Detects market regime
    3. Runs appropriate strategy based on regime
    4. Executes trades (paper or real)
    5. Manages risk with circuit breaker
    6. Tracks positions and PnL
    """

    def __init__(
        self,
        db_service: DatabaseService,
        notification_service: NotificationService,
    ):
        self.db_service = db_service
        self.notification_service = notification_service
        self.binance = BinanceService()
        self.regime_detector = RegimeDetector()
        self.risk_manager = RiskManager(db_service)

        self.strategies = {
            "alpha": AlphaMomentumRider(),
            "beta": BetaRangeScalper(),
            "gamma": GammaBreakoutHunter(),
        }

        self.is_running = False
        self.active_positions: Dict[str, Dict] = {}
        self.scan_interval = 60  # Scan every 60 seconds
        self.regime_check_interval = 3600  # Check regime every hour
        self.last_regime_check = None
        self.total_pnl = 0.0
        self.trades_executed = 0
        self.symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
            "BNBUSDT",
            "ADAUSDT",
            "DOTUSDT",
        ]
        self.btc_symbol = "BTCUSDT"
        self.paper_trading = True
        self.kline_cache: Dict[str, List[Dict]] = {}
        self.cache_ttl = 240  # 4 minutes
        self.kline_interval = "1h"  # Use 1h for more data availability on testnet
        self.kline_limit = 200  # Max candles to fetch

    async def start(self):
        """Start the trading engine"""
        self.is_running = True
        self.paper_trading = self.binance.paper_trading
        mode = "PAPER TRADING" if self.paper_trading else "LIVE TRADING"
        logger.info(f"Trading Engine started in {mode} mode")

        # Load persisted risk state FIRST
        await self.risk_manager.load_state()

        agents = await self.db_service.get_agents()
        total_capital = sum(
            a.get("finances", {}).get("current_balance", 0) for a in agents
        )
        # Only set if not already loaded from persistence
        if self.risk_manager._portfolio_start_value <= 0:
            self.risk_manager.set_portfolio_start_value(total_capital)
            logger.info(f"Portfolio start value set: ${total_capital:.2f}")
        else:
            logger.info(f"Portfolio start value restored: ${self.risk_manager._portfolio_start_value:.2f}")

        asyncio.create_task(self._trading_loop())
        asyncio.create_task(self._position_monitor_loop())

        # Background task to save risk state periodically
        asyncio.create_task(self._risk_state_persistence_loop())

    async def stop(self):
        """Stop the trading engine"""
        # Save risk state before stopping
        await self.risk_manager.save_state()
        self.is_running = False
        logger.info("Trading Engine stopped")

    async def _risk_state_persistence_loop(self):
        """Periodically save risk state to DB"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self.risk_manager.save_state()
            except Exception as e:
                logger.error(f"Error saving risk state: {e}")

    async def _trading_loop(self):
        """Main trading loop - scans for opportunities"""
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
            await asyncio.sleep(30)

    async def _scan_for_opportunities(self):
        """Scan all symbols for trading opportunities"""
        agents = await self.db_service.get_agents(status=AgentStatus.ACTIVE)
        if not agents:
            return

        # Check circuit breaker
        total_capital = sum(
            a.get("finances", {}).get("current_balance", 0) for a in agents
        )
        if self.risk_manager.check_circuit_breaker(total_capital):
            logger.warning("Circuit breaker active - skipping scan")
            return

        # Check daily loss
        if self.risk_manager.check_daily_loss(total_capital):
            logger.warning("Daily loss limit reached - skipping scan")
            return

        # Update regime if needed
        now = datetime.now(timezone.utc)
        if (
            self.last_regime_check is None
            or (now - self.last_regime_check).total_seconds()
            > self.regime_check_interval
        ):
            btc_klines = self._get_klines(self.btc_symbol, "4h", 250)
            self.regime_detector.detect(btc_klines, {})
            self.last_regime_check = now
            regime = self.regime_detector.get_status()
            logger.info(f"Market regime: {regime['regime']}")

        # Get recommended strategy
        recommended = self.regime_detector.get_recommended_strategy()
        if recommended == "none":
            logger.info(
                f"Regime: {self.regime_detector.current_regime.value} - No trading recommended"
            )
            return

        position_size_mult = self.regime_detector.get_position_size_multiplier()

        # Count current open positions
        open_positions = len(self.active_positions)
        if not self.risk_manager.can_open_position(open_positions):
            return

        # Scan symbols for opportunities
        for symbol in self.symbols:
            if symbol in self.active_positions:
                continue  # Already have position on this symbol

            klines = self._get_klines(symbol, self.kline_interval, self.kline_limit)
            btc_klines = self._get_klines(
                self.btc_symbol, self.kline_interval, self.kline_limit
            )
            current_price = self.binance.get_price(symbol)

            # Run the recommended strategy
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
            else:
                signal = None

            if signal and signal["position_size"] > 0:
                # Apply position size multiplier from regime
                signal["position_size"] *= position_size_mult
                signal["position_value"] *= position_size_mult

                # Check if we have an agent with enough capital
                for agent in agents:
                    agent_capital = agent.get("finances", {}).get("current_balance", 0)
                    if agent_capital >= signal["risk_usd"] * 2:
                        await self._execute_signal(agent, signal)
                        break

    async def _execute_signal(self, agent: Dict, signal: Dict):
        """Execute a trading signal"""
        agent_id = agent["id"]
        agent_name = agent["name"]
        symbol = signal["symbol"]

        logger.info(
            f"Executing {signal['type']} signal for {agent_name}: "
            f"{symbol} @ ${signal['entry_price']:.2f} "
            f"(Strategy: {signal['strategy']}, Score: {signal['score']})"
        )

        # Create trade record
        trade_result = await self.db_service.simulate_trade(
            agent_id,
            signal.get("risk_usd", 0) * 0.5,  # Simulated initial result
        )

        # Track position
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

        # Notify
        await self.notification_service.notify_trade_result(
            agent_id, agent_name, "paper", symbol, 0, True
        )
        await self.notification_service.notify_opportunity(
            symbol, f"{signal['strategy']} - {signal['type']}", signal["score"] / 10
        )

        self.trades_executed += 1

    async def _monitor_positions(self):
        """Monitor open positions for exit conditions"""
        symbols_to_remove = []

        for symbol, position in self.active_positions.items():
            try:
                klines = self._get_klines(symbol, self.kline_interval, self.kline_limit)
                current_price = self.binance.get_price(symbol)

                # Update highest price for trailing stop
                if current_price > position["highest_price"]:
                    position["highest_price"] = current_price

                # Select the right strategy for exit check
                strategy_name = position.get("strategy", "")
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
                else:
                    exit_signal = None

                if exit_signal:
                    pnl = exit_signal["pnl_percent"]
                    is_win = pnl > 0

                    # Update agent balance
                    agent = await self.db_service.get_agent(position["agent_id"])
                    if agent:
                        capital = agent.get("finances", {}).get("current_balance", 1000)
                        pnl_usd = capital * (pnl / 100)
                        await self.db_service.simulate_trade(
                            position["agent_id"], pnl_usd
                        )

                    logger.info(
                        f"Position closed: {symbol} - {exit_signal['reason']} "
                        f"PnL: {pnl:.2f}%"
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

    def _get_klines(self, symbol: str, interval: str, limit: int) -> List[Dict]:
        """Get klines with caching"""
        cache_key = f"{symbol}_{interval}_{limit}"
        now = datetime.now(timezone.utc)

        if cache_key in self.kline_cache:
            cached_data, cached_time = self.kline_cache[cache_key]
            if (now - cached_time).total_seconds() < self.cache_ttl:
                return cached_data

        klines = self.binance.get_klines(symbol, interval, limit)
        self.kline_cache[cache_key] = (klines, now)
        return klines

    def get_status(self) -> Dict:
        """Get engine status"""
        total_capital = sum(
            p.get("position_size", 0) * p.get("entry_price", 0)
            for p in self.active_positions.values()
        )

        return {
            "is_running": self.is_running,
            "mode": "paper" if self.paper_trading else "live",
            "binance_connected": self.binance.is_connected(),
            "regime": self.regime_detector.get_status(),
            "risk": self.risk_manager.get_status(total_capital),
            "active_positions": len(self.active_positions),
            "positions": list(self.active_positions.values()),
            "total_pnl": self.total_pnl,
            "trades_executed": self.trades_executed,
            "symbols_monitored": self.symbols,
        }
