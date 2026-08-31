from typing import TypedDict, Annotated, Optional
from pydantic import BaseModel, StringConstraints, BeforeValidator, Field

PyObjectId = Annotated[int, BeforeValidator(int)]


class TotalsStats(TypedDict):
    games: int
    points: int
    assists: int
    rebounds: int
    blocks: int
    steals: int


class AvgStats(TypedDict):
    points: float
    assists: float
    rebounds: float
    blocks: float
    steals: float


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
    career: TotalsAvg
    season: Optional[TotalsAvg]
    team: Team
