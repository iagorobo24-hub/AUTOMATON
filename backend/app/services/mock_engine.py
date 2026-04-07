import random
import asyncio
from datetime import datetime, timezone
from typing import Dict, List
from .database import DatabaseService
from ..models.enums import AgentStatus


class MockEngine:
    """
    Mock trading engine that simulates realistic trading activity.
    Generates profitable trades with positive expected value,
    fluctuating prices, and visible PnL on the dashboard.
    """

    def __init__(self, db_service: DatabaseService, notification_service=None):
        self.db_service = db_service
        self.notification_service = notification_service
        self.assets = ["BTC", "ETH", "SOL", "BNB", "ADA", "DOT"]
        self.base_prices = {
            "BTC": 65000.0,
            "ETH": 3500.0,
            "SOL": 140.0,
            "BNB": 580.0,
            "ADA": 0.45,
            "DOT": 7.2,
        }
        self.current_prices = self.base_prices.copy()
        self.is_running = False
        self.total_trades = 0
        self.total_pnl = 0.0
        self.trade_count_per_cycle = 3
        self._tasks: list[asyncio.Task] = []

    async def start(self):
        """Start the mock engine background tasks"""
        self.is_running = True
        self._tasks.append(asyncio.create_task(self._price_loop()))
        self._tasks.append(asyncio.create_task(self._agent_loop()))

    async def stop(self):
        """Stop all background tasks gracefully"""
        self.is_running = False
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._tasks.clear()

    async def _price_loop(self):
        """Background loop to fluctuate prices realistically"""
        while self.is_running:
            for asset in self.assets:
                # Small random walk: -0.5% to +0.5% per tick
                change = random.uniform(-0.005, 0.005)
                self.current_prices[asset] *= 1 + change

                await self.db_service.update_market_data(
                    f"{asset}/USDT",
                    {
                        "symbol": f"{asset}/USDT",
                        "ticker": {
                            "price": self.current_prices[asset],
                            "change_24h_percent": change * 100,
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        },
                    },
                )

            await asyncio.sleep(3)

    async def _agent_loop(self):
        """
        Background loop to trigger realistic mock trades.
        Win rate ~60%, avg win > avg loss = positive expected value.
        """
        while self.is_running:
            active_agents = await self.db_service.get_agents(status=AgentStatus.ACTIVE)

            for agent in active_agents:
                balance = agent.get("finances", {}).get("current_balance", 0)
                if balance <= 0:
                    continue

                # Each active agent has a trade every 1-2 cycles
                if random.random() < 0.5:
                    # 60% win rate
                    is_win = random.random() < 0.60

                    if is_win:
                        # Win: 2-8% of current balance
                        profit = balance * random.uniform(0.02, 0.08)
                    else:
                        # Loss: 1-4% of current balance (smaller than wins)
                        profit = -balance * random.uniform(0.01, 0.04)

                    profit = round(profit, 2)
                    await self.db_service.simulate_trade(agent["id"], profit)
                    self.total_trades += 1
                    self.total_pnl += profit

                    # Log activity for the trade
                    if self.notification_service:
                        trade_type = "trade_win" if is_win else "trade_loss"
                        await self.notification_service.log_activity(
                            type=trade_type,
                            title=f"Trade {'Ganado' if is_win else 'Perdido'}",
                            description=f"{agent['name']} simuló {'+' if profit >= 0 else ''}€{profit:.2f}",
                            icon="trending-up" if is_win else "trending-down",
                            color="green" if is_win else "red",
                            agent_id=agent["id"],
                            agent_name=agent["name"],
                            amount=profit,
                        )

            await asyncio.sleep(8)

    def get_price(self, symbol: str) -> float:
        asset = symbol.split("/")[0] if "/" in symbol else symbol
        return self.current_prices.get(asset, 100.0)
