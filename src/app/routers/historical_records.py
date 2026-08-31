from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Annotated
from ..dependencies import get_db
from ..schemas.historical_records import HistoricalRecord
from ..schemas.contants import ResponseDict, ErrorResponseDict

router = APIRouter(prefix="/historical-records", tags=["Historical Records"])


@router.get("/", status_code=200)
async def get_historical_records(
    db=Depends(get_db),
) -> ResponseDict[list[HistoricalRecord]] | ErrorResponseDict:
    hr = db["historical_records"]
    records = await hr.find({}, {"_id": 0}).to_list()
    if records and len(records) > 0:
        return {
            "message": "Historical records successfully retrieved.",
            "data": records,
        }
    raise HTTPException(
        status_code=404, detail={"message": "Historical records not found."}
    )


@router.get("/{category}", status_code=200)
async def get_historical_record_by_category(
    category: Annotated[
        str,
        Path(
            max_length=13,
            min_length=8,
            title="Specific category to be retrieved from DB",
        ),
    ],
    db=Depends(get_db),
) -> ResponseDict[HistoricalRecord] | ErrorResponseDict:
    hr = db["historical_records"]
    record = await hr.find_one({"record": category}, {"_id": 0})
    if record:
        return {
            "message": f"Historical record {category} successfully retrieved.",
            "data": record,
        }
    raise HTTPException(
        status_code=404, detail={"message": f"Historical record {category} not found."}
    )
