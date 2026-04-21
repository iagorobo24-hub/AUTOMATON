import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Dict, Any
from .database import DatabaseService
from .notifications import NotificationService
from ..models.enums import AgentStatus
from ..models.requests import AgentReplicateRequest

logger = logging.getLogger(__name__)


class ReplicationService:
    """Service to handle automated agent replication based on performance"""

    # Global limits to prevent runaway replication
    MAX_TOTAL_AGENTS = 100
    MAX_AGENT_CHILDREN = 10
    MAX_MUTATION_RANGE = 0.15
    MIN_ROI_THRESHOLD = 30.0

    def __init__(self, db_service: DatabaseService, notification_service: NotificationService):
        self.db_service = db_service
        self.notification_service = notification_service
        self.is_running = False
        self.check_interval = 60
        self._total_agents_count = 0 # Check every 60 seconds

    async def start(self):
        self.is_running = True
        asyncio.create_task(self._replication_loop())
        logger.info("Replication Service started")

    async def stop(self):
        self.is_running = False

    async def _replication_loop(self):
        while self.is_running:
            try:
                await self.check_and_replicate_eligible_agents()
            except Exception as e:
                logger.error(f"Error in replication loop: {e}")
            await asyncio.sleep(self.check_interval)

async def check_and_replicate_eligible_agents(self):
        """Find agents that meet replication criteria and clone them"""

        all_agents = await self.db_service.get_agents()
        self._total_agents_count = len(all_agents)

        if self._total_agents_count >= self.MAX_TOTAL_AGENTS:
            logger.warning(f"Global agent limit: {self._total_agents_count}/{self.MAX_TOTAL_AGENTS}")
            return

        agents = await self.db_service.get_agents(status=AgentStatus.ACTIVE)

        for agent in agents:
            perf = agent.get('performance', {})
            rules = agent.get('replication_rules', {})

            roi = perf.get('roi_percent', 0)
            min_roi = rules.get('min_roi_to_replicate', self.MIN_ROI_THRESHOLD)

            lineage = agent.get('lineage', {})
            current_children = lineage.get('clone_count', 0)
            max_children = min(rules.get('max_children', self.MAX_AGENT_CHILDREN), self.MAX_AGENT_CHILDREN)

            if roi >= min_roi and rules.get('auto_replicate', True):
                if current_children < max_children:
                    logger.info(f"Agent {agent['name']} eligible: ROI={roi:.1f}%")
                    await self._replicate_agent(agent)
                else:
                    logger.info(f"Agent {agent['name']} skipped: max children")

async def _replicate_agent(self, agent: Dict[str, Any]):
        """Execute replication with mutation logic"""
        agent_id = agent['id']

        request = AgentReplicateRequest(
            capital_split_ratio=agent.get('replication_rules', {}).get('capital_split_ratio', 0.5),
            mutation_enabled=agent.get('replication_rules', {}).get('mutation_enabled', True),
            mutation_rate=agent.get('replication_rules', {}).get('mutation_rate', 0.1)
        )

        try:
            child = await self.db_service.replicate_agent(agent_id, request)
            if child:
                if request.mutation_enabled:
                    await self._mutate_strategy(child.id, agent.get('config', {}).get('strategy_id'))

                logger.info(f"Successfully replicated {agent['name']}")
        except ValueError as e:
            logger.warning(f"Replication failed for {agent['name']}: {e}")

async def _mutate_strategy(self, agent_id: str, parent_strategy_id: str):
        """Mutate strategy parameters with safe bounds"""
        if not parent_strategy_id:
            return

        parent_strategy = await self.db_service.get_strategy(parent_strategy_id)
        if not parent_strategy:
            return

        mutated_name = f"Mutated {parent_strategy['name']}"

        indicators = parent_strategy.get('indicators', [])
        for ind in indicators:
            params = ind.get('params', {})
            for key, val in params.items():
                if isinstance(val, (int, float)):
                    mutation_factor = random.uniform(-self.MAX_MUTATION_RANGE, self.MAX_MUTATION_RANGE)
                    new_val = val * (1 + mutation_factor)
                    if 0 < new_val < val * 10:
                        params[key] = new_val

        new_strategy = await self.db_service.create_strategy(
            name=mutated_name,
            description=f"Derived from {parent_strategy['name']} via mutation",
            type=parent_strategy.get('type', 'momentum'),
            timeframe=parent_strategy.get('timeframe', '4h'),
            indicators=indicators,
            parent_strategy_id=parent_strategy_id
        )

        await self.db_service.update_agent(agent_id, {
            "config.strategy_id": new_strategy.id,
            "config.parent_rollback": parent_strategy_id
        })

        logger.info(f"Strategy mutated for agent {agent_id}")
