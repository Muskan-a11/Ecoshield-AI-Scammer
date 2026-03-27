import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.models.call_log import CallLog
import logging

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/echoshield")

client: AsyncIOMotorClient = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(
        database=client.get_default_database(),
        document_models=[User, CallLog],
    )
    logger.info("Connected to MongoDB.")


async def disconnect_db():
    global client
    if client:
        client.close()
        logger.info("Disconnected from MongoDB.")


def get_client() -> AsyncIOMotorClient:
    return client
