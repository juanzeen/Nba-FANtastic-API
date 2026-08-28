from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Annotated
from ..dependencies import get_db
from ..schemas.players import Player

router = APIRouter(prefix="/players", tags=["Current NBA Players"])


@router.get("/", status_code=200)
async def get_nba_players(db=Depends(get_db)) -> list[Player]:
    np = db["players"]
    players = await np.find().to_list()
    if players and len(players) > 0:
        return {
            "message": "Actual NBA players successfully retrieved.",
            "data": players,
        }
    raise HTTPException(
        status_code=404, detail={"message": "Actual NBA players not found."}
    )


@router.get("/{id}", status_code=200)
async def get_nba_player_by_id(
    id: Annotated[
        int, Path(max_length=7, title="ID from the player who will be fetched")
    ],
    db=Depends(get_db),
) -> Player:
    np = db["players"]
    player = await np.find_one({"_id": id})
    if player:
        return {"message": "Player successfully retrieved.", "data": player}
    raise HTTPException(
        status_code=404, detail={"message": f"Player with id: {id} not found."}
    )
