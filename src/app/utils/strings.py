def format_player_name(name: str, last_name: str = "") -> str:
    """
    Get a player name from the URL and format it to match the database format.
    """
    if name.find("-") != -1:
        return name.replace("-", " ").title()

    if last_name != "":
        return f"{name} {last_name}"
