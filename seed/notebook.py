import pandas as pd
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, playerawards

# This file is used to test nba_api endpoint and static functions.
# If you only want to seed your database, ignore this notebook.

def convert_to_cm(fi: str) -> float:
  feet, inch = fi.split("-")
  height_cm = round((int(feet) * 30.48) + (int(inch) * 2.54))
  return height_cm

def notebook():
    all_players_data = players.get_players()
    active_players = [p for p in all_players_data if p["is_active"]][:15] #530 players
    for p in active_players:
      id = p.get("id")
      full_name = p.get("full_name")
      try:
        common_df = commonplayerinfo.CommonPlayerInfo(player_id=p.get("id")).get_data_frames()[0]
        is_nba_active = True if common_df['ROSTERSTATUS'].iloc[0] == 'Active' else False
        if is_nba_active:
          p_pos = common_df['POSITION'].iloc[0]
          #TODO add these stats to historical players
          p_country = common_df['COUNTRY'].iloc[0]
          p_height = convert_to_cm(common_df['HEIGHT'].iloc[0])
          p_weight = round(int(common_df['WEIGHT'].iloc[0])/2.205, 2)
          #TODO
          team_abb = common_df['TEAM_ABBREVIATION'].iloc[0]
          team_full_name = f"{common_df['TEAM_CITY'].iloc[0]} {common_df['TEAM_NAME'].iloc[0]}"
          career_df = playercareerstats.PlayerCareerStats(player_id=p.get("id")).get_data_frames()[0]
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
          obj = {
          "id": id,
          "full_name": full_name,
          "position": p_pos,
          "country": p_country,
          "weight": p_weight,
          "height": p_height,
          "team": {"abbreviation": team_abb, "name": team_full_name},
          "career": {
            "totals": {"games": total_games, "points": total_points, "assists": total_assists, "rebounds": total_rebounds,"blocks": total_blocks, "steals": total_steals},
            "avg": { "points": avg_points, "assists": avg_assists, "rebounds": avg_rebounds,"blocks": avg_blocks, "steals": avg_steals}
          },
          "season": {
            "totals": {"games": None, "points": None,  "assists": None, "rebounds": None, "blocks": None, "steals": None,},
            "avg": { "points": None , "assists": None , "rebounds": None ,"blocks": None , "steals": None }
          }
        }
          print(obj)
        time.sleep(1.5)

      except Exception as e:
        print(e)

notebook()
