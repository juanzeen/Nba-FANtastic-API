from fastapi import FastAPI, Query, Depends, HTTPException
from typing import Annotated
from pymongo import AsyncMongoClient
import os
import dotenv
from app.utils.strings import format_player_name

dotenv.load_dotenv()

app = FastAPI()
db_url = os.getenv("MONGO_URL")
db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
client = AsyncMongoClient(db_url)


def get_client():
    return client


def get_db():
    return client[db_name]


@app.get("/", status_code=200)
async def health_check(client: AsyncMongoClient = Depends(get_client)):
    health_status = {
        "status": "healthy",
        "services": {"api": "healthy", "database": "unknown"},
    }

    try:
        ping = await client.admin.command("ping")
        if ping:
            health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["services"]["error"] = str(e)
        health_status["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_status)

    return health_status


@app.get("/historical-players", status_code=200)
async def get_historical_players(db=Depends(get_db)):
    hp = db["historical_players"]
    players = await hp.find().to_list()
    if players is None or len(players) == 0:
        raise HTTPException(
            status_code=404, detail={"message": "No historical players found."}
        )

    return {
        "message": "Historical players successfully retrieved.",
        "players": players,
    }


@app.get("/historical-players/{id}", status_code=200)
async def get_historical_player_by_id(id: int, db=Depends(get_db)):
    hp = db["historical_players"]
    player = await hp.find_one({"_id": id})
    print(player)
    if player:
        return {
            "player": player,
            "message": "Player successfully retrieved.",
        }

    raise HTTPException(
        status_code=404, detail={"message": f"Player with {id} not found."}
    )


@app.get("/historical-players/", status_code=200)
async def get_historical_player_by_name(
    name: Annotated[
        str,
        Query(
            min_length=2,
            description="Player name to search for. Can be used with last_name or with hyphen to search for the full name. Eg: 'LeBron' or 'LeBron-James'",
        ),
    ],
    last_name: Annotated[
        str,
        Query(
            description="Expected be used for specific cases and must be used with capitalized letter at the start of the last name. Eg: 'James"
        ),
    ] = "",
    db=Depends(get_db),
):
    hp = db["historical_players"]
    formatted_player_name = format_player_name(name, last_name)
    player = await hp.find_one({"full_name": formatted_player_name})
    if player:
        return {
            "player": player,
            "message": "Player successfully retrieved.",
        }
    raise HTTPException(
        status_code=404,
        detail={"message": f"Player with name {formatted_player_name} not found."},
    )
