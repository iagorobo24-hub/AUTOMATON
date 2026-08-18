from sqlmodel import Session

from app.models import Agent, AgentStatus


def replicate_agent(session: Session, parent: Agent) -> Agent:
    """Apply the canonical SQLModel replication transition and create one child."""
    parent.estado = AgentStatus.REPLICADO
    replica = Agent(
        nombre=f"{parent.nombre}_child_{parent.id}",
        presupuesto_inicial=parent.presupuesto_inicial,
        presupuesto_actual=parent.presupuesto_inicial,
        estrategia=parent.estrategia,
        estado=AgentStatus.ACTIVO,
        padre_id=parent.id,
        umbral_replica=parent.umbral_replica,
    )
    session.add(parent)
    session.add(replica)
    return replica
