from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from typing import Annotated
from fastapi import Depends
import redis.asyncio as aioredis
import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv("MONGO_URL")
db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
client = AsyncMongoClient(db_url, serverSelectionTimeoutMS=10000)
redis_client = aioredis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

def get_client() -> AsyncMongoClient:
    return client


def get_db() -> AsyncDatabase:
    return client[db_name]

def get_redis() -> aioredis.Redis:
    return redis_client


DbDependency = Annotated[AsyncDatabase, Depends(get_db, use_cache=True)]
RedisDependency = Annotated[aioredis.Redis, Depends(get_redis)]
