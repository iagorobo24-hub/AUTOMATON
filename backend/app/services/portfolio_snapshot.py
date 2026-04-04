"""
Portfolio Snapshot Service - Background worker for periodic portfolio snapshots
Tracks portfolio value over time for charting and analysis
"""

import logging
import asyncio
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class PortfolioSnapshotService:
    """
    Background worker that takes periodic snapshots of:
    - Total portfolio value
    - Per-agent balances
    - Active positions
    - PnL metrics
    Stores snapshots in MongoDB for historical charting
    """

    def __init__(self, db_service):
        self.db_service = db_service
        self.is_running = False
        self.snapshot_interval = 900  # 15 minutes
        self.collection = db_service.db.portfolio_snapshots

    async def start(self):
        """Start the snapshot worker"""
        self.is_running = True
        asyncio.create_task(self._snapshot_loop())
        logger.info(
            f"Portfolio Snapshot Service started (interval: {self.snapshot_interval}s)"
        )

    async def stop(self):
        """Stop the snapshot worker"""
        self.is_running = False
        logger.info("Portfolio Snapshot Service stopped")

    async def _snapshot_loop(self):
        """Main snapshot loop"""
        while self.is_running:
            try:
                await self._take_snapshot()
            except Exception as e:
                logger.error(f"Error taking portfolio snapshot: {e}")
            await asyncio.sleep(self.snapshot_interval)

    async def _take_snapshot(self):
        """Take a single portfolio snapshot"""
        agents = await self.db_service.get_agents()
        total_value = sum(
            a.get("finances", {}).get("current_balance", 0) for a in agents
        )
        total_initial = sum(
            a.get("finances", {}).get("initial_capital", 0) for a in agents
        )

        # Get recent trades
        trades = await self.db_service.get_all_trades(limit=100)
        recent_pnl = sum(t.get("result", {}).get("pnl_usd", 0) for t in trades)

        # Per-agent breakdown
        agent_breakdown = []
        for agent in agents:
            agent_breakdown.append(
                {
                    "agent_id": agent.get("id"),
                    "name": agent.get("name"),
                    "balance": agent.get("finances", {}).get("current_balance", 0),
                    "roi": agent.get("performance", {}).get("roi_percent", 0),
                    "status": agent.get("status"),
                    "trades": agent.get("trading_stats", {}).get("total_trades", 0),
                    "win_rate": agent.get("performance", {}).get("win_rate", 0),
                }
            )

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_value": total_value,
            "total_initial": total_initial,
            "total_pnl": total_value - total_initial,
            "total_pnl_percent": ((total_value - total_initial) / total_initial * 100)
            if total_initial > 0
            else 0,
            "active_agents": len([a for a in agents if a.get("status") == "active"]),
            "total_agents": len(agents),
            "total_trades": len(trades),
            "recent_pnl": recent_pnl,
            "agent_breakdown": agent_breakdown,
        }

        await self.collection.insert_one(snapshot)
        logger.debug(f"Portfolio snapshot: ${total_value:.2f} ({len(agents)} agents)")

    async def get_history(self, period: str = "7d") -> Dict:
        """Get portfolio history for a given period"""
        now = datetime.now(timezone.utc)
        periods = {
            "1d": now - timedelta(days=1),
            "7d": now - timedelta(days=7),
            "1m": now - timedelta(days=30),
            "3m": now - timedelta(days=90),
            "all": now - timedelta(days=365),
        }
        start = periods.get(period, periods["7d"])

        snapshots = (
            await self.collection.find(
                {"timestamp": {"$gte": start.isoformat()}}, {"_id": 0}
            )
            .sort("timestamp", 1)
            .to_list(10000)
        )

        history = []
        for snap in snapshots:
            history.append(
                {
                    "timestamp": snap["timestamp"],
                    "value": snap["total_value"],
                    "pnl": snap["total_pnl"],
                    "pnl_percent": snap["total_pnl_percent"],
                }
            )

        return {
            "period": period,
            "snapshots": len(history),
            "history": history,
        }
