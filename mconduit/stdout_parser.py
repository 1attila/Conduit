from typing import Optional, List, Tuple, Dict, TYPE_CHECKING
import parse
import json
import os

from .event import Event

if TYPE_CHECKING:
    from .server_runner import ServerRunner
    from .server import Server


PLAYER_NOT_SUPPORTED = "Player is not supported for this event!"


class ParsedResult:
    """
    Parsed stdout result
    """

    time: Tuple
    server: "Server"
    event: Event
    player: str
    infos: Optional[Dict]


    def __init__(
        self,
        time: Tuple,
        server: "Server",
        event: Event,
        player: str,
        infos: Optional[Dict]=None
    ) -> None:
        
        self.time = time
        self.server = server
        self.event = event
        self.player = player
        self.infos = infos


class StdoutParser:
    """
    Parses all the process stdout
    """

    __death_messages: List[str]
    __player_actions: List[str]
    __runner: "ServerRunner"


    def __init__(
        self,
        runner: "ServerRunner"
    ) -> None:

        self.__runner = runner
        
        with open(os.path.join("resources", "death_messages.json")) as f:

            data = json.load(f)
            self.__death_messages = data["death_messages"]

        with open(os.path.join("resources", "player_actions.json")) as f:

            data = json.load(f)
            self.__player_actions = data["player_actions"]


    def __call__(self, line: str) -> Optional[ParsedResult]:
        
        line = line.strip()
        
        if not line.__contains__("[Server thread/INFO]: "):
            return # type: ignore
        
        data = parse.parse(r"[{h}:{m}:{s}] [Server thread/INFO]: [Not secure] {line}", line)
        
        if not data:

            data = parse.parse(r"[{h}:{m}:{s}] [Server thread/INFO]: {line}", line)

            if not data:
                return # type: ignore
        
        line = data["line"]
        time = (data["h"], data["m"], data["s"])

        if player_action := self.process_player_actions(time, line):
            return player_action

        if server_action := self.process_server_actions(time, line):
            return server_action
        

    def process_player_actions(
        self,
        time: Tuple,
        line: str
    ) -> Optional[ParsedResult]:
        
        server = self.__runner.server

        if line.startswith("["):
            
            if data := self.process_misc_actions(time, line, server):
                return data

        if data := parse.parse(r"<{player}> {message}", line):

            msg = data["message"]

            if msg.startswith(self.__runner.handler.command_prefix):
                return ParsedResult(time, server, Event.PlayerCommand, data["player"], {"cmd": msg})

            return ParsedResult(time, server, Event.PlayerChat, data["player"], {"msg": msg})

        if data := parse.parse(r"{player} joined the game", line):
            return ParsedResult(time, server, Event.PlayerJoin, data["player"])

        if data := parse.parse(r"{player} left the game", line):
            return ParsedResult(time, server, Event.PlayerLeft, data["player"])

        if data := parse.parse(r"[{player}: Triggered [{trigger}]]", line):
            return ParsedResult(time, server, Event.PlayerTrigger, data["player"], {"trigger": data["trigger"]})

        if data := parse.parse(r"{player} has made the advancement [{advancement}]", line):
            return ParsedResult(time, server, Event.PlayerAdvancement, data["player"], {"advancement": data["advancement"]})

        if data := parse.parse(r"{player} has completed the challenge [{challenge}]", line):
            return ParsedResult(time, server, Event.PlayerChallenge, data["player"], {"challenge": data["challenge"]})

        for death_message in self.__death_messages:
            
            if data:= parse.parse(r"{player}" + death_message, line):
                return ParsedResult(time, server, Event.PlayerDeath, data["player"], {"msg": death_message})
            
    
    def process_misc_actions(
        self,
        time: Tuple,
        line: str,
        server: "Server"
    ) -> Optional[ParsedResult]:
        
        if data := parse.parse(r"[{player1}: Made {player2} a server operator]", line):
            return ParsedResult(time, server, Event.PlayerOpped, data["player1"], {"other_player": data["player2"]})

        if data := parse.parse(r"[{player1}: Made {player2} no longer a server operator]", line):
            return ParsedResult(time, server, Event.PlayerDeopped, data["player1"], {"other_player": data["player2"]})

        if data := parse.parse(r"[{player1}: Added {player2} to the whitelist]", line):
            return ParsedResult(time, server, Event.PlayerWhitelisted, data["player1"], {"other_player": data["player2"]})

        if data := parse.parse(r"[{player1}: Removed {player2} from the whitelist]", line):
            return ParsedResult(time, server, Event.PlayerUnwhitelisted, data["player1"], {"other_player": data["player2"]})

        if data := parse.parse(r"[{player1}: Kicked {player2}: {reason}]", line):
            return ParsedResult(time, server, Event.PlayerKicked, data["player1"], {"other_player": data["player2"]})
        
        if data := parse.parse(r"[{player1}: Set [{scoreboard}] for {player2} to {value}]", line):
            return ParsedResult(time, server, Event.SetScoreboardValue, data["player1"], {"other_player": data["player2"], "scoreboard": data["scoreboard"], "value": data["value"]})

        if data := parse.parse(r"[{player1}: Added {amount} to [{scoreboard}] for {player2} (now {value})]", line):
            return ParsedResult(time, server, Event.AddScoreboardValue, data["player1"], {"other_player": data["player2"], "scoreboard": data["scoreboard"], "value": data["value"], "amount": data["amount"]})

        if data := parse.parse(r"[{player1}: Removed {amount} from [{scoreboard}] for {player2} (now {value})]", line):
            return ParsedResult(time, server, Event.SubScoreboardValue, data["player1"], {"other_player": data["player2"], "scoreboard": data["scoreboard"], "value": data["value"], "amount": data["amount"]})
        
        if data := parse.parse(r"[{player1}: Reset [{scoreboard}] for {player2}]", line):
            return ParsedResult(time, server, Event.ResetScoreboardValue, data["player1"], {"other_player": data["player2"], "scoreboard": data["scoreboard"]})
        
        if data := parse.parse(r"[{player1}: Gave {n} [item] to {player2}]", line):
            ...

        if data := parse.parse(r"[{player1}: Set own gamemode to {gamemode} Mode]", line):
            ...

        if data := parse.parse(r"[{player1}: Summoned new {entity}]", line):
            ...

        if data := parse.parse(r"[{player1}: Killed {player2}]", line):
            ...
    
    def process_server_actions(
        self,
        time: Tuple,
        line: str
    ) -> Optional[ParsedResult]:

        if data := parse.parse(r'Done ({time}s)! For help, type "help"', line):
            return ParsedResult(time, self.__runner.server, Event.ServerStart, PLAYER_NOT_SUPPORTED, {"loading_time": data["time"]})
        
        if line == "Stopping server":
            return ParsedResult(time, self.__runner.server, Event.ServerStop, PLAYER_NOT_SUPPORTED)

        if line == "Saved the world":
            return ParsedResult(time, self.__runner.server, Event.GameSaved, PLAYER_NOT_SUPPORTED)