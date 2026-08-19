from dataclasses import dataclass
from decimal import Decimal

from sqlmodel import Session, select

from app.accounting.service import AccountingError, AccountingService
from app.agent_evolution.fitness import FitnessService
from app.agent_evolution.policy import active_evolution_policy
from app.models import (
    Account,
    Agent,
    AgentFitnessEvaluation,
    AgentLifecycleEvent,
    AgentLineage,
    AgentStatus,
)

ZERO = Decimal("0")
TRANSFER_QUANTUM = Decimal("0.00000001")


class EvolutionError(ValueError):
    pass


@dataclass(frozen=True)
class ReplicationResult:
    parent: Agent
    child: Agent
    lineage: AgentLineage
    fitness: AgentFitnessEvaluation
    allocated_capital: Decimal


class AgentEvolutionService:
    def __init__(self, session: Session):
        self.session = session

    def _parent_generation(self, parent_agent_id: int) -> int:
        lineage = self.session.exec(
            select(AgentLineage).where(AgentLineage.child_agent_id == parent_agent_id)
        ).first()
        return lineage.generation if lineage is not None else 0

    def replicate(self, parent_agent_id: int) -> ReplicationResult:
        parent = self.session.get(Agent, parent_agent_id)
        if parent is None:
            raise EvolutionError("parent agent not found")
        if parent.estado != AgentStatus.ACTIVO:
            raise EvolutionError("parent agent must be active to replicate")

        fitness = FitnessService(self.session).evaluate(parent.id)
        if fitness.decision != "PASS":
            raise EvolutionError(f"fitness rejected: {fitness.reason_codes}")
        if not fitness.strategy_version or not fitness.strategy_code_sha256:
            raise EvolutionError("fitness PASS is missing reproducible strategy provenance")

        policy = active_evolution_policy(self.session)
        parent_account = self.session.exec(
            select(Account).where(Account.agente_id == parent.id)
        ).first()
        if parent_account is None:
            raise EvolutionError("parent accounting account not found")

        available_cash = Decimal(parent_account.cash) - Decimal(parent_account.reserved_cash)
        eligible_base = min(available_cash, Decimal(parent_account.funded_capital))
        if eligible_base <= ZERO:
            raise EvolutionError("parent has no eligible funded liquid capital")
        allocation = (eligible_base * Decimal(policy.child_allocation_fraction)).quantize(TRANSFER_QUANTUM)
        if allocation <= ZERO:
            raise EvolutionError("child allocation rounds to zero")

        generation = self._parent_generation(parent.id) + 1
        child_index = len(
            self.session.exec(
                select(AgentLineage).where(AgentLineage.parent_agent_id == parent.id)
            ).all()
        ) + 1
        child = Agent(
            nombre=f"{parent.nombre}-g{generation}-{child_index}",
            presupuesto_inicial=float(allocation),
            presupuesto_actual=float(allocation),
            estrategia=parent.estrategia,
            estado=AgentStatus.ACTIVO,
            padre_id=parent.id,
            umbral_replica=parent.umbral_replica,
        )
        self.session.add(child)
        self.session.flush()

        try:
            parent_after, child_account = AccountingService(self.session).transfer_to_child(
                parent_account.id,
                child.id,
                allocation,
                reason=f"agent_replication:{parent.id}->{child.id}",
                commit=False,
            )
            parent.presupuesto_inicial = float(parent_after.funded_capital)
            parent.presupuesto_actual = float(parent_after.cash)
            child.presupuesto_inicial = float(child_account.funded_capital)
            child.presupuesto_actual = float(child_account.cash)
            self.session.add(parent)
            self.session.add(child)

            lineage = AgentLineage(
                parent_agent_id=parent.id,
                child_agent_id=child.id,
                generation=generation,
                strategy_id=parent.estrategia.value,
                strategy_version=fitness.strategy_version,
                strategy_code_sha256=fitness.strategy_code_sha256,
                policy_version=policy.version,
                fitness_evaluation_id=fitness.id,
                allocated_capital=allocation,
            )
            self.session.add(lineage)
            self.session.flush()

            fitness.consumed_by_lineage_id = lineage.id
            self.session.add(fitness)
            self.session.add(
                AgentLifecycleEvent(
                    agent_id=parent.id,
                    event_type="REPLICATED_TO",
                    reason="evolution_v1_evidence_pass",
                    fitness_evaluation_id=fitness.id,
                    lineage_id=lineage.id,
                )
            )
            self.session.add(
                AgentLifecycleEvent(
                    agent_id=child.id,
                    event_type="REPLICATED_FROM",
                    reason="evolution_v1_child_created",
                    fitness_evaluation_id=fitness.id,
                    lineage_id=lineage.id,
                )
            )
            self.session.commit()
        except AccountingError as exc:
            self.session.rollback()
            raise EvolutionError(str(exc)) from exc
        except Exception:
            self.session.rollback()
            raise

        self.session.refresh(parent)
        self.session.refresh(child)
        self.session.refresh(lineage)
        self.session.refresh(fitness)
        return ReplicationResult(
            parent=parent,
            child=child,
            lineage=lineage,
            fitness=fitness,
            allocated_capital=allocation,
        )
