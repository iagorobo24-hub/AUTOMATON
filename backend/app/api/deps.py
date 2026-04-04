from typing import Generator
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings
from ..services.database import DatabaseService
from ..services.notifications import NotificationService

# Initialize MongoDB client
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

async def get_db_service() -> DatabaseService:
    return DatabaseService(db)

async def get_notification_service() -> NotificationService:
    return NotificationService(db)
