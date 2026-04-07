"""
Migration script: Convert metadata.simulation (bool) to metadata.mode (string)
Run this once after deploying the mode system changes.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def migrate():
    print(f"Connecting to {settings.MONGO_URL}...")
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

    # Convert simulation=true -> mode=test
    result1 = await db.agents.update_many(
        {"metadata.simulation": True},
        {"$set": {"metadata.mode": "test"}, "$unset": {"metadata.simulation": ""}},
    )
    print(f"simulation=true -> mode=test: {result1.modified_count} agents")

    # Convert simulation=false -> mode=real
    result2 = await db.agents.update_many(
        {"metadata.simulation": False},
        {"$set": {"metadata.mode": "real"}, "$unset": {"metadata.simulation": ""}},
    )
    print(f"simulation=false -> mode=real: {result2.modified_count} agents")

    # Default agents without mode field to test mode
    result3 = await db.agents.update_many(
        {"metadata.mode": {"$exists": False}},
        {"$set": {"metadata.mode": "test"}},
    )
    print(f"no mode field -> mode=test: {result3.modified_count} agents")

    # Verify
    total = await db.agents.count_documents({"metadata.mode": {"$exists": True}})
    missing = await db.agents.count_documents({"metadata.mode": {"$exists": False}})
    print(f"\nVerification: {total} agents with mode, {missing} without")

    client.close()
    print("Migration complete.")


if __name__ == "__main__":
    asyncio.run(migrate())
