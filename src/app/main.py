from fastapi import FastAPI
from pymongo import AsyncMongoClient
import os
import dotenv
from app.utils.strings import format_player_name
from pydantic import BaseModel

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
    players = await hp.find().to_list()
    print(players)

    return {"message": players}


@app.get("/historical-players/{id}")
async def get_historical_player_by_id(id: int):
    hp = db["historical_players"]
    player = await hp.find_one({"_id": id})
    print(player)
    if player:
        return {
            "player": player.full_name,
            "message": "Player successfully retrieved.",
            "status": 200,
        }
    return {"message": f"Player with {id} not found.", "status": 404}

@app.get("/historical-players/")
async def get_historical_player_by_name(name: str):
    hp = db["historical_players"]
    formatted_player_name = format_player_name(name)
    player = await hp.find_one({"full_name": formatted_player_name})
    if player:
        return {
            "player": player,
            "message": "Player successfully retrieved.",
            "status": 200,
        }
    return {"message": f"{formatted_player_name} not found.", "status": 404}
