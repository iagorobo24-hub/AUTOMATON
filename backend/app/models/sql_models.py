"""
SQLModel models for AUTOMATON v2 - Simplified for SQLite
"""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from app.models.enums import AgentStatus, StrategyEnum, TradeType


class Agent(SQLModel, table=True):
    """Trading agent with budget and strategy"""
    __tablename__ = "agents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    presupuesto_inicial: float
    presupuesto_actual: float
    estrategia: StrategyEnum = Field(default=StrategyEnum.S1)
    estado: AgentStatus = Field(default=AgentStatus.ACTIVO)
    padre_id: Optional[int] = Field(default=None, foreign_key="agents.id")
    umbral_replica: float = Field(default=0.15)  # 15% default
    creado_en: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Self-referential relationship for parent
    padre: Optional["Agent"] = Relationship(
        back_populates="hijos",
        sa_relationship_kwargs={"remote_side": "Agent.id"}
    )
    hijos: list["Agent"] = Relationship(back_populates="padre")
    
    # Relationship with trades
    trades: list["Trade"] = Relationship(back_populates="agente")


class Trade(SQLModel, table=True):
    """Trade execution record"""
    __tablename__ = "trades"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    agente_id: int = Field(foreign_key="agents.id")
    precio_entrada: float
    precio_salida: Optional[float] = None
    cantidad: float
    tipo: TradeType = Field(default=TradeType.LONG)
    resultado: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationship with agent
    agente: Optional[Agent] = Relationship(back_populates="trades")
