from fastapi import FastAPI, Query
from typing import Annotated
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
            "player": player,
            "message": "Player successfully retrieved.",
            "status": 200,
        }
    return {"message": f"Player with {id} not found.", "status": 404}


@app.get("/historical-players/")
async def get_historical_player_by_name(
    name: Annotated[str, Query(min_length=2, description="Player name to search for. Can be used with last_name or with hyphen to search for the full name. Eg: 'LeBron' or 'LeBron-James'")],
    last_name: Annotated[
        str,
        Query(
            description="Expected be used for specific cases and must be used with capitalized letter at the start of the last name. Eg: 'James"
        ),
    ] = "",
):
    hp = db["historical_players"]
    formatted_player_name = format_player_name(name, last_name)
    player = await hp.find_one({"full_name": formatted_player_name})
    if player:
        return {
            "player": player,
            "message": "Player successfully retrieved.",
            "status": 200,
        }
    return {"message": f"{formatted_player_name} not found.", "status": 404}
