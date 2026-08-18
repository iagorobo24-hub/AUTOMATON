from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from sqlmodel import Session, select

from app.models import Agent, AgentStatus, StrategyEnum, Trade
from app.database import get_session
from app.services.agent_replication import replicate_agent as create_replica

router = APIRouter()


def _serialize_agent(agent: Agent, session: Session | None = None) -> dict:
    initial = agent.presupuesto_inicial
    current = agent.presupuesto_actual
    trades_count = 0
    successful_trades = 0
    if session is not None and agent.id is not None:
        trades = session.exec(select(Trade).where(Trade.agente_id == agent.id)).all()
        trades_count = len(trades)
        successful_trades = sum(
            1 for trade in trades if trade.resultado is not None and trade.resultado > 0
        )

    return {
        "id": agent.id,
        "nombre": agent.nombre,
        "estrategia": agent.estrategia.value,
        "estado": agent.estado.value,
        "presupuesto_inicial": initial,
        "presupuesto_actual": current,
        "padre_id": agent.padre_id,
        "umbral_replica": agent.umbral_replica,
        "profit": current - initial,
        "profit_percent": ((current - initial) / initial) if initial > 0 else 0,
        "trades_count": trades_count,
        "successful_trades": successful_trades,
        "creado_en": agent.creado_en.isoformat(),
    }


def _get_active_agent(session: Session, agent_id: int) -> Agent:
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if agent.estado != AgentStatus.ACTIVO:
        raise HTTPException(status_code=409, detail="El agente no está activo")
    return agent


@router.get("/")
def get_agents(session: Session = Depends(get_session)) -> List[dict]:
    """List all SQLModel agents with their real trade counters."""
    return [
        _serialize_agent(agent, session)
        for agent in session.exec(select(Agent)).all()
    ]


@router.post("/")
def create_agent(
    nombre: str = Query(min_length=1),
    estrategia: StrategyEnum = StrategyEnum.S1,
    presupuesto: float = Query(gt=0),
    umbral: float = Query(default=0.15, gt=0, lt=1),
    session: Session = Depends(get_session),
) -> dict:
    """Create an active trading agent with validated capital and threshold."""
    normalized_name = nombre.strip()
    if not normalized_name:
        raise HTTPException(status_code=422, detail="El nombre es obligatorio")

    agent = Agent(
        nombre=normalized_name,
        presupuesto_inicial=presupuesto,
        presupuesto_actual=presupuesto,
        estrategia=estrategia,
        estado=AgentStatus.ACTIVO,
        umbral_replica=umbral,
    )
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return _serialize_agent(agent, session)


@router.get("/{agent_id}")
def get_agent(agent_id: int, session: Session = Depends(get_session)) -> dict:
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return _serialize_agent(agent, session)


@router.post("/{agent_id}/replicate")
def replicate_agent(agent_id: int, session: Session = Depends(get_session)) -> dict:
    """Replicate an active agent using the same lifecycle rule as AgentEngine."""
    parent = _get_active_agent(session, agent_id)
    replica = create_replica(session, parent)
    session.commit()
    session.refresh(parent)
    session.refresh(replica)
    return {
        "parent": _serialize_agent(parent, session),
        "replica": _serialize_agent(replica, session),
    }


@router.post("/{agent_id}/deposit")
def deposit_agent(
    agent_id: int,
    amount: float = Query(gt=0),
    session: Session = Depends(get_session),
) -> dict:
    """Add positive capital to an active agent."""
    agent = _get_active_agent(session, agent_id)
    agent.presupuesto_actual += amount
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return _serialize_agent(agent, session)


@router.post("/{agent_id}/simulate-trade")
def simulate_trade_result(
    agent_id: int,
    profit: float,
    session: Session = Depends(get_session),
) -> dict:
    """Apply a simulated PnL result to an active agent without fabricating market data."""
    agent = _get_active_agent(session, agent_id)
    agent.presupuesto_actual = max(0.0, agent.presupuesto_actual + profit)
    if agent.presupuesto_actual <= 0:
        agent.estado = AgentStatus.MUERTO
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return _serialize_agent(agent, session)


@router.delete("/{agent_id}")
def kill_agent(agent_id: int, session: Session = Depends(get_session)) -> dict:
    """Terminate an agent and zero its available budget."""
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if agent.estado == AgentStatus.MUERTO:
        raise HTTPException(status_code=409, detail="El agente ya está muerto")

    agent.estado = AgentStatus.MUERTO
    agent.presupuesto_actual = 0.0
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return _serialize_agent(agent, session)
