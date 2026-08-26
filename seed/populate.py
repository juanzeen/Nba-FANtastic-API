import math
import os
import time
import dotenv
import pandas as pd
from pymongo import MongoClient
from nba_api.stats.endpoints import playercareerstats


def get_db_collection(collection_name: str = "historical_players"):
    """Initialize and return a MongoDB collection using environment variables."""
    dotenv.load_dotenv()
    db_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
    client = MongoClient(db_url)
    db = client[db_name]
    return db[collection_name]


def clean_float(val, default: float = 0.0, decimals: int = 1) -> float:
    """Safely convert any value to float rounded to specified decimals, handling NaNs/Infs."""
    if val is None or pd.isna(val):
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return round(f, decimals) if decimals is not None else f
    except (ValueError, TypeError):
        return default


def clean_int(val, default: int = 0) -> int:
    """Safely convert any value to integer, handling NaNs and floats."""
    if val is None or pd.isna(val):
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return int(f)
    except (ValueError, TypeError):
        return default


def clean_str(val, default: str = "") -> str:
    """Safely convert any value to trimmed string, handling NaNs."""
    if val is None or pd.isna(val):
        return default
    s = str(val).strip()
    return default if s.lower() == "nan" else s


def build_season_dict(
    season_year,
    team,
    games_played,
    pts,
    ast,
    reb,
    blk,
    stl,
) -> dict:
    """Format season record into the standard fix_seasons_structure format."""
    return {
        "season_year": clean_str(season_year, default="Unknown"),
        "team": clean_str(team, default="UNK"),
        "games_played": clean_int(games_played, default=0),
        "pts_avg": clean_float(pts, default=0.0, decimals=1),
        "ast_avg": clean_float(ast, default=0.0, decimals=1),
        "reb_avg": clean_float(reb, default=0.0, decimals=1),
        "blk_avg": clean_float(blk, default=0.0, decimals=1),
        "stl_avg": clean_float(stl, default=0.0, decimals=1),
    }


def normalize_season_item(season_item: dict) -> dict:
    """Convert and clean a season entry (legacy nested or flat) into standard format."""
    if not isinstance(season_item, dict):
        return build_season_dict("Unknown", "UNK", 0, 0, 0, 0, 0, 0)

    # Legacy nested format: {"1990-91": {"team": "CHI", "games_played": 82, ...}}
    if len(season_item.keys()) == 1 and "season_year" not in season_item:
        season_year = list(season_item.keys())[0]
        data = season_item[season_year]
        if not isinstance(data, dict):
            data = {}
    else:
        season_year = season_item.get("season_year", "Unknown")
        data = season_item

    team = data.get("team", "UNK")
    games_played = data.get("games_played", 0)

    averages = data.get("averages")
    if isinstance(averages, dict):
        pts = averages.get("pts", averages.get("pts_avg", data.get("pts_avg", data.get("pts", 0))))
        ast = averages.get("ast", averages.get("ast_avg", data.get("ast_avg", data.get("ast", 0))))
        reb = averages.get("reb", averages.get("reb_avg", data.get("reb_avg", data.get("reb", 0))))
        blk = averages.get("blk", averages.get("blk_avg", data.get("blk_avg", data.get("blk", 0))))
        stl = averages.get("stl", averages.get("stl_avg", data.get("stl_avg", data.get("stl", 0))))
    else:
        pts = data.get("pts_avg", data.get("pts", 0))
        ast = data.get("ast_avg", data.get("ast", 0))
        reb = data.get("reb_avg", data.get("reb", 0))
        blk = data.get("blk_avg", data.get("blk", 0))
        stl = data.get("stl_avg", data.get("stl", 0))

    return build_season_dict(
        season_year=season_year,
        team=team,
        games_played=games_played,
        pts=pts,
        ast=ast,
        reb=reb,
        blk=blk,
        stl=stl,
    )


