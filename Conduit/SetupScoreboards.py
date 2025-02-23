from typing import NoReturn, List
import parse

from .Server import Server


SCOREBOARDS = { "delta_shift" : "minecraft.custom:minecraft.sneak_time" }


def get_scoreboards(server: Server) -> List[str]:
    """
    Returns a list with all the server scoreboards
    """

    response = server.execute("/scoreboard objectives list")

    if response != "":

        scoreboards = parse.parse(r"There are {n} objective(s): {objectives}", response)
        scoreboards = scoreboards["objectives"]

        if scoreboards:
            return [scoreboard[1:-1] for scoreboard in scoreboards]

    return []


def setup_scoreboards(servers: List[Server]) -> NoReturn:
    """
    Creates and initializes scoreboards to detect events.

    It runs when the server is started
    """
    
    for server in servers:

        server_scoreboards = get_scoreboards(server)

        for s_name, s_command in SCOREBOARDS.items():
            
            if s_name not in server_scoreboards:
                server.execute(f"/scoreboard objectives add {s_name} {s_command}")

            server.execute("/scoreboard players set @a {s_name} 0")


def check_scoreboards(servers: List[Server]) -> NoReturn:
    """
    Runs really fast to check if every player has triggered an event
    """

    servers_scoreboards = []

    for server in servers:

        scoreboards = []

        for s_name in SCOREBOARDS.keys():

            scoreboard = {}
            
            for player in server.get_online_players():
                data = server.execute(f"/scoreboards players get {player} {s_name}")

                score = parse.parse(r"{player} has {n} [{s_name}]", data)

                score = score["n"]
                scoreboard[player.name] = score

            scoreboards.append(scoreboard)
        servers.append(scoreboards)