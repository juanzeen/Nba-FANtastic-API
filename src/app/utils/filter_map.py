PLAYERS_SEASON_MAP = {
    "pts": "season.totals.points",
    "ast": "season.totals.assists",
    "reb": "season.totals.rebounds",
    "stl": "season.totals.steals",
    "blk": "season.totals.blocks",
}

PLAYERS_CAREER_MAP = {
    "pts": "career.totals.points",
    "ast": "career.totals.assists",
    "reb": "career.totals.rebounds",
    "stl": "career.totals.steals",
    "blk": "career.totals.blocks",
}

HISTORICAL_PLAYERS_MAP = {
    "pts": "career_totals.pts",
    "ast": "career_totals.ast",
    "reb": "career_totals.reb",
    "stl": "career_totals.stl",
    "blk": "career_totals.blk",
    "championships": "honors.championships",
}

TEAMS_MAP = {
    "pts": "actual_season.metrics.pts_per_game",
    "ast": "actual_season.metrics.ast_per_game",
    "reb": "actual_season.metrics.reb_per_game",
    "stl": "actual_season.metrics.stl_per_game",
    "blk": "actual_season.metrics.blk_per_game",
    "championships": "championships",
    "power-rank": "actual_season.power_ranking.rank",
    "league-rank": "actual_season.rank",
}


def get_filter_key(requested_from: str, stat: str, period: str = "career") -> str:
    if not stat:
        return "_id"

    if requested_from == "players" and period == "season":
        return PLAYERS_SEASON_MAP.get(stat)

    if requested_from == "players" and period == "career":
        return PLAYERS_CAREER_MAP.get(stat)

    if requested_from == "historical_players":
        return HISTORICAL_PLAYERS_MAP.get(stat)

    if requested_from == "teams":
        return TEAMS_MAP.get(stat)
