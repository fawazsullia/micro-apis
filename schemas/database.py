from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
import schemas
from config import settings

async def init_db():
    print("Starting database...")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    await init_beanie(
        database=client.get_default_database(),
        document_models=schemas.__all__    )
    print("Database startup complete")
