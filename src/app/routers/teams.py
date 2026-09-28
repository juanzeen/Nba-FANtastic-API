from fastapi import APIRouter, Path, HTTPException, Query
from typing import Annotated
from ..dependencies import DbDependency

# from ..utils.cache import get_cached_or_db
from ..schemas.teams import Team
from ..schemas.base import (
    ResponseDict,
    ErrorResponseDict,
    PaginationParams,
    PaginationResponse,
)
import math

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get(
    "/",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Teams not found.",
        }
    },
)
async def get_teams(
    pagination: Annotated[PaginationParams, Query()], db: DbDependency
) -> PaginationResponse[Team] | ErrorResponseDict:
    tc = db["teams"]
    limit = pagination.limit
    skip = limit * (pagination.page - 1)
    total_teams = await tc.count_documents({})
    total_pages = math.ceil(total_teams / limit)
    cursor = (
        tc.find({}).sort("last_season.power_ranking.rank", 1).skip(skip).limit(limit)
    )
    teams = await cursor.to_list()
    if teams and len(teams) > 0:
        return {
            "message": "Teams successfully retrieved.",
            "data": teams,
            "pagination": {
                "page": pagination.page,
                "limit": pagination.limit,
                "total_items": total_teams,
                "total_pages": total_pages,
                "has_next": pagination.page < total_pages,
                "has_previous": pagination.page > 1,
            },
        }
    raise HTTPException(status_code=404, detail={"message": "Teams not found."})


@router.get(
    "/{id}",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Team with ID xxxx not found.",
        }
    },
)
async def get_team_by_id(
    id: Annotated[
        int,
        Path(
            gt=999999999,
            title="Specific id to be retrieved from DB",
        ),
    ],
    db: DbDependency,
) -> ResponseDict[Team] | ErrorResponseDict:
    tc = db["teams"]
    team = await tc.find_one({"_id": id})
    if team:
        return {
            "message": f"Team with id {id} successfully retrieved.",
            "data": team,
        }
    raise HTTPException(
        status_code=404, detail={"message": f"Team with id {id} not found."}
    )


@router.get("/search/{abb}/")
async def get_team_by_abbreviation(
    abb: Annotated[
        str,
        Path(
            max_length=3,
            min_length=3,
            title="Abbreviation from the team which'll be retrieved.",
        ),
    ],
    db: DbDependency,
) -> ResponseDict[Team] | ErrorResponseDict:
    tc = db["teams"]
    team = await tc.find_one({"abbreviation": abb})
    if team:
        return {
            "message": f"Team {abb} successfully retrieved.",
            "data": team,
        }
    raise HTTPException(status_code=404, detail={"message": f"Team {abb} not found."})
