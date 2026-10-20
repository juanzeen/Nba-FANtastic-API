from pydantic import BaseModel, BeforeValidator, Field
from typing import TypedDict, Optional, Annotated, Literal

PyObjectId = Annotated[int, BeforeValidator(int)]


class LabelsFilter(BaseModel):
    label: (
        Literal["points", "rebounds", "assists", "blocks", "steals", "3pm", "fg", "gp"]
        | None
    ) = None


class DetailsDict(TypedDict):
    season: Optional[str]
    team: Optional[str]


class HistoricalRecord(BaseModel):
    id: PyObjectId = Field(default=None, alias="_id")
    record: str
    title: str
    label: str
    value: int | float
    leader_full_name: str
    leader_id: int
    is_active: bool
    details: DetailsDict
