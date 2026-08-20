import dotenv
import os
import time
import pandas as pd
from pymongo import MongoClient
from nba_api.stats.endpoints import playercareerstats

def populate_historical_players():
    # Load environment variables from .env file
    dotenv.load_dotenv()
    db_url = os.getenv("MONGO_URL")
    client = MongoClient(db_url)
    db = client["nba_fantastic"] # Nome do seu banco
    collection = db["historical_players"]

    file_name = "nba_legends_normalized.csv"
    if not pd.io.common.file_exists(file_name):
        print("Arquivo CSV não encontrado!")
        return

    df_legends = pd.read_csv(file_name)
    print(f"Iniciando a migração de {len(df_legends)} lendas para o MongoDB...")

    for _, row in df_legends.iterrows():
        player_id = int(row['Player ID'])
        full_name = row['Full Name']

        try:

            document = {
                "_id": player_id,
                "full_name": full_name,
                "position": row['Position'],
                "is_active": False,
                "career_span": str(row['Career Span']),
                "career_totals": {
                    "games_played": int(row['Total Games']),
                    "pts": int(row['Total Points']),
                    "ast": int(row['Total Assists']),
                    "reb": int(row['Total Rebounds']),
                    "blk": int(row['Total Blocks']),
                    "stl": int(row['Total Steals'])
                },
                "career_peaks": {
                    "max_ppg": { "value": float(row['Peak PPG']), "season": str(row['Peak PPG Season']) },
                    "max_apg": { "value": float(row['Peak APG']), "season": str(row['Peak APG Season']) },
                    "max_rpg": { "value": float(row['Peak RPG']), "season": str(row['Peak RPG Season']) },
                    "max_bpg": { "value": float(row['Peak BPG']), "season": str(row['Peak BPG Season']) },
                    "max_spg": { "value": float(row['Peak SPG']), "season": str(row['Peak SPG Season']) }
                },
                "honors": {
                    "mvps": int(row['MVPs']),
                    "finals_mvps": int(row['Finals MVPs']),
                    "all_stars": int(row['All-Star Appearances'])
                },
                "seasons": []
            }

            # 5. Salva no MongoDB usando Upsert (se já existir, atualiza; se não, cria)
            collection.update_one(
                {"_id": player_id},
                {"$set": document},
                upsert=True
            )

            print(f"🚀 Documento salvo no MongoDB: {full_name}")

        except Exception as e:
            print(f"⚠️ Erro ao processar {full_name} para o Mongo: {e}")
            continue

def populate_historical_players_seasons():
    dotenv.load_dotenv()
    db_url = os.getenv("MONGO_URL")
    client = MongoClient(db_url)
    db = client["nba_fantastic"]
    collection = db["historical_players"]

    file_name = "nba_legends_normalized.csv"
    if not pd.io.common.file_exists(file_name):
        print("Arquivo CSV não encontrado!")
        return

    df_legends = pd.read_csv(file_name)
    players = df_legends['Player ID'].to_list()
    for id in players:
        try:
            player_info = playercareerstats.PlayerCareerStats(player_id=id).get_data_frames()[0]
            seasons = []
            for _, row in player_info.iterrows():
                season_data = {
                    "pts_avg": round(float(row['PTS'] / row['GP'] if row['GP'] > 0 else 0), 1),
                    "ast_avg": round(float(row['AST'] / row['GP'] if row['GP'] > 0 else 0), 1),
                    "reb_avg": round(float(row['REB'] / row['GP'] if row['GP'] > 0 else 0), 1),
                    "blk_avg": round(float(row['BLK'] / row['GP'] if row['GP'] > 0 and not row['BLK'] == None else 0), 1),
                    "stl_avg": round(float(row['STL'] / row['GP'] if row['GP'] > 0 and not row['STL'] == None else 0), 1),
                    "games_played": row['GP'],
                }
                seasons.append({row['SEASON_ID']: season_data})
            doc = {
                "_id": id,
                "seasons": seasons
            }
            collection.update_one(
                            {"_id": id},
                            {"$set": doc},
                            upsert=True
                        )
            print(f"Temporadas do jogador {id} exportadas com sucesso para o MongoDB.")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao exportar temporadas do jogador: {id} | {e}")




populate_historical_players_seasons()
