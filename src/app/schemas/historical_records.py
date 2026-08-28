from pydantic import BaseModel
from typing import Annotated, TypedDict


class DetailsDict(TypedDict):
    season: str
    team: str


class HistoricalRecord(BaseModel):
    record: str
    value: int | float
    leader_full_name: str
    leader_id: int
    is_active: bool
    details: DetailsDict
