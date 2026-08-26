from pymongo import AsyncMongoClient
import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv("MONGO_URL")
db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
client = AsyncMongoClient(db_url)

def get_client():
    return client

def get_db():
    return client[db_name]
