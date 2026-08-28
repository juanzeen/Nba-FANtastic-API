from fastapi import APIRouter, Depends, Path
from pymongo import AsyncMongoClient
from pydantic import BaseModel
from typing import Annotated
from ..dependencies import get_db
from ..schemas.historical_records import HistoricalRecord

router = APIRouter(prefix="/historical-records", tags=["Historical Records"])


@router.get("/", status_code=200)
async def get_historical_records(db=Depends(get_db)) -> list[HistoricalRecord]:
    hr = db["historical_records"]
    records = await hr.find({}, {"_id": 0}).to_list()
    if records and len(records) > 0:
        return {
            "message": "Historical records successfully retrieved.",
            "data": records,
        }
    return {"message": "Historical records not found.", "data": None}


@router.get("/{category}", status_code=200)
async def get_historical_record(
    category: Annotated[
        str,
        Path(
            max_length=13,
            min_length=8,
            title="Specific category to be retrieved from DB",
        ),
    ],
    db=Depends(get_db),
) -> HistoricalRecord:
    hr = db["historical_records"]
    record = await hr.find_one({"record": category}, {"_id": 0})
    if record:
        return {
            "message": f"Historical record {category} successfully retrieved.",
            "data": record,
        }
    return {"message": "Historical record not found.", "data": None}
