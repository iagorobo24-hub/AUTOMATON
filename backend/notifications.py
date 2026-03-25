"""
Automaton Orchestrator - Notifications Service
Handles system notifications, alerts and activity feed
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
import uuid


class NotificationType:
    AGENT_CREATED = "agent_created"
    AGENT_REPLICATED = "agent_replicated"
    AGENT_DYING = "agent_dying"
    AGENT_DEAD = "agent_dead"
    TRADE_OPENED = "trade_opened"
    TRADE_CLOSED = "trade_closed"
    TRADE_WIN = "trade_win"
    TRADE_LOSS = "trade_loss"
    PAYMENT_RECEIVED = "payment_received"
    ALERT_LOW_BALANCE = "alert_low_balance"
    ALERT_HIGH_DRAWDOWN = "alert_high_drawdown"
    ALERT_REPLICATION_READY = "alert_replication_ready"
    SYSTEM_INFO = "system_info"
    OPPORTUNITY_DETECTED = "opportunity_detected"


class NotificationPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    priority: str = NotificationPriority.MEDIUM
    title: str
    message: str
    icon: str = "bell"
    color: str = "primary"  # primary, green, red, purple, yellow
    link: Optional[str] = None  # URL to navigate when clicked
    agent_id: Optional[str] = None
    trade_id: Optional[str] = None
    read: bool = False
    dismissed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class ActivityEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    title: str
    description: str
    icon: str
    color: str = "primary"
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    amount: Optional[float] = None
    link: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = {}


class NotificationService:
    """Service for managing notifications and activity feed"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.notifications = db.notifications
        self.activity_feed = db.activity_feed
    
    def _serialize_datetime(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        return obj
    
    # ==================== NOTIFICATIONS ====================
    
    async def create_notification(
        self,
        type: str,
        title: str,
        message: str,
        priority: str = NotificationPriority.MEDIUM,
        icon: str = "bell",
        color: str = "primary",
        link: str = None,
        agent_id: str = None,
        trade_id: str = None,
        expires_hours: int = 24,
        metadata: Dict = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            type=type,
            priority=priority,
            title=title,
            message=message,
            icon=icon,
            color=color,
            link=link,
            agent_id=agent_id,
            trade_id=trade_id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_hours),
            metadata=metadata or {}
        )
        
        doc = self._serialize_datetime(notification.model_dump())
        await self.notifications.insert_one(doc)
        return notification
    
    async def get_notifications(
        self,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Get notifications, optionally filtered"""
        query = {"dismissed": False}
        if unread_only:
            query["read"] = False
        
        notifications = await self.notifications.find(
            query, {"_id": 0}
        ).sort("created_at", -1).to_list(limit)
        
        return notifications
    
    async def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return await self.notifications.count_documents({
            "read": False,
            "dismissed": False
        })
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        result = await self.notifications.update_one(
            {"id": notification_id},
            {"$set": {"read": True}}
        )
        return result.modified_count > 0
    
    async def mark_all_as_read(self) -> int:
        """Mark all notifications as read"""
        result = await self.notifications.update_many(
            {"read": False},
            {"$set": {"read": True}}
        )
        return result.modified_count
    
    async def dismiss_notification(self, notification_id: str) -> bool:
        """Dismiss/delete a notification"""
        result = await self.notifications.update_one(
            {"id": notification_id},
            {"$set": {"dismissed": True}}
        )
        return result.modified_count > 0
    
    async def dismiss_all(self) -> int:
        """Dismiss all notifications"""
        result = await self.notifications.update_many(
            {"dismissed": False},
            {"$set": {"dismissed": True}}
        )
        return result.modified_count
    
    # ==================== ACTIVITY FEED ====================
    
    async def log_activity(
        self,
        type: str,
        title: str,
        description: str,
        icon: str = "activity",
        color: str = "primary",
        agent_id: str = None,
        agent_name: str = None,
        amount: float = None,
        link: str = None,
        metadata: Dict = None
    ) -> ActivityEvent:
        """Log an activity event"""
        event = ActivityEvent(
            type=type,
            title=title,
            description=description,
            icon=icon,
            color=color,
            agent_id=agent_id,
            agent_name=agent_name,
            amount=amount,
            link=link,
            metadata=metadata or {}
        )
        
        doc = self._serialize_datetime(event.model_dump())
        await self.activity_feed.insert_one(doc)
        return event
    
    async def get_activity_feed(
        self,
        agent_id: str = None,
        type_filter: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get activity feed with optional filters"""
        query = {}
        if agent_id:
            query["agent_id"] = agent_id
        if type_filter:
            query["type"] = type_filter
        
        events = await self.activity_feed.find(
            query, {"_id": 0}
        ).sort("created_at", -1).to_list(limit)
        
        return events
    
    # ==================== HELPER METHODS ====================
    
    async def notify_agent_created(self, agent_id: str, agent_name: str, capital: float):
        """Notificación cuando se crea un agente"""
        await self.create_notification(
            type=NotificationType.AGENT_CREATED,
            title="Agente Desplegado",
            message=f"{agent_name} creado con €{capital:.2f}",
            icon="bot",
            color="primary",
            link=f"/agents",
            agent_id=agent_id
        )
        await self.log_activity(
            type=NotificationType.AGENT_CREATED,
            title="Nuevo Agente Desplegado",
            description=f"{agent_name} inicializado con €{capital:.2f} de capital",
            icon="bot",
            color="primary",
            agent_id=agent_id,
            agent_name=agent_name,
            amount=capital,
            link=f"/agents"
        )
    
    async def notify_agent_replicated(self, parent_name: str, child_name: str, child_id: str, capital: float):
        """Notificación cuando un agente se replica"""
        await self.create_notification(
            type=NotificationType.AGENT_REPLICATED,
            title="¡Agente Replicado!",
            message=f"{parent_name} creó clon {child_name} con €{capital:.2f}",
            icon="copy",
            color="green",
            priority=NotificationPriority.HIGH,
            link=f"/agents",
            agent_id=child_id
        )
        await self.log_activity(
            type=NotificationType.AGENT_REPLICATED,
            title="Evento de Replicación",
            description=f"{parent_name} → {child_name} (€{capital:.2f})",
            icon="git-branch",
            color="green",
            agent_id=child_id,
            agent_name=child_name,
            amount=capital
        )
    
    async def notify_agent_dying(self, agent_id: str, agent_name: str, balance: float):
        """Alerta cuando el balance del agente es críticamente bajo"""
        await self.create_notification(
            type=NotificationType.AGENT_DYING,
            title="¡Agente en Riesgo!",
            message=f"{agent_name} saldo crítico: €{balance:.2f}",
            icon="alert-triangle",
            color="red",
            priority=NotificationPriority.CRITICAL,
            link=f"/agents",
            agent_id=agent_id
        )
        await self.log_activity(
            type=NotificationType.AGENT_DYING,
            title="Agente Crítico",
            description=f"{agent_name} entró en estado crítico",
            icon="alert-triangle",
            color="red",
            agent_id=agent_id,
            agent_name=agent_name,
            amount=balance
        )
    
    async def notify_agent_dead(self, agent_id: str, agent_name: str, reason: str):
        """Notificación cuando un agente muere"""
        await self.create_notification(
            type=NotificationType.AGENT_DEAD,
            title="Agente Terminado",
            message=f"{agent_name} terminado: {reason}",
            icon="skull",
            color="red",
            link=f"/agents",
            agent_id=agent_id
        )
        await self.log_activity(
            type=NotificationType.AGENT_DEAD,
            title="Agente Terminado",
            description=f"{agent_name} - {reason}",
            icon="skull",
            color="red",
            agent_id=agent_id,
            agent_name=agent_name
        )
    
    async def notify_trade_result(
        self, 
        agent_id: str, 
        agent_name: str, 
        trade_id: str,
        symbol: str,
        pnl: float,
        is_win: bool
    ):
        """Notificación de resultado de trade"""
        type_ = NotificationType.TRADE_WIN if is_win else NotificationType.TRADE_LOSS
        color = "green" if is_win else "red"
        icon = "trending-up" if is_win else "trending-down"
        
        await self.log_activity(
            type=type_,
            title=f"Trade {'Ganado' if is_win else 'Perdido'}",
            description=f"{agent_name} {symbol}: {'+' if pnl >= 0 else ''}€{pnl:.2f}",
            icon=icon,
            color=color,
            agent_id=agent_id,
            agent_name=agent_name,
            amount=pnl
        )
        
        # Solo crear notificación para ganancias/pérdidas significativas
        if abs(pnl) >= 10:
            await self.create_notification(
                type=type_,
                title=f"Trade {'Ganado' if is_win else 'Perdido'}: €{abs(pnl):.2f}",
                message=f"{agent_name} cerró posición de {symbol}",
                icon=icon,
                color=color,
                link=f"/agents",
                agent_id=agent_id,
                trade_id=trade_id
            )
    
    async def notify_replication_ready(self, agent_id: str, agent_name: str, roi: float):
        """Alerta cuando un agente está listo para replicar"""
        await self.create_notification(
            type=NotificationType.ALERT_REPLICATION_READY,
            title="¡Listo para Replicar!",
            message=f"{agent_name} alcanzó {roi:.1f}% ROI - elegible para replicación",
            icon="zap",
            color="purple",
            priority=NotificationPriority.HIGH,
            link=f"/agents",
            agent_id=agent_id
        )
    
    async def notify_opportunity(self, symbol: str, signal_type: str, confidence: float):
        """Notificación de oportunidad de trading detectada"""
        await self.create_notification(
            type=NotificationType.OPPORTUNITY_DETECTED,
            title=f"Oportunidad: {symbol}",
            message=f"Señal {signal_type} detectada ({confidence*100:.0f}% confianza)",
            icon="target",
            color="yellow",
            link=f"/crypto"
        )
        await self.log_activity(
            type=NotificationType.OPPORTUNITY_DETECTED,
            title=f"Señal: {symbol}",
            description=f"{signal_type} - {confidence*100:.0f}% confianza",
            icon="target",
            color="yellow"
        )
