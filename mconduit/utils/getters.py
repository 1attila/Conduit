from typing import Optional, List, TYPE_CHECKING

import parse

if TYPE_CHECKING:
    from ..server import Server


def get_teams(server: "Server") -> Optional[List[str]]:
    """
    Fetches all the teams name of the given server, if Rcon is active
    """

    if not server.is_running:
        return
    
    response = server.execute("/team list")

    if parsed := parse.parse(r"There are {n} team(s): {teams}", response):

        teams = parsed["teams"]

        if "," in teams:
            teams = teams.split(", ")
        else:
            teams = [teams]

        return [team[1:-1] for team in teams]