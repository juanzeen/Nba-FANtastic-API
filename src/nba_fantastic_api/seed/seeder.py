from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats, playerawards, commonplayerinfo
import pandas as pd
import time
import csv
import os

def is_legendary_player(points, rebs, asts, mvp_count, all_star_participations, finals_mvp_count, min_games) -> bool:
    # Ajustado conforme sua lógica
    volume_conditions = (points >= 25000 or rebs >= 8000 or asts >= 7000) and min_games >= 460
    peak_conditions = (mvp_count > 1 or all_star_participations > 5 or finals_mvp_count > 0)
    return volume_conditions or peak_conditions

def extract_legendary_players():
    file_name = "nba_legends.csv"
    headers = ["Player ID", "Full Name", "Total Games", "Total Points", "Total Rebounds", "Total Assists", "MVPs", "Finals MVPs", "All-Star Appearances"]
    file_exists = os.path.isfile(file_name)
    all_players_data = players.get_players()
    retired = [p for p in all_players_data if not p['is_active']]
    processed_ids = set()
    if file_exists:
        with open(file_name, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_ids.add(row["Player ID"])
    print(f"Jogadores já processados: {len(processed_ids)}")

    print(f"Total de jogadores aposentados para processar: {len(retired)}")

    with open(file_name, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()

        for p in retired:
            player_id = p['id']
            if player_id in processed_ids:
                continue

            name = p['full_name']

            try:
                career = playercareerstats.PlayerCareerStats(player_id=player_id)
                career_stats = career.get_data_frames()[0]
                awards = playerawards.PlayerAwards(player_id=player_id)
                df_awards = awards.get_data_frames()[0]
                time.sleep(1.5)

                total_points = int(career_stats['PTS'].sum())
                total_rebs = int(career_stats['REB'].sum())
                total_asts = int(career_stats['AST'].sum())
                total_games = int(career_stats['GP'].sum())

                season_mvps = len(df_awards[df_awards['DESCRIPTION'] == 'NBA Most Valuable Player'])
                finals_mvps = len(df_awards[df_awards['DESCRIPTION'] == 'NBA Finals Most Valuable Player'])
                all_star_apps = len(df_awards[df_awards['DESCRIPTION'] == 'NBA All-Star'])

                if is_legendary_player(total_points, total_rebs, total_asts, season_mvps, all_star_apps, finals_mvps, total_games):
                    print(f"Lenda adicionada: {name}")
                    writer.writerow({
                        "Player ID": player_id, "Full Name": name, "Total Games": total_games,
                        "Total Points": total_points, "Total Rebounds": total_rebs,
                        "Total Assists": total_asts, "MVPs": season_mvps,
                        "Finals MVPs": finals_mvps, "All-Star Appearances": all_star_apps
                    })
                    f.flush()

            except Exception as e:
                print(f"⚠️ Erro ao processar {name}: {e}")
                continue
def get_legendary_players_max_avg():
    df = playercareerstats.PlayerCareerStats(player_id='76003').get_data_frames()[0]
    if df.empty or 'GP' not in df.columns:
        return None
    total_blocks = int(df['BLK'].sum())
    total_steals = int(df['STL'].sum())

    # Filtra apenas temporadas onde o jogador realmente jogou para evitar divisão por zero
    df = df[df['GP'] > 0].copy()

    if df.empty:
        return None

    # Calcula as médias por jogo para cada temporada individualmente
    df['PPG'] = df['PTS'] / df['GP']
    df['APG'] = df['AST'] / df['GP']
    df['RPG'] = df['REB'] / df['GP']
    df['BLK'] = df['BLK'] / df['GP']
    df['STL'] = df['STL'] / df['GP']

    # Encontra a linha (temporada) com a maior média de pontos (PPG)
    max_ppg_row = df.loc[df['PPG'].idxmax()]

    # Encontra a linha com a maior média de assistências (APG)
    max_apg_row = df.loc[df['APG'].idxmax()]
    max_reb_row = df.loc[df['RPG'].idxmax()]
    max_blk_row = df.loc[df['BLK'].idxmax()]
    max_stl_row = df.loc[df['STL'].idxmax()]
    peaks = {
        "steals": total_steals,
        "blocks": total_blocks,
        "max_ppg": {
            "value": round(max_ppg_row['PPG'], 1),
            "season": max_ppg_row['SEASON_ID'],
            "team": max_ppg_row['TEAM_ABBREVIATION']
        },
        "max_apg": {
            "value": round(max_apg_row['APG'], 1),
            "season": max_apg_row['SEASON_ID'],
            "team": max_apg_row['TEAM_ABBREVIATION']
        },
        "max_rpg": {
            "value": round(max_reb_row['RPG'], 1),
            "season": max_reb_row['SEASON_ID'],
            "team": max_reb_row['TEAM_ABBREVIATION']
        },
        "max_bpg": {
            "value": round(max_blk_row['BLK'], 1),
            "season": max_blk_row['SEASON_ID'],
            "team": max_blk_row['TEAM_ABBREVIATION']
        },
        "max_spg": {
            "value": round(max_stl_row['STL'], 1),
            "season": max_stl_row['SEASON_ID'],
            "team": max_stl_row['TEAM_ABBREVIATION']
        }

    }

    print(peaks)

def update_all_players_career_data():
    file_name = "nba_legends.csv"

    if not pd.io.common.file_exists(file_name):
        print(f"Arquivo {file_name} não encontrado.")
        return

    df = pd.read_csv(file_name)
    all_player_ids = df['Player ID'].tolist()

    print(f"Iniciando a atualização completa para {len(all_player_ids)} jogadores...")

    for player_id in all_player_ids:
        player_row = df[df['Player ID'].astype(str) == str(player_id)].iloc[0]
        full_name = player_row['Full Name']

        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            df_career = career.get_data_frames()[0]

            if df_career.empty:
                print(f"⚠️ Sem dados para {full_name}")
                continue

            # Tratamento blindado contra colunas vazias
            for col in ['PTS', 'REB', 'AST', 'GP', 'STL', 'BLK']:
                if col not in df_career.columns:
                    df_career[col] = 0
                else:
                    df_career[col] = pd.to_numeric(df_career[col], errors='coerce').fillna(0)

            df_career = df_career[df_career['GP'] > 0].copy()

            # --- CÁLCULO DO TEMPO DE CARREIRA ---
            total_seasons = int(df_career['SEASON_ID'].nunique())
            career_span = f"{df_career['SEASON_ID'].min()} - {df_career['SEASON_ID'].max()}"

            # Totais Gerais
            total_games = int(df_career['GP'].sum())
            total_points = int(df_career['PTS'].sum())
            total_rebs = int(df_career['REB'].sum())
            total_asts = int(df_career['AST'].sum())
            total_stl = int(df_career['STL'].sum())
            total_blk = int(df_career['BLK'].sum())

            # Médias por Temporada para os Picos (incluindo Steals e Blocks)
            df_career['PPG'] = df_career['PTS'] / df_career['GP']
            df_career['APG'] = df_career['AST'] / df_career['GP']
            df_career['RPG'] = df_career['REB'] / df_career['GP']
            df_career['SPG'] = df_career['STL'] / df_career['GP']
            df_career['BPG'] = df_career['BLK'] / df_career['GP']

            max_ppg = df_career.loc[df_career['PPG'].idxmax()]
            max_rpg = df_career.loc[df_career['RPG'].idxmax()]
            max_apg = df_career.loc[df_career['APG'].idxmax()]
            max_spg = df_career.loc[df_career['SPG'].idxmax()]
            max_bpg = df_career.loc[df_career['BPG'].idxmax()]

            idx = df[df['Player ID'].astype(str) == str(player_id)].index[0]

            # --- ATUALIZAÇÃO DE TODAS AS COLUNAS DO CSV ---
            df.at[idx, 'Total Games'] = total_games
            df.at[idx, 'Total Points'] = total_points
            df.at[idx, 'Total Rebounds'] = total_rebs
            df.at[idx, 'Total Assists'] = total_asts
            df.at[idx, 'Total Steals'] = total_stl
            df.at[idx, 'Total Blocks'] = total_blk

            # Mantém os prêmios que já estavam salvos no CSV original
            df.at[idx, 'MVPs'] = player_row['MVPs']
            df.at[idx, 'Finals MVPs'] = player_row['Finals MVPs']
            df.at[idx, 'All-Star Appearances'] = player_row['All-Star Appearances']

            # Picos de Carreira e Temporadas
            df.at[idx, 'Peak PPG'] = round(max_ppg['PPG'], 1)
            df.at[idx, 'Peak PPG Season'] = max_ppg['SEASON_ID']
            df.at[idx, 'Peak RPG'] = round(max_rpg['RPG'], 1)
            df.at[idx, 'Peak RPG Season'] = max_rpg['SEASON_ID']
            df.at[idx, 'Peak APG'] = round(max_apg['APG'], 1)
            df.at[idx, 'Peak APG Season'] = max_apg['SEASON_ID']
            df.at[idx, 'Peak SPG'] = round(max_spg['SPG'], 1)
            df.at[idx, 'Peak SPG Season'] = max_spg['SEASON_ID']
            df.at[idx, 'Peak BPG'] = round(max_bpg['BPG'], 1)
            df.at[idx, 'Peak BPG Season'] = max_bpg['SEASON_ID']

            # Novas colunas de tempo de carreira
            df.at[idx, 'Total Seasons'] = total_seasons
            df.at[idx, 'Career Span'] = career_span

            print(f"✅ Atualizado: {full_name} ({career_span} | {total_seasons} temps)")
            time.sleep(1.5)

        except Exception as e:
            print(f"⚠️ Erro ao processar {full_name}: {e}")
            continue

    # Salva o arquivo final com a estrutura completa
    df.to_csv("nba_legends_normalized.csv", index=False)
    print(f"\n🎯 Sucesso! O arquivo '{file_name}' foi atualizado contemplando todas as colunas.")
def update_legends_data():
    file_name = "nba_legends.csv"
    if not pd.io.common.file_exists(file_name):
        print("Arquivo nba_legends.csv não encontrado!")
        return

    df_existing = pd.read_csv(file_name)
    player_ids = df_existing['Player ID'].astype(str).tolist()

    print(f"Atualizando {len(player_ids)} lendas com Steals, Blocks e Picos de Temporada...")

    updated_legends = []

    for player_id in player_ids:
        row_data = df_existing[df_existing['Player ID'] == player_id].iloc[0]
        full_name = row_data['Full Name']

        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            df_career = career.get_data_frames()[0]

            if df_career.empty:
                continue

            df_career = df_career[df_career['GP'] > 0].copy()
            total_games = int(df_career['GP'].sum())
            total_points = int(df_career['PTS'].sum())
            total_rebs = int(df_career['REB'].sum())
            total_asts = int(df_career['AST'].sum())
            total_stl = int(df_career['STL'].sum() if 'STL' in df_career.columns else 0)
            total_blk = int(df_career['BLK'].sum() if 'BLK' in df_career.columns else 0)

            df_career['PPG'] = df_career['PTS'] / df_career['GP']
            df_career['APG'] = df_career['AST'] / df_career['GP']
            df_career['RPG'] = df_career['REB'] / df_career['GP']
            df_career['SPG'] = df_career['STL'] / df_career['GP'] if 'STL' in df_career.columns else 0
            df_career['BPG'] = df_career['BLK'] / df_career['GP'] if 'BLK' in df_career.columns else 0

            max_ppg = df_career.loc[df_career['PPG'].idxmax()]
            max_rpg = df_career.loc[df_career['RPG'].idxmax()]
            max_apg = df_career.loc[df_career['APG'].idxmax()]
            max_spg = df_career.loc[df_career['SPG'].idxmax()] if 'STL' in df_career.columns else None
            max_bpg = df_career.loc[df_career['BPG'].idxmax()] if 'BLK' in df_career.columns else None

            mvps = row_data['MVPs']
            finals_mvps = row_data['Finals MVPs']
            all_stars = row_data['All-Star Appearances']

            updated_legends.append({
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
                "Peak PPG": round(max_ppg['PPG'], 1),
                "Peak PPG Season": max_ppg['SEASON_ID'],
                "Peak RPG": round(max_rpg['RPG'], 1),
                "Peak RPG Season": max_rpg['SEASON_ID'],
                "Peak APG": round(max_apg['APG'], 1),
                "Peak APG Season": max_apg['SEASON_ID'],
                "Peak SPG": round(max_spg['SPG'], 1) if max_spg is not None else 0,
                "Peak SPG Season": max_spg['SEASON_ID'] if max_spg is not None else "N/A",
                "Peak BPG": round(max_bpg['BPG'], 1) if max_bpg is not None else 0,
                "Peak BPG Season": max_bpg['SEASON_ID'] if max_bpg is not None else "N/A",
            })

            print(f"✅ Atualizado: {full_name}")
            time.sleep(1.5)

        except Exception as e:
            print(f"⚠️ Erro ao atualizar {full_name}: {e}")
            updated_legends.append(row_data.to_dict())
            continue

    if updated_legends:
        df_new = pd.DataFrame(updated_legends)
        df_new.to_csv(file_name, index=False)
        print(f"\n✨ Sucesso! O arquivo '{file_name}' foi totalmente atualizado com as novas estatísticas e picos.")

def get_players_position():
    file_name = "nba_legends.csv"

    if not pd.io.common.file_exists(file_name):
        print(f"Arquivo {file_name} não encontrado.")
        return

    df = pd.read_csv(file_name)
    players_id = df['Player ID'].to_list()
    print(players_id)
    for player_id in players_id:
      try:
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        df_info = info.get_data_frames()[0]

        if not df_info.empty and 'POSITION' in df_info.columns:
          position = df_info['POSITION'].iloc[0]

        if pd.notna(position) and position != "":
          idx = df[df['Player ID'].astype(str) == str(player_id)].index[0]
          df.at[idx, 'Position'] = position


      except Exception as e:
        print(f"Erro ao buscar posição para o ID {player_id}: {e}")
      time.sleep(1)
    df.to_csv("legends_with_position.csv", index=False)
