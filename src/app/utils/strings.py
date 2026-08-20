def format_player_name(player_name: str) -> str:
  """
  Get a player name from the URL and format it to match the database format.
  """
  return player_name.replace("-", " ").title()
