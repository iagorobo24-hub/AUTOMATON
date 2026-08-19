from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from sqlmodel import Session, select

from app.accounting.service import AccountingError, AccountingService
from app.models import Account, Agent, AgentStatus, StrategyEnum, Trade
from app.database import get_session

router = APIRouter()


EVIDENCE_MODE = "legacy_unclassified"


def _serialize_agent(agent: Agent, session: Session | None = None) -> dict:
    initial = agent.presupuesto_inicial
    current = agent.presupuesto_actual
    legacy_trades_count = 0
    if session is not None and agent.id is not None:
        legacy_trades_count = len(
            session.exec(select(Trade).where(Trade.agente_id == agent.id)).all()
        )
        account = session.exec(
            select(Account).where(Account.agente_id == agent.id)
        ).first()
        if account is not None:
            initial = float(account.funded_capital)
            current = float(account.cash)

    return {
        "id": agent.id,
        "nombre": agent.nombre,
        "estrategia": agent.estrategia.value,
        "estado": agent.estado.value,
        "presupuesto_inicial": initial,
        "presupuesto_actual": current,
        "padre_id": agent.padre_id,
        "umbral_replica": agent.umbral_replica,
        "profit": None,
        "profit_percent": None,
        "trades_count": None,
        "successful_trades": None,
        "legacy_trades_count": legacy_trades_count,
        "performance_evidence_valid": False,
        "evidence_mode": EVIDENCE_MODE,
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
    """List agents without treating legacy synthetic history as financial evidence."""
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
    session.flush()
    AccountingService(session).create_account(agent.id, Decimal(str(presupuesto)))
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
    """Blocked until Agent Evolution defines a capital-transfer policy."""
    _get_active_agent(session, agent_id)
    raise HTTPException(
        status_code=409,
        detail=(
            "Replication is blocked until an explicit capital allocation policy "
            "is implemented; duplicating parent capital is forbidden"
        ),
    )


@router.post("/{agent_id}/deposit")
def deposit_agent(
    agent_id: int,
    amount: float = Query(gt=0),
    session: Session = Depends(get_session),
) -> dict:
    """Fund an active agent through the authoritative accounting ledger."""
    agent = _get_active_agent(session, agent_id)
    account = session.exec(
        select(Account).where(Account.agente_id == agent.id)
    ).first()
    if account is None:
        raise HTTPException(status_code=409, detail="El agente no tiene cuenta contable")

    agent.presupuesto_inicial += amount
    agent.presupuesto_actual += amount
    session.add(agent)
    try:
        AccountingService(session).deposit(
            account.id,
            Decimal(str(amount)),
            reason="operator_funding",
        )
    except AccountingError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    session.refresh(agent)
    return _serialize_agent(agent, session)


@router.delete("/{agent_id}")
def kill_agent(agent_id: int, session: Session = Depends(get_session)) -> dict:
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if agent.estado == AgentStatus.MUERTO:
        raise HTTPException(status_code=409, detail="El agente ya está muerto")

    agent.estado = AgentStatus.MUERTO
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return _serialize_agent(agent, session)
