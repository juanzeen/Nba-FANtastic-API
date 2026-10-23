from pydantic import BaseModel
from typing import Literal


class StatsFilters(BaseModel):
    stat: Literal["pts", "ast", "reb", "stl", "blk"] | None = None
    position: Literal["guard", "forward", "center"] | None = None
    period: Literal["season", "career"] | None = "career"
    order: Literal["asc", "desc"] | None = None


class HistoricalStatsFilters(BaseModel):
    stat: Literal["pts", "ast", "reb", "stl", "blk", "championships"] | None = None
    position: Literal["guard", "forward", "center"] | None = None
    order: Literal["asc", "desc"] | None = None


class TeamFilters(BaseModel):
    stat: (
        Literal[
            "pts",
            "ast",
            "reb",
            "stl",
            "blk",
            "championships",
            "power-rank",
            "league-rank",
        ]
        | None
    ) = None
    order: Literal["asc", "desc"] | None = None
