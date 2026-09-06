from typing import TypedDict, Annotated, Optional
from pydantic import BaseModel, StringConstraints, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class Peak(TypedDict):
    value: int
    game_id: int
    opponent: str
    date: str


class TotalsStats(TypedDict):
    games_played: int
    pts: int
    ast: int
    reb: int
    blk: int
    stl: int


class AvgStats(TypedDict):
    pts: float
    ast: float
    reb: float
    blk: float
    stl: float


class SeasonPeaks(TypedDict):
    max_pts: Peak
    max_ast: Peak
    max_reb: Peak
    max_stl: Peak
    max_blk: Peak


class Team(TypedDict):
    abbreviation: Annotated[str, StringConstraints(max_length=3)]
    name: str


class PerformanceVsTeams(TypedDict):
    team: str
    games_played: int
    avg_pts: float
    avg_ast: float
    avg_reb: float
    avg_blk: float
    avg_stl: float


class Games(TypedDict):
    game_id: int
    date: str
    opponent: str
    result: str
    is_home: bool
    playoffs: bool
    minutes: str
    pts: int
    ast: int
    reb: int
    stl: int
    blk: int
    fg_pct: float
    fg3_pct: float
    ft_pct: float


class PlayerSeason(BaseModel):
    id: PyObjectId = Field(default=None, alias="_id")
    player_id: int
    season_year: str
    team: Team
    season_totals: TotalsStats
    season_averages: AvgStats
    season_peaks: SeasonPeaks
    performance_vs_teams: list[PerformanceVsTeams]
    games: list[Games]
