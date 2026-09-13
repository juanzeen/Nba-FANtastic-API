from fastapi import APIRouter, Path, HTTPException
from typing import Annotated
from ..dependencies import DbDependency, RedisDependency
from ..utils.cache import get_cached_or_db
from ..schemas.historical_records import HistoricalRecord
from ..schemas.base import ResponseDict, ErrorResponseDict

router = APIRouter(prefix="/historical-records", tags=["Historical Records"])


@router.get(
    "/",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Historical records not found.",
        }
    },
)
async def get_historical_records(
    db: DbDependency,
    redis: RedisDependency
) -> ResponseDict[list[HistoricalRecord]] | ErrorResponseDict:
    hr = db["historical_records"]
    records = await get_cached_or_db(redis=redis, cache_key="historical_records", fetch_from_db=hr.find({}, {"_id": 0}).to_list())
    if records and len(records) > 0:
        return {
            "message": "Historical records successfully retrieved.",
            "data": records,
        }
    raise HTTPException(
        status_code=404, detail={"message": "Historical records not found."}
    )


@router.get(
    "/{category}",
    status_code=200,
    responses={
        404: {
            "model": ErrorResponseDict,
            "description": "Historical record with category xxxx not found.",
        }
    },
)
async def get_historical_record_by_category(
    category: Annotated[
        str,
        Path(
            max_length=13,
            min_length=8,
            title="Specific category to be retrieved from DB",
        ),
    ],
    db: DbDependency,
    redis: RedisDependency
) -> ResponseDict[HistoricalRecord] | ErrorResponseDict:
    hr = db["historical_records"]
    db_function = hr.find_one({"record": category}, {"_id": 0})
    record = await get_cached_or_db(redis=redis, cache_key=f"historical_records:{category}", fetch_from_db=db_function)
    if record:
        return {
            "message": f"Historical record {category} successfully retrieved.",
            "data": record,
        }
    raise HTTPException(
        status_code=404, detail={"message": f"Historical record {category} not found."}
    )
