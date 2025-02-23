from typing import NoReturn, Optional, List, Tuple, Dict, TYPE_CHECKING
import parse
import json
import os

from .Event import Event

if TYPE_CHECKING:
    from .ServerRunner import ServerRunner
    from .Server import Server


class ParsedResult:
    """
    Parsed stdout result
    """

    time: Tuple
    server: "Server"
    event: Event
    player: str
    infos: Dict


    def __init__(self, time: Tuple, server: "Server", event: Event, player: str, infos: Optional[Dict]=None):
        
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


    def __init__(self, runner: "ServerRunner") -> NoReturn:

        self.__runner = runner
        
        with open(os.getcwd() + "\\Conduit\\Resources\\death_messages.json") as f:

            data = json.load(f)
            self.__death_messages = data["death_messages"]

        with open(os.getcwd() + "\\Conduit\\Resources\\player_actions.json") as f:

            data = json.load(f)
            self.__player_actions = data["player_actions"]


    def __call__(self, line: str) -> Optional[ParsedResult]:
        
        line = line.strip()

        if line == "":
            return
        
        if not line.__contains__("[Server thread/INFO]: "):
            return
        
        data = parse.parse(r"[{h}:{m}:{s}] [Server thread/INFO]: {line}", line)
        
        if not data:
            return
        
        line = data["line"]
        time = (data["h"], data["m"], data["s"])

        return self.process_player_actions(time, line)
        

    def process_player_actions(self, time: Tuple, line: str) -> Optional[ParsedResult]:
        
        server = self.__runner.server

        if data:= parse.parse(r"{player} joined the game", line):
            return ParsedResult(time, server, Event.PlayerJoin, data["player"])

        if data:= parse.parse(r"{player} left the game", line):
            return ParsedResult(time, server, Event.PlayerLeft, data["player"])

        if data:= parse.parse(r"<{player}> {message}", line):

            msg = data["message"]

            if msg.startswith(self.__runner.handler.command_prefix):
                return ParsedResult(time, server, Event.PlayerCommand, data["player"], {"cmd": msg})

            return ParsedResult(time, server, Event.PlayerChat, data["player"], {"msg": msg})

        for death_message in self.__death_messages:
            
            if data:= parse.parse(r"{player}" + death_message, line):
                return ParsedResult(time, server, Event.PlayerDeath, data["player"], {"msg": death_message})