def populate_historical_players():
    """Populate base historical player profiles from CSV into MongoDB."""
    file_path = "nba_legends.csv"

    if not os.path.exists(file_path):
        print("CSV file not found!")
        return
    collection = get_db_collection("historical_players")

    df_legends = pd.read_csv(file_path)
    print(f"Starting migration of {len(df_legends)} legends to MongoDB ({file_path})...")

    for _, row in df_legends.iterrows():
        player_id = clean_int(row.get("Player ID"))
        if not player_id:
            continue
        full_name = clean_str(row.get("Full Name"))

        try:
            document = {
                "_id": player_id,
                "full_name": full_name,
                "position": clean_str(row.get("Position"), default="UNK"),
                "is_active": False,
                "career_span": clean_str(row.get("Career Span")),
                "career_totals": {
                    "games_played": clean_int(row.get("Total Games")),
                    "pts": clean_int(row.get("Total Points")),
                    "ast": clean_int(row.get("Total Assists")),
                    "reb": clean_int(row.get("Total Rebounds")),
                    "blk": clean_int(row.get("Total Blocks")),
                    "stl": clean_int(row.get("Total Steals")),
                },
                "career_peaks": {
                    "max_ppg": {
                        "value": clean_float(row.get("Peak PPG")),
                        "season": clean_str(row.get("Peak PPG Season")),
                    },
                    "max_apg": {
                        "value": clean_float(row.get("Peak APG")),
                        "season": clean_str(row.get("Peak APG Season")),
                    },
                    "max_rpg": {
                        "value": clean_float(row.get("Peak RPG")),
                        "season": clean_str(row.get("Peak RPG Season")),
                    },
                    "max_bpg": {
                        "value": clean_float(row.get("Peak BPG")),
                        "season": clean_str(row.get("Peak BPG Season")),
                    },
                    "max_spg": {
                        "value": clean_float(row.get("Peak SPG")),
                        "season": clean_str(row.get("Peak SPG Season")),
                    },
                },
                "honors": {
                    "mvps": clean_int(row.get("MVPs")),
                    "finals_mvps": clean_int(row.get("Finals MVPs")),
                    "all_stars": clean_int(row.get("All-Star Appearances")),
                },
            }

            collection.update_one(
                {"_id": player_id},
                {
                    "$set": document,
                    "$setOnInsert": {"seasons": []},
                },
                upsert=True,
            )

            print(f"Document saved in MongoDB: {full_name} (ID: {player_id})")

        except Exception as e:
            print(f"Error processing {full_name} for MongoDB: {e}")
            continue


def populate_historical_players_seasons():
    """Fetch season-by-season stats from NBA API for each legend and save formatted seasons."""
    file_path = "nba_legends.csv"

    if not os.path.exists(file_path):
        print("CSV file not found!")
        return
    collection = get_db_collection("historical_players")

    df_legends = pd.read_csv(file_path)
    players = df_legends["Player ID"].dropna().unique().tolist()
    print(f"Starting season updates for {len(players)} players...")

    for player_id in players:
        player_id = clean_int(player_id)
        if not player_id:
            continue

        try:
            player_info = playercareerstats.PlayerCareerStats(
                player_id=player_id
            ).get_data_frames()[0]
            seasons = []

            if not player_info.empty:
                for _, row in player_info.iterrows():
                    gp = clean_int(row.get("GP"), default=0)
                    pts = (row["PTS"] / gp) if gp > 0 and "PTS" in row and pd.notna(row["PTS"]) else 0.0
                    ast = (row["AST"] / gp) if gp > 0 and "AST" in row and pd.notna(row["AST"]) else 0.0
                    reb = (row["REB"] / gp) if gp > 0 and "REB" in row and pd.notna(row["REB"]) else 0.0
                    blk = (row["BLK"] / gp) if gp > 0 and "BLK" in row and pd.notna(row["BLK"]) else 0.0
                    stl = (row["STL"] / gp) if gp > 0 and "STL" in row and pd.notna(row["STL"]) else 0.0

                    season_data = build_season_dict(
                        season_year=row.get("SEASON_ID"),
                        team=row.get("TEAM_ABBREVIATION"),
                        games_played=gp,
                        pts=pts,
                        ast=ast,
                        reb=reb,
                        blk=blk,
                        stl=stl,
                    )
                    seasons.append(season_data)

            collection.update_one(
                {"_id": player_id},
                {"$set": {"seasons": seasons}},
                upsert=True,
            )
            print(
                f"Seasons for player {player_id} successfully updated in MongoDB ({len(seasons)} seasons)."
            )
            time.sleep(1)

        except Exception as e:
            print(f"Error exporting seasons for player {player_id}: {e}")


def fix_seasons_structure():
    """Correct and clean the seasons array across all historical player records in MongoDB."""
    collection = get_db_collection("historical_players")
    print("Starting correction and cleanup of 'seasons' array...")

    players = collection.find({})
    updated_count = 0

    for player in players:
        player_id = player.get("_id")
        old_seasons = player.get("seasons", [])
        if not isinstance(old_seasons, list):
            old_seasons = []

        new_seasons = [normalize_season_item(season_item) for season_item in old_seasons]

        collection.update_one({"_id": player_id}, {"$set": {"seasons": new_seasons}})
        updated_count += 1

    print(
        f"\n✨ Success! {updated_count} players had their seasons corrected and cleaned of NaN values."
    )


populate_historical_players()
populate_historical_players_seasons()
