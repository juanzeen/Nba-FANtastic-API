from pydantic import BaseModel
from typing import TypedDict, Optional


class DetailsDict(TypedDict):
    season: Optional[str]
    team: Optional[str]


class HistoricalRecord(BaseModel):
    _id: str
    record: str
    value: int | float
    leader_full_name: str
    leader_id: int
    is_active: bool
    details: DetailsDict
