from fastapi import APIRouter, Path, HTTPException
from typing import Annotated
from ..dependencies import DbDependency
#from ..utils.cache import get_cached_or_db
from ..schemas.teams import Team
from ..schemas.base import ResponseDict, ErrorResponseDict

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
    db: DbDependency
) -> ResponseDict[list[Team]] | ErrorResponseDict:
    tc = db["teams"]
    teams = await tc.find({}).to_list()
    if teams and len(teams) > 0:
        return {
            "message": "Teams successfully retrieved.",
            "data": teams,
        }
    raise HTTPException(
        status_code=404, detail={"message": "Teams not found."}
    )


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
    raise HTTPException(
        status_code=404, detail={"message": f"Team {abb} not found."}
    )
