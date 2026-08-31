from fastapi import APIRouter, Query, Path, Depends, HTTPException
from typing import Annotated, Optional, TypedDict
from ..dependencies import get_db
from ..schemas.historical_players import HistoricalPlayer
from ..schemas.pagination import PaginationParams, PaginationResponse
from ..schemas.contants import ResponseDict, ErrorResponseDict
from ..utils.strings import format_player_name
import math

router = APIRouter(prefix="/historical-players", tags=["Historical Players"])

@router.get("/", status_code=200, response_model=PaginationResponse[HistoricalPlayer])
async def get_historical_players(
    pagination: Annotated[PaginationParams, Query()],
    db=Depends(get_db)
) -> PaginationResponse[HistoricalPlayer] | ErrorResponseDict:
    hp = db["historical_players"]
    limit = pagination.limit
    skip = (pagination.page - 1) * limit
    total_players = await hp.count_documents({})
    total_pages = math.ceil(total_players/limit)
    cursor = hp.find({}).sort("_id", 1).skip(skip).limit(limit)
    players = await cursor.to_list()
    if not players:
        raise HTTPException(
            status_code=404, detail={"message": "No historical players found."}
        )

    return {
        "message": "Historical players successfully retrieved.",
        "pagination": {
            "page": pagination.page,
            "limit": pagination.limit,
            "total_items": total_players,
            "total_pages": total_pages,
            "has_next": pagination.page < total_pages,
            "has_previous": pagination.page > 1
        },
        "data": players
    }

@router.get("/{id_or_slug}", status_code=200)
async def get_historical_player_by_id(
    id_or_slug: Annotated[
        int, Path(ge=10, lt=1000000, title="_id from the player who will be fetched")
    ] | Annotated[str, Path(min_length=3, title="Slug from the player who will be fetched")],
    db=Depends(get_db),
) -> ResponseDict | ErrorResponseDict:
    hp = db["historical_players"]
    player = await hp.find_one({"_id": id_or_slug})
    if player:
        return {
            "data": player,
            "message": "Player successfully retrieved.",
        }

    raise HTTPException(
        status_code=404, detail={"message": f"Player with id {id_or_slug} not found."}
    )
