import pandas as pd
from nba_api.stats.endpoints import commonplayerinfo

def main():
  df = pd.read_csv("nba_legends_normalized.csv")
  to_change = df[(df['Total Points'] < 20000) & (df['Total Assists'] < 7000) & (df['Total Rebounds'] < 8000)]
  print(to_change[['Player ID', 'Full Name', 'MVPs', 'Finals MVPs', 'All-Star Appearances']])


main()
