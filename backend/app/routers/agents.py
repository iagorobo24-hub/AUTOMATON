from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlmodel import Session, select

from app.models import Agent, AgentStatus, StrategyEnum
from app.database import get_session
from app.services.agent_engine import AgentEngine

router = APIRouter()


@router.get("/")
def get_agents(
    session: Session = Depends(get_session)
) -> List[dict]:
    """List all agents with their current status"""
    agentes = session.exec(select(Agent)).all()
    return [
        {
            "id": a.id,
            "nombre": a.nombre,
            "estrategia": a.estrategia.value,
            "estado": a.estado.value,
            "presupuesto_inicial": a.presupuesto_inicial,
            "presupuesto_actual": a.presupuesto_actual,
            "padre_id": a.padre_id,
            "umbral_replica": a.umbral_replica,
            "profit": a.presupuesto_actual - a.presupuesto_inicial,
            "creado_en": a.creado_en.isoformat(),
        }
        for a in agentes
    ]


@router.post("/")
def create_agent(
    nombre: str,
    estrategia: StrategyEnum,
    presupuesto: float,
    umbral: float = 0.15,
    session: Session = Depends(get_session)
) -> dict:
    """Create a new agent"""
    agente = Agent(
        nombre=nombre,
        presupuesto_inicial=presupuesto,
        presupuesto_actual=presupuesto,
        estrategia=estrategia,
        estado=AgentStatus.ACTIVO,
        umbral_replica=umbral,
    )
    session.add(agente)
    session.commit()
    session.refresh(agente)
    
    return {
        "id": agente.id,
        "nombre": agente.nombre,
        "estrategia": agente.estrategia.value,
        "estado": agente.estado.value,
        "presupuesto_inicial": agente.presupuesto_inicial,
        "umbral_replica": agente.umbral_replica,
        "creado_en": agente.creado_en.isoformat(),
    }


@router.get("/{agent_id}")
def get_agent(
    agent_id: int,
    session: Session = Depends(get_session)
) -> dict:
    """Get detail of a single agent"""
    agente = session.get(Agent, agent_id)
    if not agente:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    
    return {
        "id": agente.id,
        "nombre": agente.nombre,
        "estrategia": agente.estrategia.value,
        "estado": agente.estado.value,
        "presupuesto_inicial": agente.presupuesto_inicial,
        "presupuesto_actual": agente.presupuesto_actual,
        "padre_id": agente.padre_id,
        "umbral_replica": agente.umbral_replica,
        "profit": agente.presupuesto_actual - agente.presupuesto_inicial,
        "profit_percent": (agente.presupuesto_actual - agente.presupuesto_inicial) / agente.presupuesto_inicial,
        "creado_en": agente.creado_en.isoformat(),
    }


@router.delete("/{agent_id}")
def kill_agent(
    agent_id: int,
    session: Session = Depends(get_session)
) -> dict:
    """Kill an agent manually (set estado to MUERTO)"""
    agente = session.get(Agent, agent_id)
    if not agente:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    
    agente.estado = AgentStatus.MUERTO
    session.add(agente)
    session.commit()
    
    return {
        "id": agente.id,
        "nombre": agente.nombre,
        "estado": agente.estado.value,
        "message": f"Agente {agent_id} eliminado manualmente",
    }
