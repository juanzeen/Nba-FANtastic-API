from nba_api.stats.static import players
from nba_api.stats.endpoints import (
    playercareerstats,
    playerawards,
    commonplayerinfo,
    alltimeleadersgrids,
)
import pandas as pd
import time
import csv
import os

def normalize_name(name: str):
    return name.lower().replace("-", "").replace("'", "")

def is_legendary_player(
    points, rebs, asts, mvp_count, all_star_participations, finals_mvp_count, min_games
) -> bool:
    volume_conditions = (
        points >= 25000 or rebs >= 8000 or asts >= 7000
    ) and min_games >= 460
    peak_conditions = (
        mvp_count > 1 or all_star_participations > 5 or finals_mvp_count > 0
    )
    return volume_conditions or peak_conditions


def convert_to_cm(fi: str) -> float:
    feet, inch = fi.split("-")
    height_cm = round((int(feet) * 30.48) + (int(inch) * 2.54))
    return height_cm


def extract_legendary_players():
    file_name = "nba_legends.csv"
    headers = [
        "Player ID",
        "Full Name",
        "Total Games",
        "Total Points",
        "Total Rebounds",
        "Total Assists",
        "MVPs",
        "Finals MVPs",
        "All-Star Appearances",
    ]
    file_exists = os.path.isfile(file_name)
    all_players_data = players.get_players()
    retired = [p for p in all_players_data if not p["is_active"]]
    processed_ids = set()
    if file_exists:
        with open(file_name, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_ids.add(row["Player ID"])
    print(f"Jogadores já processados: {len(processed_ids)}")

    print(f"Total de jogadores aposentados para processar: {len(retired)}")

    with open(file_name, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()

        for p in retired:
            player_id = p["id"]
            if player_id in processed_ids:
                continue

            name = p["full_name"]

            try:
                career = playercareerstats.PlayerCareerStats(player_id=player_id)
                career_stats = career.get_data_frames()[0]
                awards = playerawards.PlayerAwards(player_id=player_id)
                df_awards = awards.get_data_frames()[0]
                time.sleep(1.5)

                total_points = int(career_stats["PTS"].sum())
                total_rebs = int(career_stats["REB"].sum())
                total_asts = int(career_stats["AST"].sum())
                total_games = int(career_stats["GP"].sum())

                season_mvps = len(
                    df_awards[df_awards["DESCRIPTION"] == "NBA Most Valuable Player"]
                )
                finals_mvps = len(
                    df_awards[
                        df_awards["DESCRIPTION"] == "NBA Finals Most Valuable Player"
                    ]
                )
                all_star_apps = len(
                    df_awards[df_awards["DESCRIPTION"] == "NBA All-Star"]
                )

                if is_legendary_player(
                    total_points,
                    total_rebs,
                    total_asts,
                    season_mvps,
                    all_star_apps,
                    finals_mvps,
                    total_games,
                ):
                    print(f"Lenda adicionada: {name}")
                    writer.writerow(
                        {
                            "Player ID": player_id,
                            "Full Name": name,
                            "Total Games": total_games,
                            "Total Points": total_points,
                            "Total Rebounds": total_rebs,
                            "Total Assists": total_asts,
                            "MVPs": season_mvps,
                            "Finals MVPs": finals_mvps,
                            "All-Star Appearances": all_star_apps,
                        }
                    )
                    f.flush()

            except Exception as e:
                print(f"Erro ao processar {name}: {e}")
                continue

    file_name = "nba_legends.csv"
    if not pd.io.common.file_exists(file_name):
        print("Arquivo nba_legends.csv não encontrado!")
        return

    df_existing = pd.read_csv(file_name)
    player_ids = df_existing["Player ID"].astype(str).tolist()

    print(
        f"Atualizando {len(player_ids)} lendas com Steals, Blocks e Picos de Temporada..."
    )

    updated_legends = []

    for player_id in player_ids:
        row_data = df_existing[df_existing["Player ID"] == player_id].iloc[0]
        full_name = row_data["Full Name"]

        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            df_career = career.get_data_frames()[0]

            if df_career.empty:
                continue

            df_career = df_career[df_career["GP"] > 0].copy()
            total_games = int(df_career["GP"].sum())
            total_points = int(df_career["PTS"].sum())
            total_rebs = int(df_career["REB"].sum())
            total_asts = int(df_career["AST"].sum())
            total_stl = int(df_career["STL"].sum() if "STL" in df_career.columns else 0)
            total_blk = int(df_career["BLK"].sum() if "BLK" in df_career.columns else 0)

            df_career["PPG"] = df_career["PTS"] / df_career["GP"]
            df_career["APG"] = df_career["AST"] / df_career["GP"]
            df_career["RPG"] = df_career["REB"] / df_career["GP"]
            df_career["SPG"] = (
                df_career["STL"] / df_career["GP"] if "STL" in df_career.columns else 0
            )
            df_career["BPG"] = (
                df_career["BLK"] / df_career["GP"] if "BLK" in df_career.columns else 0
            )

            max_ppg = df_career.loc[df_career["PPG"].idxmax()]
            max_rpg = df_career.loc[df_career["RPG"].idxmax()]
            max_apg = df_career.loc[df_career["APG"].idxmax()]
            max_spg = (
                df_career.loc[df_career["SPG"].idxmax()]
                if "STL" in df_career.columns
                else None
            )
            max_bpg = (
                df_career.loc[df_career["BPG"].idxmax()]
                if "BLK" in df_career.columns
                else None
            )

            mvps = row_data["MVPs"]
            finals_mvps = row_data["Finals MVPs"]
            all_stars = row_data["All-Star Appearances"]

            updated_legends.append(
                {
                    "Player ID": player_id,
                    "Full Name": full_name,
                    "Total Games": total_games,
                    "Total Points": total_points,
                    "Total Rebounds": total_rebs,
                    "Total Assists": total_asts,
                    "Total Steals": total_stl,
                    "Total Blocks": total_blk,
                    "MVPs": mvps,
                    "Finals MVPs": finals_mvps,
                    "All-Star Appearances": all_stars,
                    "Peak PPG": round(max_ppg["PPG"], 1),
                    "Peak PPG Season": max_ppg["SEASON_ID"],
                    "Peak RPG": round(max_rpg["RPG"], 1),
                    "Peak RPG Season": max_rpg["SEASON_ID"],
                    "Peak APG": round(max_apg["APG"], 1),
                    "Peak APG Season": max_apg["SEASON_ID"],
                    "Peak SPG": round(max_spg["SPG"], 1) if max_spg is not None else 0,
                    "Peak SPG Season": max_spg["SEASON_ID"]
                    if max_spg is not None
                    else "N/A",
                    "Peak BPG": round(max_bpg["BPG"], 1) if max_bpg is not None else 0,
                    "Peak BPG Season": max_bpg["SEASON_ID"]
                    if max_bpg is not None
                    else "N/A",
                }
            )

            print(f"Atualizado: {full_name}")
            time.sleep(1.5)

        except Exception as e:
            print(f"Erro ao atualizar {full_name}: {e}")
            updated_legends.append(row_data.to_dict())
            continue

    if updated_legends:
        df_new = pd.DataFrame(updated_legends)
        df_new.to_csv(file_name, index=False)
        print(
            f"\nSucesso! O arquivo '{file_name}' foi totalmente atualizado com as novas estatísticas e picos."
        )


def update_legends_career_data(file_name="nba_legends.csv"):
    """
    Centralized function to update NBA legends data with complete career statistics,
    season peaks (PPG, RPG, APG, SPG, BPG), career span, total seasons, and position.
    """
    if not os.path.exists(file_name):
        print(f"Arquivo '{file_name}' não encontrado.")
        return

    df = pd.read_csv(file_name)
    all_player_ids = df["Player ID"].tolist()

    print(
        f"Iniciando a atualização completa para {len(all_player_ids)} jogadores a partir de '{file_name}'..."
    )

    stat_cols = ["PTS", "REB", "AST", "GP", "STL", "BLK"]

    for player_id in all_player_ids:
        player_matches = df[df["Player ID"].astype(str) == str(player_id)]
        if player_matches.empty:
            continue
        idx = player_matches.index[0]
        full_name = df.at[idx, "Full Name"]

        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
            awards = playerawards.PlayerAwards(player_id=player_id)
            df_career = career.get_data_frames()[0]
            df_info = info.get_data_frames()[0]
            df_awards = awards.get_data_frames()[0]

            if df_career.empty:
                print(f"No career data for {full_name}")
                continue

            for col in stat_cols:
                if col not in df_career.columns:
                    df_career[col] = 0

            df_career = df_career[df_career["GP"] > 0].copy()
            if df_career.empty:
                print(f"No valid games for {full_name}")
                continue

            total_seasons = int(df_career["SEASON_ID"].nunique())
            career_span = (
                f"{df_career['SEASON_ID'].min()} - {df_career['SEASON_ID'].max()}"
            )

            total_games = int(df_career["GP"].sum())
            total_points = int(df_career["PTS"].sum())
            total_rebs = int(df_career["REB"].sum())
            total_asts = int(df_career["AST"].sum())
            total_stl = int(df_career["STL"].sum())
            total_blk = int(df_career["BLK"].sum())

            season_mvps = len(
                df_awards[df_awards["DESCRIPTION"] == "NBA Most Valuable Player"]
            )
            finals_mvps = len(
                df_awards[df_awards["DESCRIPTION"] == "NBA Finals Most Valuable Player"]
            )
            all_star_apps = len(df_awards[df_awards["DESCRIPTION"] == "NBA All-Star"])

            df_career["PPG"] = df_career["PTS"] / df_career["GP"]
            df_career["APG"] = df_career["AST"] / df_career["GP"]
            df_career["RPG"] = df_career["REB"] / df_career["GP"]
            df_career["SPG"] = df_career["STL"] / df_career["GP"]
            df_career["BPG"] = df_career["BLK"] / df_career["GP"]

            max_ppg = df_career.loc[df_career["PPG"].idxmax()]
            max_rpg = df_career.loc[df_career["RPG"].idxmax()]
            max_apg = df_career.loc[df_career["APG"].idxmax()]
            max_spg = df_career.loc[df_career["SPG"].idxmax()]
            max_bpg = df_career.loc[df_career["BPG"].idxmax()]

            df.at[idx, "Total Games"] = total_games
            df.at[idx, "Total Points"] = total_points
            df.at[idx, "Total Rebounds"] = total_rebs
            df.at[idx, "Total Assists"] = total_asts
            df.at[idx, "Total Steals"] = total_stl
            df.at[idx, "Total Blocks"] = total_blk

            df.at[idx, "MVPs"] = season_mvps
            df.at[idx, "Finals MVPs"] = finals_mvps
            df.at[idx, "All-Star Appearances"] = all_star_apps

            df.at[idx, "Peak PPG"] = round(float(max_ppg["PPG"]), 1)
            df.at[idx, "Peak PPG Season"] = max_ppg["SEASON_ID"]
            df.at[idx, "Peak RPG"] = round(float(max_rpg["RPG"]), 1)
            df.at[idx, "Peak RPG Season"] = max_rpg["SEASON_ID"]
            df.at[idx, "Peak APG"] = round(float(max_apg["APG"]), 1)
            df.at[idx, "Peak APG Season"] = max_apg["SEASON_ID"]
            df.at[idx, "Peak SPG"] = (
                round(float(max_spg["SPG"]), 1) if max_spg["SPG"] > 0 else 0.0
            )
            df.at[idx, "Peak SPG Season"] = (
                max_spg["SEASON_ID"] if max_spg["SPG"] > 0 else "N/A"
            )
            df.at[idx, "Peak BPG"] = (
                round(float(max_bpg["BPG"]), 1) if max_bpg["BPG"] > 0 else 0.0
            )
            df.at[idx, "Peak BPG Season"] = (
                max_bpg["SEASON_ID"] if max_bpg["BPG"] > 0 else "N/A"
            )

            df.at[idx, "Total Seasons"] = total_seasons
            df.at[idx, "Career Span"] = career_span

            position = ""
            if not df_info.empty and "POSITION" in df_info.columns:
                pos_val = df_info["POSITION"].iloc[0]
                if pd.notna(pos_val) and str(pos_val).strip() != "":
                    position = str(pos_val).strip()

            if position:
                df.at[idx, "Position"] = position

            slug = df_info["PLAYER_SLUG"].iloc[0]
            country = df_info["COUNTRY"].iloc[0]
            height = convert_to_cm(df_info["HEIGHT"].iloc[0])
            df.at[idx, "Player Slug"] = slug
            df.at[idx, "Country"] = country
            df.at[idx, "Height"] = height

            print(f"Atualizado: {slug} ({country} | {height}cm)")
            time.sleep(2)

        except Exception as e:
            print(f"Erro ao processar {full_name} (ID: {player_id}): {e}")
            continue

    df.to_csv("nba_legends_updated.csv", index=False)
    print(
        f"\nSucesso! O arquivo nba_legends.csv foi totalmente atualizado contemplando todas as colunas."
    )


def get_all_time_leaders():
    endpoints = [
        alltimeleadersgrids.AllTimeLeadersGrids().ast_leaders,
        alltimeleadersgrids.AllTimeLeadersGrids().blk_leaders,
        alltimeleadersgrids.AllTimeLeadersGrids().fg3_m_leaders,
        alltimeleadersgrids.AllTimeLeadersGrids().fgm_leaders,
        alltimeleadersgrids.AllTimeLeadersGrids().g_p_leaders,
        alltimeleadersgrids.AllTimeLeadersGrids().pts_leaders,
        alltimeleadersgrids.AllTimeLeadersGrids().reb_leaders,
        alltimeleadersgrids.AllTimeLeadersGrids().stl_leaders,
    ]
    leaders = []
    for f in endpoints:
        try:
            current_leaders = f.get_dict()
            record_obj = {
                "category": current_leaders.get("headers")[2],
                "value": current_leaders.get("data")[0][2],
                "leader_id": current_leaders.get("data")[0][0],
                "leader_full_name": current_leaders.get("data")[0][1],
                "active": current_leaders.get("data")[0][4],
            }
            print(record_obj)
            leaders.append(record_obj)
        except Exception as e:
            print(e)
    pd.DataFrame(leaders).to_csv("all_time_leaders.csv", index=False)


def extract_current_nba_players():
    all_players_data = players.get_players()
    active_players = [p for p in all_players_data if p["is_active"]]  # 530 players
    file_name = "nba_players.csv"
    headers = [
        "ID",
        "Full Name",
        "Country",
        "Weight",
        "Height",
        "Position",
        "Team Abbreviation",
        "Team Full Name",
        "Total Games",
        "Total Points",
        "Total Assists",
        "Total Rebounds",
        "Total Blocks",
        "Total Steals",
        "Avg Points",
        "Avg Rebounds",
        "Avg Assists",
        "Avg Blocks",
        "Avg Steals",
        "Season Games",
        "Season Points",
        "Season Assists",
        "Season Rebounds",
        "Season Blocks",
        "Season Steals",
        "Season Avg Points",
        "Season Avg Rebounds",
        "Season Avg Assists",
        "Season Avg Blocks",
        "Season Avg Steals",
    ]
    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not os.path.isfile(file_name):
            writer.writeheader()
        for p in active_players:
            id = p.get("id")
            full_name = p.get("full_name")
            try:
                common_df = commonplayerinfo.CommonPlayerInfo(
                    player_id=p.get("id")
                ).get_data_frames()[0]
                is_nba_active = (
                    True if common_df["ROSTERSTATUS"].iloc[0] == "Active" else False
                )
                if is_nba_active:
                    print(f"Extracting {full_name} with ID: {id}")
                    p_pos = common_df["POSITION"].iloc[0]
                    p_country = common_df["COUNTRY"].iloc[0]
                    p_height = convert_to_cm(common_df["HEIGHT"].iloc[0])
                    p_weight = round(int(common_df["WEIGHT"].iloc[0]) / 2.205, 2)
                    team_abb = common_df["TEAM_ABBREVIATION"].iloc[0]
                    team_full_name = f"{common_df['TEAM_CITY'].iloc[0]} {common_df['TEAM_NAME'].iloc[0]}"
                    career_df = playercareerstats.PlayerCareerStats(
                        player_id=p.get("id")
                    ).get_data_frames()[0]
                    total_games = int(career_df["GP"].sum())
                    total_points = int(career_df["PTS"].sum())
                    total_assists = int(career_df["AST"].sum())
                    total_rebounds = int(career_df["REB"].sum())
                    total_steals = int(career_df["STL"].sum())
                    total_blocks = int(career_df["BLK"].sum())
                    avg_points = round(total_points / total_games, 1)
                    avg_assists = round(total_assists / total_games, 1)
                    avg_rebounds = round(total_rebounds / total_games, 1)
                    avg_steals = round(total_steals / total_games, 1)
                    avg_blocks = round(total_blocks / total_games, 1)
                    row = {
                        "ID": id,
                        "Full Name": full_name,
                        "Position": p_pos,
                        "Country": p_country,
                        "Weight": p_weight,
                        "Height": p_height,
                        "Team Abbreviation": team_abb,
                        "Team Full Name": team_full_name,
                        "Total Games": total_games,
                        "Total Points": total_points,
                        "Total Assists": total_assists,
                        "Total Rebounds": total_rebounds,
                        "Total Blocks": total_blocks,
                        "Total Steals": total_steals,
                        "Avg Points": avg_points,
                        "Avg Assists": avg_assists,
                        "Avg Rebounds": avg_rebounds,
                        "Avg Blocks": avg_blocks,
                        "Avg Steals": avg_steals,
                        "Season Games": None,
                        "Season Points": None,
                        "Season Assists": None,
                        "Season Rebounds": None,
                        "Season Blocks": None,
                        "Season Avg Points": None,
                        "Season Avg Assists": None,
                        "Season Avg Rebounds": None,
                        "Season Avg Blocks": None,
                        "Season Avg Steals": None,
                    }
                    writer.writerow(row)
                time.sleep(1.5)

            except Exception as e:
                print(e)

def append_player_slug_actual_players():
    df = pd.read_csv("nba_players.csv")
    ids = df["ID"].tolist()
    for id in ids:
        player_matches = df[df["ID"].astype(str) == str(id)]
        if player_matches.empty:
            continue
        idx = player_matches.index[0]
        full_name = df.at[idx, "Full Name"]
        array = full_name.split(" ")
        normalized = [normalize_name(n) for n in array]
        slug = "-".join(normalized)
        print(f"Adding slug for {full_name} | {slug} ")
        df.at[idx, "Player Slug"] = slug
    df.to_csv("nba_players.csv", index=False)

append_player_slug_actual_players()
