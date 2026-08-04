from typing import List, Optional, TYPE_CHECKING
import datetime
import parse # type: ignore[import-untyped]

from mconduit.event import Event, EventListener

if TYPE_CHECKING:
    from mconduit.server import Server


class ScoreboardTracker(EventListener):
    """
    Utilty class to track scoreboards values
    """

    scoreboard_name: str


    def __init__(self, server, scoreboard: str) -> None:

        super().__init__(server)
        self.scoreboard_name = scoreboard


    def tick(self) -> None:
        raise NotImplementedError()


class TextScoreboardTracker(ScoreboardTracker):

    def tick(self) -> None:

        for player in self.server.online_players:

            score = self.server.execute(f"/scoreboard players get {player} {self.scoreboard_name}")
            
            if value := parse.parse(r"{player} has {n} {scoreboard}", score):

                if int(value["n"]) > 0:

                    self.server.execute(f"/scoreboard players set {player} {self.scoreboard_name} 0")

                    date = datetime.datetime.now()

                    # self._run_fallbacks(
                    #     Context(player, (date.hour, date.minute, date.second), self.server, Event.TextClick)
                    # )

        return None


def generate_text_scoreboard(server: "Server") -> str:
    """
    Generates a scoreboard to run text functions
    """

    TEXT_SCOREBOARD_PREFIX = "mconduit-text-"

    all_scoreboards = server.execute("/scoreboard objectives list")

    if all_scoreboards == "There are no objectives":
        
        s_name = TEXT_SCOREBOARD_PREFIX + str(0)
        server.execute(f'/scoreboard objectives add {s_name} dummy "{s_name}"')

        return s_name

    if parsed := parse.parse(r"There are {n} objective(s): {scoreboards}", all_scoreboards):
        
        scoreboards = parsed["scoreboards"]
        
        if "," in scoreboards:
            scoreboards = scoreboards.split(", ")
        else:
            scoreboards = [scoreboards]
        
        text_ids = []

        for scoreboard in scoreboards:
            
            if scoreboard.startswith(f"[{TEXT_SCOREBOARD_PREFIX}"):
                text_ids.append(int(scoreboard[15:-1]))
        
        new_id = max(text_ids, default=-1) + 1
        
        s_name = TEXT_SCOREBOARD_PREFIX + str(new_id)

        server.execute(f'/scoreboard objectives add {s_name} dummy "{s_name}"')

        return s_name

    raise RuntimeError("Unable to parse output of /scoreboard objectives list")
    

def get_latest_scoreboard_id(server: "Server", scoreboard_name: str) -> int:
    """
    Return the id of the scoreboards with the matching name
    """

    all_scoreboards = server.execute("/scoreboard objectives list")

    if all_scoreboards == "There are no objectives":
        return 0

    if parsed := parse.parse(r"There are {n} objective(s): {scoreboards}", all_scoreboards):
        
        scoreboards = parsed["scoreboards"]
        
        if "," in scoreboards:
            scoreboards = scoreboards.split(", ")
        else:
            scoreboards = [scoreboards]
        
        text_ids = []

        for scoreboard in scoreboards:
            
            if scoreboard.startswith(f"[{scoreboard_name}"):
                text_ids.append(int(scoreboard[len(scoreboard_name)+1:-1]))
        
        return max(text_ids, default=-1) + 1

    raise RuntimeError("Unable to parse output of /scoreboard objective list")


def get_latest_trigger_id(server: "Server", trigger_name: str) -> int:
    """
    Return the next trigger id, needed for a text function
    """

    all_scoreboards = server.execute("/scoreboard objectives list")

    if all_scoreboards == "There are no objectives":
        return 0

    if parsed := parse.parse(r"There are {n} objective(s): {scoreboards}", all_scoreboards):
        
        scoreboards = parsed["scoreboards"]
        
        if "," in scoreboards:
            scoreboards = scoreboards.split(", ")
        else:
            scoreboards = [scoreboards]
        
        text_ids = []

        for scoreboard in scoreboards:
            
            if scoreboard.startswith(f"[{trigger_name}"):

                id, _button_id = scoreboard[len(trigger_name)+1:-1].split("-")

                try: # It may happens smh "mconduit-text-None-X"
                    id = int(id)
                except:
                    id = 0
                
                text_ids.append(id)
        
        return max(text_ids, default=-1) + 1
    
    return 0
    

def list_scoreboards(server: "Server", prefix: str="") -> List[str]:
    """
    Lists all the scoreboards on a given server
    """

    all_scoreboards = server.execute("/scoreboard objectives list")

    if all_scoreboards == "There are no objectives":
        return []

    if parsed := parse.parse(r"There are {n} objective(s): {scoreboards}", all_scoreboards):
        
        scoreboards = parsed["scoreboards"]
        
        if "," in scoreboards:
            scoreboards = scoreboards.split(", ")
        else:
            scoreboards = [scoreboards]
        
        text_ids = []

        for scoreboard in scoreboards:
            
            if scoreboard.startswith(f"[{prefix}"):
                text_ids.append(scoreboard[1:-1])

        return text_ids
    
    else:
        return []


def get_score(server: "Server", player: str, objective: str) -> Optional[float]:

    value = server.execute(f"/scoreboards players get {player} {objective}")

    if value is None and isinstance(value, str):
        return None

    if parsed := parse.parse(r"{player} has {score} [{scoreboard-id}]", value):
        return float(parsed["score"])

    return None