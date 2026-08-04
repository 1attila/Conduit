from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
import parse # type: ignore[import-untyped]
import json
import os

from mconduit.event import Event

if TYPE_CHECKING:
    from mconduit.server_runner import ServerRunner
    from mconduit.server import Server


PLAYER_NOT_SUPPORTED = "Player is not supported for this event!"


class ParsedResult:
    """
    Parsed stdout result
    """

    time: Tuple
    server: "Server"
    event: Event
    player: str
    infos: Dict[str, Any]


    def __init__(
        self,
        time: Tuple,
        server: "Server",
        event: Event,
        player: str,
        **kwargs
    ) -> None:
        
        self.time = time
        self.server = server
        self.event = event
        self.player = player
        self.infos = kwargs


class StdoutParser:
    """
    Parses all the process stdout
    """

    _death_messages: List[str]
    _player_actions: List[str]
    _runner: "ServerRunner"


    def __init__(
        self,
        runner: "ServerRunner"
    ) -> None:

        self._runner = runner
        
        with open(os.path.join("resources", "death_messages.json")) as f:

            data = json.load(f)
            self._death_messages = data["death_messages"]

        with open(os.path.join("resources", "player_actions.json")) as f:

            data = json.load(f)
            self._player_actions = data["player_actions"]


    def __call__(self, line: str) -> Optional[ParsedResult]:
        
        line = line.strip()
        
        if not line.__contains__("[Server thread/INFO]: "):
            return None
        
        data = parse.parse(r"[{h}:{m}:{s}] [Server thread/INFO]: [Not secure] {line}", line)
        
        if not data:

            data = parse.parse(r"[{h}:{m}:{s}] [Server thread/INFO]: {line}", line)

            if not data:
                return None
        
        line = data["line"]
        time = (data["h"], data["m"], data["s"])

        if player_action := self.process_player_actions(time, line):
            return player_action

        if server_action := self.process_server_actions(time, line):
            return server_action

        return None
        

    def process_player_actions(
        self,
        time: Tuple,
        line: str
    ) -> Optional[ParsedResult]:
        
        server = self._runner.server

        if line.startswith("["):
            
            if data := self.process_misc_actions(time, line, server):
                return data

        if data := parse.parse(r"<{player}> {message}", line):

            msg: str = data["message"]

            if msg.startswith(self._runner.handler.command_prefix):
                return ParsedResult(time, server, Event.PLAYER_COMMAND, data["player"], message=msg)

            return ParsedResult(time, server, Event.PLAYER_CHAT, data["player"], message=msg)

        if data := parse.parse(r"{player} joined the game", line):
            return ParsedResult(time, server, Event.PLAYER_JOIN, data["player"])

        if data := parse.parse(r"{player} left the game", line):
            return ParsedResult(time, server, Event.PLAYER_LEFT, data["player"])

        if data := parse.parse(r"[{player}: Triggered [{trigger}]]", line):
            return ParsedResult(time, server, Event.PLAYER_TRIGGER, data["player"], message=data["trigger"])

        if data := parse.parse(r"{player} has made the advancement [{advancement}]", line):
            return ParsedResult(time, server, Event.PLAYER_ADVANCEMENT, data["player"], advancement=data["advancement"])

        if data := parse.parse(r"{player} has completed the challenge [{challenge}]", line):
            return ParsedResult(time, server, Event.PLAYER_CHALLENGE, data["player"], message=data["challenge"])

        for death_message in self._death_messages:
            
            if data:= parse.parse(r"{player}" + death_message, line):
                return ParsedResult(time, server, Event.PLAYER_DEATH, data["player"], message=death_message)
        
        return None

    
    def process_misc_actions(
        self,
        time: Tuple,
        line: str,
        server: "Server"
    ) -> Optional[ParsedResult]:
        
        if data := parse.parse(r"[{player1}: Made {player2} a server operator]", line):
            return ParsedResult(time, server, Event.PLAYER_OPPED, data["player1"], other_player=data["player2"])

        if data := parse.parse(r"[{player1}: Made {player2} no longer a server operator]", line):
            return ParsedResult(time, server, Event.PLAYER_DEOPPED, data["player1"], other_player=data["player2"])

        if data := parse.parse(r"[{player1}: Added {player2} to the whitelist]", line):
            return ParsedResult(time, server, Event.PLAYER_WHITELISTED, data["player1"], other_player=data["player2"])

        if data := parse.parse(r"[{player1}: Removed {player2} from the whitelist]", line):
            return ParsedResult(time, server, Event.PLAYER_UNWHITELISTED, data["player1"], other_player=data["player2"])

        if data := parse.parse(r"[{player1}: Kicked {player2}: {reason}]", line):
            return ParsedResult(time, server, Event.PLAYER_KICKED, data["player1"], other_player=data["player2"])
        
        if data := parse.parse(r"[{player1}: Set [{scoreboard}] for {player2} to {value}]", line):
            return ParsedResult(time, server, Event.SET_SCOREBOARD_VALUE, data["player1"], other_player=data["player2"], scoreboard=data["scoreboard"], value=data["value"])

        if data := parse.parse(r"[{player1}: Added {amount} to [{scoreboard}] for {player2} (now {value})]", line):
            return ParsedResult(time, server, Event.ADD_SCOREBOARD_VALUE, data["player1"], other_player=data["player2"], scoreboard=data["scoreboard"], value=data["value"], amount=data["amount"])

        if data := parse.parse(r"[{player1}: Removed {amount} from [{scoreboard}] for {player2} (now {value})]", line):
            return ParsedResult(time, server, Event.SUB_SCOREBOARD_VALUE, data["player1"], other_player=data["player2"], scoreboard=data["scoreboard"], value=data["value"], amount=data["amount"])
        
        if data := parse.parse(r"[{player1}: Reset [{scoreboard}] for {player2}]", line):
            return ParsedResult(time, server, Event.RESET_SCOREBOARD_VALUE, data["player1"], other_player=data["player2"], scoreboard=data["scoreboard"])
        
        if data := parse.parse(r"[{player1}: Saved the game]", line):

            player1 = data["player1"]

            if player1 == "Rcon":
                return ParsedResult(time, server, Event.GAME_SAVED, PLAYER_NOT_SUPPORTED)

            return ParsedResult(time, server, Event.PLAYER_SAVED_THE_GAME, player1)

        if data := parse.parse(r"[{player1}: Gave {n} [item] to {player2}]", line):
            ...

        if data := parse.parse(r"[{player1}: Set own gamemode to {gamemode} Mode]", line):
            ...

        if data := parse.parse(r"[{player1}: Summoned new {entity}]", line):
            ...

        if data := parse.parse(r"[{player1}: Killed {player2}]", line):
            ...

        return None
        
    
    def process_server_actions(
        self,
        time: Tuple,
        line: str
    ) -> Optional[ParsedResult]:

        if data := parse.parse(r'Done ({time}s)! For help, type "help"', line):
            return ParsedResult(time, self._runner.server, Event.SERVER_START, PLAYER_NOT_SUPPORTED)
        
        if line == "Stopping server":
            return ParsedResult(time, self._runner.server, Event.SERVER_STOP, PLAYER_NOT_SUPPORTED)

        if line == "Saved the game":
            return ParsedResult(time, self._runner.server, Event.GAME_SAVED, PLAYER_NOT_SUPPORTED)

        return None