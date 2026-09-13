from fastapi import APIRouter, Depends, Path, HTTPException, Query
from typing import Annotated
from ..dependencies import DbDependency, RedisDependency
from ..utils.cache import get_cached_or_db
from ..schemas.nba_players import Player
from ..schemas.player_seasons import PlayerSeason
from ..schemas.base import (
    ResponseDict,
    ErrorResponseDict,
    PaginationResponse,
    PaginationParams,
)
import math

router = APIRouter(prefix="/players", tags=["Current NBA Players"])


@router.get(
    "/",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Actual NBA players not found.",
        }
    },
)
async def get_nba_players(
    pagination: Annotated[PaginationParams, Query()], db: DbDependency
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


@router.get(
    "/{id}",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Actual NBA player with id xx not found.",
        }
    },
)
async def get_nba_player_by_id(
    id: Annotated[
        int, Path(gt=10, lt=10000000, title="ID from the player who will be fetched")
    ],
    db: DbDependency,
) -> ResponseDict[Player] | ErrorResponseDict:
    np = db["players"]
    player = await np.find_one({"_id": id})
    if player:
        return {"message": "Player successfully retrieved.", "data": player}
    raise HTTPException(
        status_code=404, detail={"message": f"Player with id {id} not found."}
    )


@router.get(
    "/search/{slug}",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Actual NBA player with slug xxx-xxxx not found.",
        }
    },
)
async def get_nba_player_by_slug(
    slug: Annotated[
        str,
        Path(
            min_length=7,
            title="Slug from the player who will be fetched",
            description="Slug in the format name-lastname",
        ),
    ],
    db: DbDependency,
) -> ResponseDict[Player] | ErrorResponseDict:
    np = db["players"]
    player = await np.find_one({"slug": slug})
    if player:
        return {"message": "Player successfully retrieved.", "data": player}
    raise HTTPException(
        status_code=404, detail={"message": f"Player with slug {slug} not found."}
    )


# Seasons
@router.get(
    "/{player_id}/seasons",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Seasons from player with id xx not found.",
        }
    },
)
async def get_nba_player_seasons(
    player_id: Annotated[
        int, Path(gt=10, lt=10000000, title="ID from the player who will be fetched.")
    ],
    pagination: Annotated[PaginationParams, Query()],
    db: DbDependency,
) -> PaginationResponse[PlayerSeason] | ErrorResponseDict:
    ps = db["players_seasons"]
    limit = pagination.limit
    skip = limit * (pagination.page - 1)
    total_seasons = await ps.count_documents({"player_id": player_id})
    total_pages = math.ceil(total_seasons / limit)
    cursor = ps.find({"player_id": player_id}).sort("_id", 1).skip(skip).limit(limit)
    seasons = await cursor.to_list()

    if seasons and len(seasons) > 0:
        return {
            "message": f"Seasons from player with id {player_id} successfully retrieved.",
            "data": seasons,
            "pagination": {
                "page": pagination.page,
                "limit": pagination.limit,
                "total_items": total_seasons,
                "total_pages": total_pages,
                "has_next": pagination.page < total_pages,
                "has_previous": pagination.page > 1,
            },
        }

    raise HTTPException(
        status_code=404,
        detail={"message": f"Seasons from player with id {player_id} not found."},
    )


@router.get(
    "/{player_id}/seasons/{season_year}",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Season xxxx-xx from player with id xx not found.",
        }
    },
)
async def get_nba_player_season_by_year(
    player_id: Annotated[
        int, Path(gt=10, lt=10000000, title="ID from the player who will be fetched.")
    ],
    season_year: Annotated[
        str,
        Path(
            min_length=7,
            max_length=7,
            title="ID from the season which will be fetched.",
        ),
    ],
    db: DbDependency,
    redis: RedisDependency,
) -> ResponseDict[PlayerSeason] | ErrorResponseDict:
    ps = db["players_seasons"]
    season = await get_cached_or_db(
        redis=redis,
        cache_key=f"players:{player_id}:seasons:{season_year}",
        fetch_from_db=ps.find_one({"player_id": player_id, "season_year": season_year}),
    )
    if season:
        return {
            "message": f"Season {season_year} from player with id {player_id} successfully retrieved.",
            "data": season,
        }
    raise HTTPException(
        status_code=404,
        detail={
            "message": f"Season {season_year} from player with id {player_id} not found."
        },
    )


@router.get(
    "/team/{team_abb}",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Players from team XXX not found.",
        }
    },
)
async def get_players_by_team(
    team_abb: Annotated[
        str,
        Path(
            min_length=3,
            max_length=3,
            title="Abbreviation from the team which will have players retrived",
        ),
    ],
    db: DbDependency,
    redis: RedisDependency,
) -> ResponseDict[list[Player]] | ErrorResponseDict:
    np = db["players"]
    normalized_abb = team_abb.upper()
    cursor = np.find({"team.abbreviation": normalized_abb}).sort("full_name", 1)
    players = await get_cached_or_db(
        redis=redis,
        cache_key=f"players:team:{normalized_abb}",
        fetch_from_db=cursor.to_list(),
    )
    if players and len(players) > 0:
        return {
            "message": f"Players from {normalized_abb} successfully retrieved.",
            "data": players,
        }
    raise HTTPException(
        status_code=404,
        detail={"message": f"Players from {normalized_abb} not found."},
    )
