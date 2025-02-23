from typing import Optional, Callable, NoReturn, List, Dict, TYPE_CHECKING
from pathlib import Path
import copy
import os

from .ServerAPI import ServerAPI
from .EventHandler import EventHandler
from .utils.Rcon import Rcon
from .utils.CheckAnnotation import check_annotation
from .Lang.Lang import Lang
from .Event import Event
from .Context import Context

if TYPE_CHECKING:
    from .ServerRunner import ServerRunner
    from .ConduitConfig import ServerRunnerConfig
    from .Handler import Handler


class Server(ServerAPI):
    """
    Minecraft server interface

    Contains all the fetching and rcon API and some useful attributes 
    """

    __name: str
    __names: Optional[List[str]]
    __path: Path
    __rcon: Rcon
    __runner: "ServerRunner"
    __config: "ServerRunnerConfig"
    __event_handler: EventHandler
    __lang: "Lang"
    __slots: Dict[Event, List[Callable]]


    def __init__(self, runner: "ServerRunner") -> "Server":

        config = runner.config
        self.__runner = runner
        self.__config = config
        self.__path = config.path
        self.__name = config.name
        self.__names = config.names

        self.__event_handler = EventHandler(self)
        self.__lang = Lang(os.getcwd() + "\\Conduit\\Resources", config.language)
        
        self.__rcon = Rcon(
            config.rcon_config.address,
            config.rcon_config.port,
            config.rcon_config.password
        )
        
        self.__slots = {event: [] for event in [
            Event.PlayerJoin, 
            Event.PlayerLeft,
            Event.PlayerDeath,
            Event.PlayerChat,
            Event.PlayerCommand
        ]}

        super().init(self.__config, self.__rcon) # ServerDataFetchAPI
    

    @property
    def name(self) -> str:
        """
        Server main name
        """

        return self.__name
    

    @property
    def names(self) -> List[str]:
        """
        All servers names
        """

        return self.__names
    

    @property
    def path(self) -> Path:
        """
        Server folder path
        """

        return self.__path
    

    @property
    def handler(self) -> "Handler":
        """
        Servers handler
        """

        return self.__runner.handler
    

    @property
    def config(self) -> "ServerRunnerConfig":
        """
        Servers config, Rcon configs are obfuscated for security
        """
        
        config = copy.deepcopy(self.__config)
        config.rcon_config = None

        return config
    

    @property
    def event_handler(self) -> EventHandler:
        """
        Server event handler
        """

        return self.__event_handler
    

    @property
    def lang(self) -> "Lang":
        """
        Server language
        """

        return self.__lang
    

    def set_lang(self, lang: str) -> NoReturn:
        """
        Sets the main language
        """
        
        self.__lang.set_lang(lang)
        self.__runner.handler.__config.save()
    
    
    def start(self) -> NoReturn:
        """
        Starts the server
        """

        self.__runner.start()


    def stop(self) -> NoReturn:
        """
        Stops the server process
        """

        self.__runner.stop()


    @property
    def seed(self) -> Optional[int]:
        """
        Retrieves the server seed with Rcon.
        """

        return int(self.execute("/seed"))
    

    def event(self, fn: Callable) -> NoReturn:
        """
        Calls the function every time the event of the function name occours.

        The function must only take a single argument of type Context or subclasses of it, depending on the event type
        """
        
        match fn.__name__:
            case "on_player_join":
                self.on_player_join(fn)
            case "on_player_left":
                self.on_player_left(fn)
            case "on_player_death":
                self.on_player_death(fn)
            case "on_player_message":
                self.on_player_message(fn)
            case "on_player_command":
                self.on_player_command(fn)
            case _:
                raise Exception("The function name doesn't match any event name!")


    def on_player_join(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time player joins.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerJoin].append(fn)


    def on_player_left(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time a player left the server.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerLeft].append(fn)


    def on_player_death(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time a player is killed.

        The function must only take a single argument of type PlayerDeathContext
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerDeath].append(fn)


    def on_player_message(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time a player sends a message.

        The function must only take a single argument of type PlayerMessageContext
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerChat].append(fn)


    def on_player_command(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time a player sends a command.

        The function must only take a single argument of type PlayerCommandContext
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerCommand].append(fn)

    
    def execute(self, command: str) -> str:
        """
        Executes a command with Rcon
        """

        return self.__rcon(command)
        

    def __call__(self, command: str) -> str:
        """
        execute() alis, executes a command with Rcon
        """

        return self.execute(command)

    
    def _on_player_event(self, ctx: Context) -> NoReturn:
        """
        Dispatches server events and calls them
        """

        for fn in self.__slots[ctx.event_type]:
            fn(ctx)

    
    def on_player_rigth_click(): ...
    def on_player_left_click(): ...
    def on_player_shift(): ...