from fastapi import APIRouter, Query, Path, Depends, HTTPException
from typing import Annotated, Optional, TypedDict
from ..dependencies import get_db
from ..schemas.historical_players import HistoricalPlayer
from ..schemas.base import (
    ResponseDict,
    ErrorMessage,
    ErrorResponseDict,
    PaginationParams,
    PaginationResponse,
)
from ..utils.strings import format_player_name
import math

router = APIRouter(prefix="/historical-players", tags=["Historical Players"])


@router.get("/", status_code=200, responses={
    404:{
        "model": ErrorResponseDict,
        "description": "Historical players not found."
     }
})
async def get_historical_players(
    pagination: Annotated[PaginationParams, Query()], db=Depends(get_db)
) -> PaginationResponse[HistoricalPlayer] | ErrorResponseDict:
    hp = db["historical_players"]
    limit = pagination.limit
    skip = (pagination.page - 1) * limit
    total_players = await hp.count_documents({})
    total_pages = math.ceil(total_players / limit)
    cursor = hp.find({}).sort("_id", 1).skip(skip).limit(limit)
    players = await cursor.to_list()
    if not players:
        raise HTTPException(
            status_code=404, detail={"message": "Historical players not found."}
        )

    return {
        "message": "Historical players successfully retrieved.",
        "pagination": {
            "page": pagination.page,
            "limit": pagination.limit,
            "total_items": total_players,
            "total_pages": total_pages,
            "has_next": pagination.page < total_pages,
            "has_previous": pagination.page > 1,
        },
        "data": players,
    }


@router.get("/{id}", status_code=200, responses={
    404:{
        "model": ErrorResponseDict,
        "description": "Historical player with id xx not found."
     }
})
async def get_historical_player_by_id(
    id: Annotated[
        int, Path(ge=10, lt=1000000, title="_id from the player who will be fetched")
    ],
    db=Depends(get_db),
) -> ResponseDict[HistoricalPlayer] | ErrorResponseDict:
    hp = db["historical_players"]
    player = await hp.find_one({"_id": id})
    if player:
        return {
            "data": player,
            "message": "Player successfully retrieved.",
        }

    raise HTTPException(
        status_code=404, detail={"message": f"Player with id {id} not found."}
    )


@router.get("/search/{slug}", status_code=200, responses={
    404:{
        "model": ErrorResponseDict,
        "description": "Historical player with slug xxxx-xxxx not found."
     }
})
async def get_historical_player_by_slug(
    slug: Annotated[
        str,
        Path(
            min_length=8,
            title="Slug of the player who will be fetched.",
            description="Slug must be in the format name-lastname",
        ),
    ],
    db=Depends(get_db),
):
    hp = db["historical_players"]
    player = await hp.find_one({"slug": slug})
    if player:
        return {
            "data": player,
            "message": "Player successfully retrieved.",
        }

    raise HTTPException(
        status_code=404, detail={"message": f"Player with slug {slug} not found."}
    )
