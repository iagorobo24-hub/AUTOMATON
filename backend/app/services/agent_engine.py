"""
Agent Engine for AUTOMATON v2
Manages agent lifecycle, trading execution, death and replication logic
"""
import asyncio
import random
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import Session, select

from app.models import Agent, Trade, AgentStatus, StrategyEnum, TradeType
from app.services.strategies import get_strategy
from app.database import SessionLocal


class AgentEngine:
    """Engine that runs agent trading simulation"""
    
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None
        
        # Precios base para simulación
        self.precios_base = {
            'BTC': 65000.0,
            'ETH': 3500.0,
            'SOL': 150.0,
        }
        
        # Historial de precios simulados (para cada símbolo)
        self.historial_precios: Dict[str, list[float]] = {
            'BTC': [65000.0] * 30,
            'ETH': [3500.0] * 30,
            'SOL': [150.0] * 30,
        }
    
    async def start(self):
        """Start the agent engine loop"""
        self.running = True
        self.task = asyncio.create_task(self._run_loop())
        print("[ENGINE] AgentEngine started")
    
    async def stop(self):
        """Stop the agent engine"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("[ENGINE] AgentEngine stopped")
    
    async def _run_loop(self):
        """Main loop that runs every 5 seconds"""
        while self.running:
            try:
                await self._tick()
                await asyncio.sleep(5)  # 5 segundos como especifica el prompt
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"[ENGINE] Error in tick: {e}")
                await asyncio.sleep(5)
    
    async def _tick(self):
        """Execute one tick of the simulation"""
        # Actualizar precios simulados (random walk)
        self._actualizar_precios()
        
        # Procesar agentes activos
        with SessionLocal() as session:
            agentes = session.exec(
                select(Agent).where(Agent.estado == AgentStatus.ACTIVO)
            ).all()
            
            for agente in agentes:
                await self._procesar_agente(session, agente)
            
            session.commit()
    
    def _actualizar_precios(self):
        """Update simulated prices with random walk"""
        for symbol, precio in self.precios_base.items():
            # Random walk: cambio de ±2% máximo
            cambio = random.uniform(-0.02, 0.02)
            nuevo_precio = self.historial_precios[symbol][-1] * (1 + cambio)
            
            # Mantener dentro de rangos razonables
            if symbol == 'BTC':
                nuevo_precio = max(40000, min(90000, nuevo_precio))
            elif symbol == 'ETH':
                nuevo_precio = max(2000, min(5000, nuevo_precio))
            elif symbol == 'SOL':
                nuevo_precio = max(80, min(250, nuevo_precio))
            
            self.historial_precios[symbol].append(nuevo_precio)
            # Mantener solo últimos 50 precios
            self.historial_precios[symbol] = self.historial_precios[symbol][-50:]
    
    async def _procesar_agente(self, session: Session, agente: Agent):
        """Process a single agent's trading logic"""
        # Usar BTC como símbolo por defecto
        symbol = 'BTC'
        precio_actual = self.historial_precios[symbol][-1]
        
        # Ejecutar estrategia
        strategy = get_strategy(agente.estrategia.value)
        señal = strategy.calcular_señal(self.historial_precios[symbol])
        
        if señal == 'BUY' and agente.presupuesto_actual > 0:
            # Simular compra
            cantidad = agente.presupuesto_actual * 0.1 / precio_actual  # Usar 10% del presupuesto
            costo = cantidad * precio_actual
            
            if costo <= agente.presupuesto_actual:
                agente.presupuesto_actual -= costo
                
                # Crear trade
                trade = Trade(
                    agente_id=agente.id,
                    precio_entrada=precio_actual,
                    cantidad=cantidad,
                    tipo=TradeType.LONG,
                )
                session.add(trade)
                
                print(f"[AGENT {agente.id}] BUY @ {precio_actual:.2f}")
        
        # Simular cierre de trades abiertos (para simplificación)
        trades_abiertos = session.exec(
            select(Trade).where(
                Trade.agente_id == agente.id,
                Trade.precio_salida == None
            )
        ).all()
        
        for trade in trades_abiertos:
            # Cerrar trade con 30% de probabilidad o si señal es SELL
            if señal == 'SELL' or random.random() < 0.3:
                trade.precio_salida = precio_actual
                
                if trade.tipo == TradeType.LONG:
                    pnl = trade.cantidad * (precio_actual - trade.precio_entrada)
                else:
                    pnl = trade.cantidad * (trade.precio_entrada - precio_actual)
                
                trade.resultado = pnl
                agente.presupuesto_actual += trade.cantidad * precio_actual + pnl
                
                print(f"[AGENT {agente.id}] CLOSE @ {precio_actual:.2f} PnL: {pnl:.2f}")
        
        # Verificar condición de MUERTE
        if agente.presupuesto_actual <= 0:
            agente.estado = AgentStatus.MUERTO
            print(f"[AGENT {agente.id}] ☠️ MUERTO - presupuesto agotado")
        
        # Verificar condición de RÉPLICA (profit > umbral)
        profit = (agente.presupuesto_actual - agente.presupuesto_inicial) / agente.presupuesto_inicial
        if profit >= agente.umbral_replica:
            agente.estado = AgentStatus.REPLICADO
            print(f"[AGENT {agente.id}] 🧬 REPLICADO - profit: {profit:.2%}")
            
            # Crear réplica
            self._crear_replica(session, agente)
        
        session.add(agente)
    
    def _crear_replica(self, session: Session, agente: Agent):
        """Create a replica of a successful agent"""
        replica = Agent(
            nombre=f"{agente.nombre}_child_{agente.id}",
            presupuesto_inicial=agente.presupuesto_inicial,
            presupuesto_actual=agente.presupuesto_inicial,  # Presupuesto fresco
            estrategia=agente.estrategia,
            estado=AgentStatus.ACTIVO,
            padre_id=agente.id,
            umbral_replica=agente.umbral_replica,
        )
        session.add(replica)
        print(f"[ENGINE] Réplica creada de agente {agente.id}")
    
    def crear_agente(
        self,
        nombre: str,
        estrategia: StrategyEnum,
        presupuesto: float,
        umbral: float = 0.15
    ) -> Agent:
        """Create a new agent"""
        with SessionLocal() as session:
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
            print(f"[ENGINE] Agente creado: {agente.id} - {nombre}")
            return agente
    
    def get_estado(self) -> Dict[str, Any]:
        """Get current state of all agents and stats"""
        with SessionLocal() as session:
            agentes = session.exec(select(Agent)).all()
            
            total_agentes = len(agentes)
            activos = sum(1 for a in agentes if a.estado == AgentStatus.ACTIVO)
            muertos = sum(1 for a in agentes if a.estado == AgentStatus.MUERTO)
            replicados = sum(1 for a in agentes if a.estado == AgentStatus.REPLICADO)
            
            profit_total = sum(
                a.presupuesto_actual - a.presupuesto_inicial
                for a in agentes
            )
            
            return {
                "precios_actuales": {
                    symbol: self.historial_precios[symbol][-1]
                    for symbol in self.precios_base.keys()
                },
                "agentes_totales": total_agentes,
                "agentes_activos": activos,
                "agentes_muertos": muertos,
                "agentes_replicados": replicados,
                "profit_total": profit_total,
                "agentes": [
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
                ],
            }
