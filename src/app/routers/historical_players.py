from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Annotated, Optional
from ..dependencies import get_db
from ..utils.strings import format_player_name

router = APIRouter(prefix="/historical-players", tags=["Historical Players"])


@router.get("/", status_code=200)
async def get_historical_players(
    name: Annotated[
        Optional[str],
        Query(
            min_length=2,
            description="Player name to search for. Can be used with last_name or with hyphen. Eg: 'LeBron' or 'LeBron-James'",
        ),
    ] = None,
    last_name: Annotated[
        str,
        Query(
            description="Expected to be used for specific cases with capitalized last name. Eg: 'James'"
        ),
    ] = "",
    db=Depends(get_db),
):
    hp = db["historical_players"]

    if name:
        formatted_player_name = format_player_name(name, last_name)
        player = await hp.find_one({"full_name": formatted_player_name})

        if not player:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"Player with name {formatted_player_name} not found."
                },
            )

        return {
            "player": player,
            "message": "Player successfully retrieved.",
        }

    players = await hp.find().to_list()
    if not players:
        raise HTTPException(
            status_code=404, detail={"message": "No historical players found."}
        )

    return {
        "players": players,
        "message": "Historical players successfully retrieved.",
    }


@router.get("/{id}", status_code=200)
async def get_historical_player_by_id(id: int, db=Depends(get_db)):
    hp = db["historical_players"]
    player = await hp.find_one({"_id": id})
    if player:
        return {
            "player": player,
            "message": "Player successfully retrieved.",
        }

    raise HTTPException(
        status_code=404, detail={"message": f"Player with id {id} not found."}
    )
