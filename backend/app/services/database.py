"""
Automaton Orchestrator - Database Service
Handles all database operations with the modular schema
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import hashlib
import json

from ..models.enums import AgentStatus, AgentType, TradeSide, TradeStatus
from ..models.agent import (
    Agent,
    Lineage,
    Lifecycle,
    AgentFinances,
    Performance,
    TradingStats,
    AgentConfig,
    ReplicationRules,
    DeathRules,
    AgentMetadata,
)
from ..models.trading import (
    Strategy,
    Trade,
    TradeEntry,
    TradeResult,
    Position,
    Signal,
    RiskManagement,
)
from ..models.finance import Wallet, AssetBalance, RiskProfile
from ..models.system import (
    AgentLineage,
    LineageTreeNode,
    LineageStats,
    AuditLog,
    AuditActor,
    AuditTarget,
    OrchestratorState,
)
from ..models.requests import (
    AgentCreateRequest,
    AgentReplicateRequest,
    TradeCreateRequest,
)


class DatabaseService:
    """Service for all database operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

        # Collections
        self.agents = db.agents
        self.strategies = db.strategies
        self.trades = db.trades
        self.positions = db.positions
        self.wallets = db.wallets
        self.risk_profiles = db.risk_profiles
        self.signals = db.signals
        self.market_data = db.market_data
        self.agent_lineages = db.agent_lineages
        self.audit_logs = db.audit_logs
        self.orchestrator_state = db.orchestrator_state
        self.clone_configs = db.clone_configs

    # ==================== HELPERS ====================

    def _serialize_datetime(self, obj: Any) -> Any:
        """Recursively serialize datetime objects to ISO strings"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        return obj

    def _generate_audit_hash(self, data: Dict) -> str:
        """Generate hash for audit log integrity"""
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    async def _log_audit(
        self,
        event_type: str,
        event_category: str,
        actor_type: str,
        actor_id: str,
        actor_name: str,
        details: Dict = None,
        target_type: str = None,
        target_id: str = None,
        target_name: str = None,
        result: str = "success",
        error_message: str = None,
    ):
        """Create an audit log entry"""
        log = AuditLog(
            event_type=event_type,
            event_category=event_category,
            actor=AuditActor(type=actor_type, id=actor_id, name=actor_name),
            target=AuditTarget(type=target_type, id=target_id, name=target_name)
            if target_id
            else None,
            details=details or {},
            result=result,
            error_message=error_message,
        )

        doc = self._serialize_datetime(log.model_dump())
        doc["hash"] = self._generate_audit_hash(doc)
        await self.audit_logs.insert_one(doc)

    # ==================== AGENTS ====================

    async def create_agent(
        self, request: AgentCreateRequest, created_by: str = "user"
    ) -> Agent:
        """Create a new agent with full schema"""

        agent = Agent(
            name=request.name,
            display_name=request.name,
            agent_type=request.agent_type,
            specialization=request.specialization,
            generation=1,
            lineage=Lineage(root_ancestor_id=None),
            finances=AgentFinances(
                initial_capital=request.initial_capital,
                current_balance=request.initial_capital,
                available_balance=request.initial_capital,
            ),
            config=AgentConfig(
                strategy_id=request.strategy_id,
                risk_profile_id=request.risk_profile_id,
                allowed_pairs=[f"{s}/USDT" for s in request.specialization],
            ),
            metadata=AgentMetadata(
                created_by=created_by, tags=[request.agent_type.value]
            ),
        )

        agent.lineage.root_ancestor_id = agent.id

        if request.parent_id:
            parent = await self.get_agent(request.parent_id)
            if parent:
                agent.lineage.parent_id = request.parent_id
                agent.lineage.root_ancestor_id = parent.get("lineage", {}).get(
                    "root_ancestor_id", request.parent_id
                )
                agent.generation = parent.get("generation", 1) + 1
                agent.lineage.generation_depth = agent.generation - 1

        doc = self._serialize_datetime(agent.model_dump())
        await self.agents.insert_one(doc)

        await self.create_wallet(agent.id, request.initial_capital)

        await self._log_audit(
            event_type="agent_created",
            event_category="lifecycle",
            actor_type="user" if created_by == "user" else "agent",
            actor_id=created_by,
            actor_name=created_by,
            target_type="agent",
            target_id=agent.id,
            target_name=agent.name,
            details={
                "initial_capital": request.initial_capital,
                "agent_type": request.agent_type.value,
                "parent_id": request.parent_id,
            },
        )

        return agent

    async def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID"""
        return await self.agents.find_one({"id": agent_id}, {"_id": 0})

    async def get_agents(
        self, status: Optional[AgentStatus] = None, limit: int = 100
    ) -> List[Dict]:
        """Get all agents with optional status filter"""
        query = {}
        if status:
            query["status"] = status.value
        return await self.agents.find(query, {"_id": 0}).to_list(limit)

    async def update_agent(self, agent_id: str, updates: Dict) -> bool:
        """Update agent fields"""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = await self.agents.update_one(
            {"id": agent_id}, {"$set": self._serialize_datetime(updates)}
        )
        return result.modified_count > 0

    async def replicate_agent(
        self, agent_id: str, request: AgentReplicateRequest
    ) -> Optional[Agent]:
        """Replicate an agent (create child)"""
        parent = await self.get_agent(agent_id)
        if not parent:
            return None

        parent_balance = parent.get("finances", {}).get("current_balance", 0)
        min_balance_for_replication = (
            parent.get("replication_rules", {}).get("min_balance_usd", 50) * 2
        )

        if parent_balance < min_balance_for_replication:
            raise ValueError(
                f"Insufficient balance for replication. Need at least {min_balance_for_replication}"
            )

        child_capital = parent_balance * request.capital_split_ratio
        parent_new_balance = parent_balance - child_capital

        children_count = len(parent.get("lineage", {}).get("children_ids", []))
        child_name = (
            request.custom_name or f"{parent['name']}_child_{children_count + 1}"
        )

        child_request = AgentCreateRequest(
            name=child_name,
            agent_type=AgentType(parent.get("agent_type", "crypto_trader")),
            initial_capital=child_capital,
            specialization=parent.get("specialization", ["BTC", "ETH"]),
            strategy_id=parent.get("config", {}).get("strategy_id"),
            risk_profile_id=parent.get("config", {}).get("risk_profile_id"),
            parent_id=agent_id,
        )

        child = await self.create_agent(child_request, created_by=agent_id)

        await self.agents.update_one(
            {"id": agent_id},
            {
                "$set": {
                    "finances.current_balance": parent_new_balance,
                    "finances.available_balance": parent_new_balance,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                "$push": {"lineage.children_ids": child.id},
                "$inc": {"lineage.clone_count": 1, "lineage.total_descendants": 1},
            },
        )

        await self._log_audit(
            event_type="agent_replicated",
            event_category="lifecycle",
            actor_type="agent",
            actor_id=agent_id,
            actor_name=parent["name"],
            target_type="agent",
            target_id=child.id,
            target_name=child.name,
            details={
                "parent_balance_before": parent_balance,
                "parent_balance_after": parent_new_balance,
                "child_capital": child_capital,
                "capital_split_ratio": request.capital_split_ratio,
                "generation": child.generation,
            },
        )

        return child

    async def update_agent_status(
        self, agent_id: str, status: AgentStatus, reason: str = None
    ):
        """Update agent status with lifecycle tracking"""
        updates = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if status == AgentStatus.DEAD:
            updates["lifecycle.death_at"] = datetime.now(timezone.utc).isoformat()
            updates["lifecycle.death_reason"] = reason
            updates["finances.current_balance"] = 0
            updates["finances.available_balance"] = 0
        elif status == AgentStatus.ACTIVE:
            updates["lifecycle.last_active_at"] = datetime.now(timezone.utc).isoformat()

        await self.agents.update_one({"id": agent_id}, {"$set": updates})

        agent = await self.get_agent(agent_id)
        await self._log_audit(
            event_type=f"agent_{status.value}",
            event_category="lifecycle",
            actor_type="orchestrator",
            actor_id="orchestrator",
            actor_name="Orchestrator",
            target_type="agent",
            target_id=agent_id,
            target_name=agent.get("name", "Unknown") if agent else "Unknown",
            details={"reason": reason},
        )

    async def simulate_trade(self, agent_id: str, profit: float) -> Dict:
        """Simulate a trade for an agent and update stats"""
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError("Agent not found")

        finances = agent.get("finances", {})
        stats = agent.get("trading_stats", {})
        current_balance = finances.get("current_balance", 0)
        initial_capital = finances.get("initial_capital", 100)

        new_balance = current_balance + profit
        new_trades = stats.get("total_trades", 0) + 1
        is_winner = profit > 0

        new_wins = stats.get("winning_trades", 0) + (1 if is_winner else 0)
        new_losses = stats.get("losing_trades", 0) + (0 if is_winner else 1)
        roi = (
            ((new_balance - initial_capital) / initial_capital) * 100
            if initial_capital > 0
            else 0
        )

        death_rules = agent.get("death_rules", {})
        replication_rules = agent.get("replication_rules", {})

        new_status = agent.get("status", "active")
        status_reason = None

        if new_balance <= death_rules.get("min_balance_usd", 1):
            new_status = AgentStatus.DEAD.value
            status_reason = "bankruptcy"
        elif new_balance <= initial_capital * 0.2:
            new_status = AgentStatus.DYING.value
            status_reason = "low_balance"
        elif roi >= replication_rules.get(
            "min_roi_to_replicate", 50
        ) and new_trades >= replication_rules.get("min_trades_to_replicate", 100):
            new_status = AgentStatus.REPLICATING.value
        else:
            new_status = AgentStatus.ACTIVE.value

        win_rate = new_wins / new_trades if new_trades > 0 else 0
        current_streak = stats.get("current_streak", 0)
        streak_type = stats.get("streak_type", "none")

        if is_winner:
            current_streak = current_streak + 1 if streak_type == "win" else 1
            streak_type = "win"
        else:
            current_streak = current_streak - 1 if streak_type == "loss" else -1
            streak_type = "loss"

        updates = {
            "finances.current_balance": max(0, new_balance),
            "finances.available_balance": max(0, new_balance),
            "trading_stats.total_trades": new_trades,
            "trading_stats.winning_trades": new_wins,
            "trading_stats.losing_trades": new_losses,
            "trading_stats.current_streak": current_streak,
            "trading_stats.streak_type": streak_type,
            "performance.roi_percent": roi,
            "performance.win_rate": win_rate,
            "status": new_status,
            "lifecycle.last_active_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if is_winner and profit > stats.get("largest_win", 0):
            updates["trading_stats.largest_win"] = profit
        elif not is_winner and profit < stats.get("largest_loss", 0):
            updates["trading_stats.largest_loss"] = profit

        if is_winner and current_streak > stats.get("consecutive_wins_max", 0):
            updates["trading_stats.consecutive_wins_max"] = current_streak
        elif not is_winner and abs(current_streak) > stats.get(
            "consecutive_losses_max", 0
        ):
            updates["trading_stats.consecutive_losses_max"] = abs(current_streak)

        if new_status == AgentStatus.DEAD.value:
            updates["lifecycle.death_at"] = datetime.now(timezone.utc).isoformat()
            updates["lifecycle.death_reason"] = status_reason

        await self.agents.update_one({"id": agent_id}, {"$set": updates})

        trade = Trade(
            agent_id=agent_id,
            symbol="BTC/USDT",
            base_asset="BTC",
            quote_asset="USDT",
            side=TradeSide.LONG if profit > 0 else TradeSide.SHORT,
            entry=TradeEntry(
                price=42000, quantity=abs(profit) / 42000, value_usd=abs(profit)
            ),
            result=TradeResult(
                pnl_usd=profit,
                pnl_percent=(profit / current_balance * 100)
                if current_balance > 0
                else 0,
                net_pnl_usd=profit,
                is_winner=is_winner,
            ),
            status=TradeStatus.CLOSED,
        )
        await self.trades.insert_one(self._serialize_datetime(trade.model_dump()))

        return {
            "agent_id": agent_id,
            "trade_id": trade.id,
            "profit": profit,
            "new_balance": max(0, new_balance),
            "roi": roi,
            "status": new_status,
            "is_winner": is_winner,
            "total_trades": new_trades,
            "win_rate": win_rate,
        }

    # ==================== WALLETS ====================

    async def create_wallet(self, agent_id: str, initial_balance: float = 0) -> Wallet:
        """Create a wallet for an agent"""
        wallet = Wallet(
            agent_id=agent_id,
            balances={
                "USDT": AssetBalance(
                    total=initial_balance,
                    available=initial_balance,
                    value_usd=initial_balance,
                )
            },
            total_value_usd=initial_balance,
        )
        await self.wallets.insert_one(self._serialize_datetime(wallet.model_dump()))
        return wallet

    async def get_wallet(self, agent_id: str) -> Optional[Dict]:
        """Get wallet for an agent"""
        return await self.wallets.find_one({"agent_id": agent_id}, {"_id": 0})

    # ==================== TRADES ====================

    async def create_trade(self, request: TradeCreateRequest) -> Trade:
        """Create a new trade"""
        trade = Trade(
            agent_id=request.agent_id,
            symbol=request.symbol,
            base_asset=request.symbol.split("/")[0],
            quote_asset=request.symbol.split("/")[1]
            if "/" in request.symbol
            else "USDT",
            side=request.side,
            strategy_id=request.strategy_id,
            entry=TradeEntry(
                price=request.entry_price,
                quantity=request.quantity,
                value_usd=request.entry_price * request.quantity,
            ),
            risk_management=RiskManagement(
                initial_stop_loss=request.stop_loss or 0,
                initial_take_profit=request.take_profit or 0,
                position_size_percent=5.0,
            ),
            status=TradeStatus.OPEN,
        )
        await self.trades.insert_one(self._serialize_datetime(trade.model_dump()))
        return trade

    async def get_trades(self, agent_id: str, limit: int = 100) -> List[Dict]:
        """Get trades for an agent"""
        return (
            await self.trades.find({"agent_id": agent_id}, {"_id": 0})
            .sort("created_at", -1)
            .to_list(limit)
        )

    async def get_all_trades(self, limit: int = 100) -> List[Dict]:
        """Get all trades across agents"""
        return (
            await self.trades.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
        )

    # ==================== STRATEGIES ====================

    async def create_strategy(
        self, name: str, description: str = "", **kwargs
    ) -> Strategy:
        """Create a new trading strategy"""
        strategy = Strategy(name=name, description=description, **kwargs)
        await self.strategies.insert_one(
            self._serialize_datetime(strategy.model_dump())
        )
        return strategy

    async def get_strategies(self, limit: int = 100) -> List[Dict]:
        """Get all strategies"""
        return await self.strategies.find({}, {"_id": 0}).to_list(limit)

    async def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        """Get strategy by ID"""
        return await self.strategies.find_one({"id": strategy_id}, {"_id": 0})

    # ==================== RISK PROFILES ====================

    async def create_risk_profile(
        self, name: str, description: str = "", **kwargs
    ) -> RiskProfile:
        """Create a new risk profile"""
        profile = RiskProfile(name=name, description=description, **kwargs)
        await self.risk_profiles.insert_one(
            self._serialize_datetime(profile.model_dump())
        )
        return profile

    async def get_risk_profiles(self) -> List[Dict]:
        """Get all risk profiles"""
        return await self.risk_profiles.find({}, {"_id": 0}).to_list(100)

    # ==================== SIGNALS ====================

    async def get_active_signals(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get active trading signals"""
        query = {"status": "active"}
        if symbol:
            query["symbol"] = symbol
        return await self.signals.find(query, {"_id": 0}).to_list(100)

    # ==================== MARKET DATA ====================

    async def update_market_data(self, symbol: str, data: Dict):
        """Update or insert market data"""
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.market_data.update_one(
            {"symbol": symbol}, {"$set": data}, upsert=True
        )

    async def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get market data for a symbol"""
        return await self.market_data.find_one({"symbol": symbol}, {"_id": 0})

    # ==================== ORCHESTRATOR ====================

    async def get_orchestrator_state(self) -> Dict:
        """Get or create orchestrator state"""
        state = await self.orchestrator_state.find_one(
            {"orchestrator_id": "main"}, {"_id": 0}
        )
        if not state:
            default_state = OrchestratorState()
            doc = self._serialize_datetime(default_state.model_dump())
            await self.orchestrator_state.insert_one(doc)
            return doc
        return state

    async def update_orchestrator_metrics(self):
        """Update global orchestrator metrics"""
        agents = await self.get_agents()
        active = len([a for a in agents if a.get("status") == "active"])
        total_capital = sum(
            a.get("finances", {}).get("current_balance", 0) for a in agents
        )

        await self.orchestrator_state.update_one(
            {"orchestrator_id": "main"},
            {
                "$set": {
                    "global_metrics.total_agents": len(agents),
                    "global_metrics.active_agents": active,
                    "global_metrics.total_capital_managed": total_capital,
                    "last_health_check": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            upsert=True,
        )

    # ==================== LINEAGE ====================

    async def get_agent_lineage(self, root_agent_id: str) -> Optional[Dict]:
        """Get lineage tree for an agent family"""
        return await self.agent_lineages.find_one(
            {"root_agent_id": root_agent_id}, {"_id": 0}
        )

    async def rebuild_lineage_tree(self, root_agent_id: str):
        """Rebuild the lineage tree for a root agent"""
        root = await self.get_agent(root_agent_id)
        if not root:
            return

        async def build_tree(agent_id: str) -> Dict:
            agent = await self.get_agent(agent_id)
            if not agent:
                return None
            children = []
            for child_id in agent.get("lineage", {}).get("children_ids", []):
                child_tree = await build_tree(child_id)
                if child_tree:
                    children.append(child_tree)
            return {
                "agent_id": agent["id"],
                "name": agent["name"],
                "generation": agent.get("generation", 1),
                "created_at": agent.get("created_at"),
                "status": agent.get("status", "active"),
                "roi": agent.get("performance", {}).get("roi_percent", 0),
                "death_reason": agent.get("lifecycle", {}).get("death_reason"),
                "children": children,
            }

        tree = await build_tree(root_agent_id)
        all_agents = await self.agents.find(
            {"lineage.root_ancestor_id": root_agent_id}, {"_id": 0}
        ).to_list(1000)
        stats = {
            "total_agents": len(all_agents),
            "active_agents": len(
                [a for a in all_agents if a.get("status") == "active"]
            ),
            "dead_agents": len([a for a in all_agents if a.get("status") == "dead"]),
            "replicating_agents": len(
                [a for a in all_agents if a.get("status") == "replicating"]
            ),
            "max_generation": max(
                (a.get("generation", 1) for a in all_agents), default=1
            ),
            "total_capital_managed": sum(
                a.get("finances", {}).get("current_balance", 0) for a in all_agents
            ),
            "survival_rate": len([a for a in all_agents if a.get("status") != "dead"])
            / len(all_agents)
            if all_agents
            else 0,
        }

        lineage_doc = {
            "lineage_id": str(uuid.uuid4()),
            "root_agent_id": root_agent_id,
            "root_agent_name": root["name"],
            "tree": tree,
            "stats": stats,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.agent_lineages.update_one(
            {"root_agent_id": root_agent_id}, {"$set": lineage_doc}, upsert=True
        )

    # ==================== AUDIT LOGS ====================

    async def get_audit_logs(
        self,
        agent_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get audit logs with optional filters"""
        query = {}
        if agent_id:
            query["$or"] = [{"actor.id": agent_id}, {"target.id": agent_id}]
        if event_type:
            query["event_type"] = event_type
        return (
            await self.audit_logs.find(query, {"_id": 0})
            .sort("created_at", -1)
            .to_list(limit)
        )

    # ==================== DASHBOARD STATS ====================

    async def get_dashboard_stats(self) -> Dict:
        """Get comprehensive dashboard statistics"""
        agents = await self.get_agents()
        trades = await self.get_all_trades(limit=1000)
        active = [a for a in agents if a.get("status") == "active"]
        total_balance = sum(
            a.get("finances", {}).get("current_balance", 0) for a in agents
        )
        total_initial = sum(
            a.get("finances", {}).get("initial_capital", 0) for a in agents
        )
        avg_roi = (
            sum(a.get("performance", {}).get("roi_percent", 0) for a in agents)
            / len(agents)
            if agents
            else 0
        )
        winning_trades = [
            t for t in trades if t.get("result", {}).get("is_winner", False)
        ]
        total_pnl = sum(t.get("result", {}).get("pnl_usd", 0) for t in trades)
        sorted_by_roi = sorted(
            agents,
            key=lambda a: a.get("performance", {}).get("roi_percent", 0),
            reverse=True,
        )
        top_performers = sorted_by_roi[:5] if sorted_by_roi else []

        return {
            "agents": {
                "total": len(agents),
                "active": len(active),
                "dying": len([a for a in agents if a.get("status") == "dying"]),
                "dead": len([a for a in agents if a.get("status") == "dead"]),
                "replicating": len(
                    [a for a in agents if a.get("status") == "replicating"]
                ),
                "by_type": {
                    "crypto_trader": len(
                        [a for a in agents if a.get("agent_type") == "crypto_trader"]
                    ),
                    "business_scout": len(
                        [a for a in agents if a.get("agent_type") == "business_scout"]
                    ),
                    "market_analyzer": len(
                        [a for a in agents if a.get("agent_type") == "market_analyzer"]
                    ),
                },
            },
            "finances": {
                "total_balance": total_balance,
                "total_initial_capital": total_initial,
                "avg_roi": avg_roi,
                "total_pnl": total_pnl,
            },
            "trading": {
                "total_trades": len(trades),
                "winning_trades": len(winning_trades),
                "win_rate": len(winning_trades) / len(trades) if trades else 0,
                "total_pnl": total_pnl,
            },
            "top_performers": [
                {
                    "id": a.get("id"),
                    "name": a.get("name"),
                    "roi": a.get("performance", {}).get("roi_percent", 0),
                    "balance": a.get("finances", {}).get("current_balance", 0),
                }
                for a in top_performers
            ],
            "lineage": {
                "total_generations": max(
                    (a.get("generation", 1) for a in agents), default=1
                ),
                "total_replications": sum(
                    a.get("lineage", {}).get("clone_count", 0) for a in agents
                ),
            },
        }
