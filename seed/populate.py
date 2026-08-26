import os
import time
import pandas as pd
from pymongo import MongoClient
from nba_api.stats.endpoints import playercareerstats
import math
import dotenv


def populate_historical_players():
    dotenv.load_dotenv()
    db_url = os.getenv("LOCAL_MONGO_URL")
    db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
    client = MongoClient(db_url)
    db = client[db_name]
    collection = db["historical_players"]

    file_name = "nba_legends_normalized.csv"
    if not pd.io.common.file_exists(file_name):
        print("Arquivo CSV não encontrado!")
        return

    df_legends = pd.read_csv(file_name)
    print(f"Iniciando a migração de {len(df_legends)} lendas para o MongoDB...")

    for _, row in df_legends.iterrows():
        player_id = int(row["Player ID"])
        full_name = row["Full Name"]

        try:
            document = {
                "_id": player_id,
                "full_name": full_name,
                "position": row["Position"],
                "is_active": False,
                "career_span": str(row["Career Span"]),
                "career_totals": {
                    "games_played": int(row["Total Games"]),
                    "pts": int(row["Total Points"]),
                    "ast": int(row["Total Assists"]),
                    "reb": int(row["Total Rebounds"]),
                    "blk": int(row["Total Blocks"]),
                    "stl": int(row["Total Steals"]),
                },
                "career_peaks": {
                    "max_ppg": {
                        "value": float(row["Peak PPG"]),
                        "season": str(row["Peak PPG Season"]),
                    },
                    "max_apg": {
                        "value": float(row["Peak APG"]),
                        "season": str(row["Peak APG Season"]),
                    },
                    "max_rpg": {
                        "value": float(row["Peak RPG"]),
                        "season": str(row["Peak RPG Season"]),
                    },
                    "max_bpg": {
                        "value": float(row["Peak BPG"]),
                        "season": str(row["Peak BPG Season"]),
                    },
                    "max_spg": {
                        "value": float(row["Peak SPG"]),
                        "season": str(row["Peak SPG Season"]),
                    },
                },
                "honors": {
                    "mvps": int(row["MVPs"]),
                    "finals_mvps": int(row["Finals MVPs"]),
                    "all_stars": int(row["All-Star Appearances"]),
                },
                "seasons": [],
            }

            collection.update_one({"_id": player_id}, {"$set": document}, upsert=True)

            print(f"Documento salvo no MongoDB: {full_name}")

        except Exception as e:
            print(f"Erro ao processar {full_name} para o Mongo: {e}")
            continue


def populate_historical_players_seasons():
    dotenv.load_dotenv()
    db_url = os.getenv("MONGO_URL")
    client = MongoClient(db_url)
    db = client["nba_fantastic"]
    collection = db["historical_players"]

    file_name = "nba_legends.csv"
    if not pd.io.common.file_exists(file_name):
        print("Arquivo CSV não encontrado!")
        return

    df_legends = pd.read_csv(file_name)
    players = df_legends["Player ID"].to_list()

    for player_id in players:
        try:
            player_info = playercareerstats.PlayerCareerStats(
                player_id=player_id
            ).get_data_frames()[0]
            seasons = []

            for _, row in player_info.iterrows():
                gp = row["GP"] if pd.notna(row["GP"]) else 0

                pts_avg = (
                    round(float(row["PTS"] / gp), 1)
                    if gp > 0 and pd.notna(row["PTS"])
                    else 0.0
                )
                ast_avg = (
                    round(float(row["AST"] / gp), 1)
                    if gp > 0 and pd.notna(row["AST"])
                    else 0.0
                )
                reb_avg = (
                    round(float(row["REB"] / gp), 1)
                    if gp > 0 and pd.notna(row["REB"])
                    else 0.0
                )
                blk_avg = (
                    round(float(row["BLK"] / gp), 1)
                    if gp > 0 and "BLK" in row and pd.notna(row["BLK"])
                    else 0.0
                )
                stl_avg = (
                    round(float(row["STL"] / gp), 1)
                    if gp > 0 and "STL" in row and pd.notna(row["STL"])
                    else 0.0
                )

                season_data = {
                    "season_year": str(row["SEASON_ID"]),
                    "team": str(row["TEAM_ABBREVIATION"])
                    if "TEAM_ABBREVIATION" in row
                    else "UNK",
                    "games_played": int(gp),
                    "pts_avg": pts_avg,
                    "ast_avg": ast_avg,
                    "reb_avg": reb_avg,
                    "blk_avg": blk_avg,
                    "stl_avg": stl_avg,
                }
                seasons.append(season_data)

            collection.update_one(
                {"_id": player_id}, {"$set": {"seasons": seasons}}, upsert=True
            )
            print(
                f"Temporadas do jogador {player_id} atualizadas com sucesso no MongoDB."
            )
            time.sleep(1)

        except Exception as e:
            print(f"Erro ao exportar temporadas do jogador: {player_id} | {e}")


def fix_seasons_structure():
    dotenv.load_dotenv()
    db_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DATABASE_NAME", "nba_fantastic")
    client = MongoClient(db_url)
    db = client[db_name]
    collection = db["historical_players"]
    print("Iniciando a correção e limpeza do array 'seasons'...")

    players = collection.find({})
    updated_count = 0

    for player in players:
        player_id = player["_id"]
        old_seasons = player.get("seasons", [])
        new_seasons = []

        has_changes = False

        for season_item in old_seasons:
            if (
                isinstance(season_item, dict)
                and len(season_item.keys()) == 1
                and "season_year" not in season_item
            ):
                season_year = list(season_item.keys())[0]
                inner_data = season_item[season_year]

                team = inner_data.get("team", "UNK")
                games_played = inner_data.get("games_played", 0)

                averages = inner_data.get("averages", inner_data)

                pts = averages.get("pts", 0)
                ast = averages.get("ast", 0)
                reb = averages.get("reb", 0)
                blk = averages.get("blk", 0)
                stl = averages.get("stl", 0)

                has_changes = True
            else:
                season_year = season_item.get("season_year", "Unknown")
                team = season_item.get("team", "UNK")
                games_played = season_item.get("games_played", 0)

                averages = season_item.get("averages", season_item)
                pts = averages.get("pts", 0)
                ast = averages.get("ast", 0)
                reb = averages.get("reb", 0)
                blk = averages.get("blk", 0)
                stl = averages.get("stl", 0)

            def clean_value(val):
                if val is None:
                    return 0.0
                if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                    return 0.0
                try:
                    return float(val)
                except ValueError, TypeError:
                    return 0.0

            cleaned_season = {
                "season_year": str(season_year),
                "team": str(team),
                "games_played": int(games_played) if games_played is not None else 0,
                "pts_avg": round(clean_value(pts), 1),
                "ast_avg": round(clean_value(ast), 1),
                "reb_avg": round(clean_value(reb), 1),
                "blk_avg": round(clean_value(blk), 1),
                "stl_avg": round(clean_value(stl), 1),
            }

            new_seasons.append(cleaned_season)
        collection.update_one({"_id": player_id}, {"$set": {"seasons": new_seasons}})
        updated_count += 1

    print(
        f"\nSucesso! {updated_count} jogadores tiveram suas temporadas corrigidas e limpas de valores NaN."
    )


populate_historical_players_seasons()
