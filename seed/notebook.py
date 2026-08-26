import pandas as pd
from nba_api.stats.static import players


def find_record_leaders_info():
    players_to_find_id = ["Mark Eaton", "Alvin Robertson", "Scott Skiles", "Elmore Smith", "Klay Thompson", "Larry Kenon", "Kendall Gill"]
    for p in players_to_find_id:
        try:
            player_id = players.find_players_by_full_name(p)[0].get("id")
            print(player_id)
        except Exception as e:
            print(e)
