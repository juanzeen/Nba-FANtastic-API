from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from typing import Annotated
from fastapi import Depends
import redis.asyncio as aioredis
import os
import dotenv
import json

dotenv.load_dotenv()

db_url = os.getenv("MONGO_URL")
db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
client = AsyncMongoClient(db_url, serverSelectionTimeoutMS=10000)
redis_client = aioredis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

async def get_cached_or_db(cache_key: str, fetch_from_db, expire_seconds: int = 3600):
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    db_data = await fetch_from_db
    if not db_data:
        return None
    await redis_client.set(cache_key, json.dumps(db_data), ex=expire_seconds)
    return db_data

def get_client() -> AsyncMongoClient:
    return client


def get_db() -> AsyncDatabase:
    return client[db_name]


DbDependency = Annotated[AsyncDatabase, Depends(get_db, use_cache=True)]
