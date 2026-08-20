from fastapi import FastAPI
from pymongo import AsyncMongoClient
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI()
db_url = os.getenv("MONGO_URL")
db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
client = AsyncMongoClient(db_url)
db = client[db_name]


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/historical-players")
async def get_historical_players():
    hp = db["historical_players"]
    players = await hp.find().to_list(max_length=100)
    print(players)

    return {"message": "testing retrieve players"}

@app.get("/historical-players/{player_name}")
async def get_historical_player_by_name1(player_name: str):
    hp = db["historical_players"]
    normalized_player_name = player_name.replace("-", " ").title()
    player = await hp.find_one({"full_name": normalized_player_name})
    if player:
      return {"player": player, "message": "Player successfully retrieved.", "status": 200}
    return {"message": f"{normalized_player_name} not found.", "status": 404}
