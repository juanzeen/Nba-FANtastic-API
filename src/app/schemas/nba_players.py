from typing import TypedDict, Annotated, Optional
from pydantic import BaseModel, StringConstraints, BeforeValidator, Field

PyObjectId = Annotated[int, BeforeValidator(int)]


class TotalsStats(TypedDict):
    games: Optional[int]
    points: Optional[int]
    assists: Optional[int]
    rebounds: Optional[int]
    blocks: Optional[int]
    steals: Optional[int]


class AvgStats(TypedDict):
    points: Optional[float]
    assists: Optional[float]
    rebounds: Optional[float]
    blocks: Optional[float]
    steals: Optional[float]


class Team(TypedDict):
    abbreviation: Annotated[str, StringConstraints(max_length=3)]
    name: str


class TotalsAvg(TypedDict):
    totals: TotalsStats
    avg: AvgStats


class Player(BaseModel):
    id: PyObjectId = Field(default=None, alias="_id")
    full_name: str
    slug: str
    height: int
    position: str
    country: str
    career_span: str
    career: TotalsAvg
    season: TotalsAvg
    team: Team
