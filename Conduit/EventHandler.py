from typing import Callable, NoReturn, Dict, List, TYPE_CHECKING

from .Event import Event
from .Types.Player import Player
from .Context import Context
from .StdoutParser import ParsedResult

if TYPE_CHECKING:
    from Server import Server


class EventHandler:
    """
    Handles and dispatch events
    """


    __slots: Dict[Event, List[Callable]]
    __fallback: "Server"
    __players: List[Player]


    def __init__(self, fallback: "Server") -> NoReturn:
        self.__fallback = fallback


    def process_parsed_stdout(self, parsed: ParsedResult) -> Context:
        
        match parsed.event:
            
            case Event.PlayerJoin:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerJoin)
            case Event.PlayerLeft:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerLeft)
            case Event.PlayerDeath:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerDeath, parsed.infos["msg"])
            case Event.PlayerChat:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerChat, parsed.infos["msg"])
            case Event.PlayerCommand:
                return Context(parsed.player, parsed.time, parsed.server, Event.PlayerCommand, parsed.infos["cmd"])


    def __call__(self, player_event: ParsedResult) -> NoReturn:
        
        # prev_players = self.__players
        # self.__players = self.__fallback.get_online_players()

        # for event, fns in self.__slots:

        #     if ctxs:= event.process():
                
        #         for ctx in ctxs:
        #             for fn in fns:
        #                 fn(ctx)

        if player_event:
            self.__fallback._on_player_event(self.process_parsed_stdout(player_event))


    def add_listener(self, event: Event, fn: Callable) -> NoReturn:
        """
        The function that gets called by the event must have only a single parameter of type Context
        """

        assert event not in [
            Event.PlayerLeftClick,
            Event.PlayerRigthClick,
            Event.PlayerShift
        ], "This event is registered by default"

        annotation = fn.__annotations__

        if "return" in annotation.keys():
            annotation.pop("return")

        for item in annotation.values():
            param = item
        
        if type(param) == Context or issubclass(type(param), Context):
            self.__slots[event].append(fn)