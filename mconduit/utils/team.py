from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import Server


def list_teams(server: "Server") -> List[str]:
    
    response = server.execute("/team list")

    if parsed := parse.parse(r"There are {n} team(s): {teams}", response):

        teams = parsed["teams"]

        if "," in teams:
            teams = teams.split(", ")
        else:
            teams = [teams]

        return [team[1:-1] for team in teams]
    
    return []


def list_team_of_player(server: "Server", player: str) -> List[str]:
    ...


def remove_player(server: "Server", team: str, player: str) -> None:
    ...