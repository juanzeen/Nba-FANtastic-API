from fastapi import APIRouter, Depends, Path, HTTPException, Query
from typing import Annotated
from ..dependencies import get_db
from ..schemas.nba_players import Player
from ..schemas.pagination import PaginationResponse, PaginationParams
from ..schemas.contants import ResponseDict, ErrorResponseDict
import math

router = APIRouter(prefix="/players", tags=["Current NBA Players"])


@router.get("/", status_code=200)
async def get_nba_players(
    pagination: Annotated[PaginationParams, Query()], db=Depends(get_db)
) -> PaginationResponse[Player] | ErrorResponseDict:
    np = db["players"]
    limit = pagination.limit
    skip = limit * (pagination.page - 1)
    total_players = await np.count_documents({})
    total_pages = math.ceil(total_players / limit)
    cursor = np.find({}).sort("_id", 1).skip(skip).limit(limit)
    players = await cursor.to_list()
    if players and len(players) > 0:
        return {
            "message": "Actual NBA players successfully retrieved.",
            "data": players,
            "pagination": {
                "page": pagination.page,
                "limit": pagination.limit,
                "total_items": total_players,
                "total_pages": total_pages,
                "has_next": pagination.page < total_pages,
                "has_previous": pagination.page > 1,
            },
        }
    raise HTTPException(
        status_code=404, detail={"message": "Actual NBA players not found."}
    )


@router.get("/{id}", status_code=200)
async def get_nba_player_by_id(
    id: Annotated[
        int, Path(gt=10, lt=10000000, title="ID from the player who will be fetched")
    ],
    db=Depends(get_db),
) -> ResponseDict[Player] | ErrorResponseDict:
    np = db["players"]
    player = await np.find_one({"_id": id})
    if player:
        return {"message": "Player successfully retrieved.", "data": player}
    raise HTTPException(
        status_code=404, detail={"message": f"Player with id: {id} not found."}
    )
