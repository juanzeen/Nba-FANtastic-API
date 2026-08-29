from typing import TypedDict, Annotated
from pydantic import BaseModel, StringConstraints


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
    _id: int
    full_name: str
    height: int
    weight: float
    position: str
    country: str
    career: TotalsAvg
    season: TotalsAvg
    team: Team
