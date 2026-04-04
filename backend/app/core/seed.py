import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.config import settings
from app.services.database import DatabaseService
from app.models.requests import AgentCreateRequest
from app.models.enums import AgentType

async def seed_data():
    print(f"Connecting to MongoDB at {settings.MONGO_URL}...")
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]
    db_service = DatabaseService(db)
    
    # Check if agents already exist
    agents = await db_service.get_agents()
    if len(agents) > 0:
        print("Database already contains agents. Skipping seed.")
        return

    print("Seeding initial agents (Genesis Fleet)...")
    
    # Create Root Strategy
    strategy = await db_service.create_strategy(
        name="Genesis Momentum",
        description="Base strategy for the first generation of agents",
        type="momentum",
        timeframe="1h",
        indicators=[
            {"name": "RSI", "params": {"period": 14}, "weight": 1.0},
            {"name": "EMA_CROSS", "params": {"fast": 9, "slow": 21}, "weight": 1.5}
        ]
    )
    
    # Create Root Risk Profile
    risk = await db_service.create_risk_profile(
        name="Standard Genesis Risk",
        description="Safe risk profile for original agents"
    )
    
    # Genesis Agents
    genesis_agents = [
        {"name": "ADAN", "specialization": ["BTC", "ETH"]},
        {"name": "EVA", "specialization": ["SOL", "BNB"]},
        {"name": "LILITH", "specialization": ["ADA", "DOT"]}
    ]
    
    for agent_data in genesis_agents:
        request = AgentCreateRequest(
            name=agent_data["name"],
            agent_type=AgentType.CRYPTO_TRADER,
            initial_capital=1000.0,
            specialization=agent_data["specialization"],
            strategy_id=strategy.id,
            risk_profile_id=risk.id
        )
        agent = await db_service.create_agent(request)
        print(f"Created Genesis Agent: {agent.name} ({agent.id})")
        
    print("Seed complete.")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
