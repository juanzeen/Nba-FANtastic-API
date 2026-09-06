from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from typing import Annotated
from fastapi import Depends
import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv("MONGO_URL")
db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
client = AsyncMongoClient(db_url)


def get_client() -> AsyncMongoClient:
    return client


def get_db() -> AsyncDatabase:
    return client[db_name]

DbDependency = Annotated[AsyncDatabase, Depends(get_db, use_cache=True)]
