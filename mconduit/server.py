from typing import Optional, Union, Callable, List, Dict, Any, TYPE_CHECKING
from pathlib import Path
import threading
import copy

from .server_api import ServerAPI
from .event_handler import EventHandler
from .utils.rcon import Rcon, AllAtOnce
from .utils.version_fetcher import VersionFetcher
from .utils.check_annotation import check_annotation
from .text._text_handler import TextHandler
from .resource_pack import ResourcePack
from .lang.lang import Lang
from .plugin_manager import PluginManager
from .event import Event
from .context import Context

if TYPE_CHECKING:
    from .server_runner import ServerRunner
    from .conduit_config import ServerRunnerConfig
    from .handler import Handler
    from .plugins.perms import Permission


class Server(ServerAPI):
    """
    Minecraft server interface

    Contains all the fetching and Rcon API and some useful attributes 
    """

    __names: List[str]
    __path: Path
    __rcon: Rcon
    __runner: "ServerRunner"
    __config: "ServerRunnerConfig"
    __event_handler: EventHandler
    __lang: "Lang"
    __slots: Dict[Event, List[Callable[[Any], Any]]]
    __lock: threading.RLock
    __plugin_manager: PluginManager
    __perms: Dict["Permission", List[str]]
    __is_running: bool
    __is_v1_21_5: bool
    __text_handler: "TextHandler"
    __resource_pack: ResourcePack


    def __init__(self, runner: "ServerRunner") -> None:

        config = runner.config
        self.__runner = runner
        self.__config = config
        self.__path = config.path
        self.__names = config.names

        self.__slots = {event: [] for event in [
            Event.PlayerJoin, 
            Event.PlayerLeft,
            Event.PlayerDeath,
            Event.PlayerChat,
            Event.PlayerCommand,
            Event.ServerStart,
            Event.ServerStop,
            Event.ConduitStart,
            Event.ConduitStop
        ]}

        def on_start(self: "Server"):
            self.__is_running = True
            self.execute("/gamerule sendCommandFeedback false")
            self.__is_v1_21_5 = VersionFetcher.is_v1_21_5(self)
            self.execute("/scoreboard objectives add mconduit-sneak minecraft.custom:minecraft.sneak_time")
            self.__text_handler.reset()
            self.__resource_pack._serve()
        
        def on_stop(self: "Server"):
            self.__is_running = False
            self.__resource_pack._stop_and_update()

        self.__slots[Event.ServerStart].append(on_start)
        self.__slots[Event.ServerStop].append(on_stop)
        
        self.__lock = threading.RLock()
        self.__event_handler = EventHandler(self)
        self.__lang = Lang(Path.cwd() / "resources", config.language) # NOTE: This may raise
        
        self.__rcon = Rcon(
            config.rcon_config.address,
            config.rcon_config.port,
            config.rcon_config.password
        )

        super().init(self.__config, self.__rcon) # ServerDataFetchAPI
        
        self.__is_running = self.seed is not None
        self.__is_v1_21_5 = False # PlaceHolder
        self.__text_handler = TextHandler(self)

        self.__resource_pack = ResourcePack(self)

        if self.__is_running:
            on_start(self)
        else:
            self.__resource_pack._stop_and_update()
        
        self.__plugin_manager = PluginManager(self)
        self.__perms = {}


    def __repr__(self) -> str:
        return self.__names[0]

    
    @property
    def name(self) -> str:
        """
        Server main name
        """

        return self.__names[0]
    

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
        Copy of Servers config, Rcon and Machine configs are None for security reasons
        """
        
        config = copy.deepcopy(self.__config)
        config.rcon_config = None # type: ignore
        config.machine_config = None # type: ignore

        return config
    

    @property
    def event_handler(self) -> EventHandler:
        """
        Server event handler
        """

        return self.__event_handler


    @property
    def plugin_manager(self) -> PluginManager:
        """
        Server plugin manager
        """

        return self.__plugin_manager

    
    @property
    def permissions(self) -> Dict["Permission", List[str]]:
        """
        Server permission -> teams mapping
        """

        return self.__perms

    
    def _set_perms(self, perms: Dict["Permission", List[str]]) -> None:
        """
        Sets server permissions.

        This function should be called ONLY by `Handler`
        """

        with self.__lock:

            self.__perms[4] = perms["Owner"]
            self.__perms[3] = perms["Admin"]
            self.__perms[2] = perms["Helper"]
            self.__perms[1] = perms["User"]
            self.__perms[0] = perms["Guest"]
            

    @property
    def lang(self) -> "Lang":
        """
        Server language
        """

        return self.__lang
    

    def set_lang(self, lang: str) -> None:
        """
        Sets the main language to the server and all it's plugins.

        Updates configs aswell
        """
        
        with self.__lock:
        
            if self.__lang.set_lang(lang):

                self.__runner.handler.__config.save()
                self.__plugin_manager.set_lang(lang)


    @property
    def is_running(self) -> bool:
        """
        True if the Minecraft server is running with Rcon enabled, False otherwise
        """

        with self.__lock:
            
            self.__is_running = self.seed is not None

            return self.__is_running


    @property
    def slots(self) -> Dict[Event, List[Callable[[Union["Handler", "Server", Context]], Any]]]:
        return self.__slots
    
    
    def start(self) -> None:
        """
        Starts the server
        """

        raise NotImplementedError
        self.__runner.start()


    def stop(self) -> None:
        """
        Stops the server process
        """

        self.__runner.stop()


    @property
    def seed(self) -> Optional[int]:
        """
        Retrieves the server seed with Rcon.
        """

        res = self.execute("/seed")
        
        if res is not None and len(res) > 0:

            res = res[7:-2]
            return int(res) # type: ignore


    @property
    def is_v1_21_5(self) -> bool:
        """
        Returns True, if the server version >= 1.21.5

        This exists mainly due to debug purposes, since Json Text has changed since 1.21.5+
        """

        return self.__is_v1_21_5
    

    @property
    def _text_handler(self) -> TextHandler:
        """
        Responsible to bind the text click and execute their callbacks.

        This should be accessed only by EventHandler.__call__()
        """

        return self.__text_handler
    

    @property
    def resource_pack(self) -> ResourcePack:
        """
        Server resource pack.

        Can be used to add custom sounds/textures etc.

        Note: To apply changes you must restart the server!
        """

        return self.__resource_pack
        

    def read_file(self, relative_path: str) -> Optional[str]:
        """
        Returns the content of the given file.

        This should be used ONLY if the file is located to the server machine (like server.properties)
        """
        
        return self.__runner._read_file(relative_path)

    
    def write_file(self, relative_path: str, content: Union[str, bytes]) -> None:
        """
        Writes the given file with the specified content.

        This should be used ONLY if the file is located to the server machine (like server.properties)
        """
        
        self.__runner._write_file(relative_path, content)


    def all_at_once(self) -> AllAtOnce:
        """
        Builds a ContextManager that executes all the commands that have been called in it's context at the end
        """

        with self.__lock:
            return self.__rcon.all_at_once()

    
    def _add_event_fallback(
        self,
        event: Event,
        fallback: Callable[[Union[Context, "Server", "Handler"]], Any]
    ) -> None:
        """
        Adds the given fallback to the specified event name.

        This function exist only to be called by the Plugin to link it's events
        """

        with self.__lock:
            self.__slots.setdefault(event, []).append(fallback)
    

    def event(self, fn: Callable[[Union[Context, "Server", "Handler"]], Any]) -> None:
        """
        Calls the function every time the event of the function name occours.

        The function must only take a single argument of type Context
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
            case "on_server_start":
                self.on_server_start(fn)
            case "on_server_stop":
                self.on_server_stop(fn)
            case _:
                raise Exception("The function name doesn't match any event name!")


    def on_player_join(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time player joins.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerJoin].append(fn)


    def on_player_left(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time a player left the server.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerLeft].append(fn)


    def on_player_death(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time a player is killed.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerDeath].append(fn)


    def on_player_message(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time a player sends a message.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerChat].append(fn)


    def on_player_command(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time a player sends a command.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self.__slots[Event.PlayerCommand].append(fn)

    
    def on_conduit_start(self, fn: Callable[["Handler"], Any]) -> None:
        """
        Decorator that calls the function every time conduit is started.

        The function must only take a single argument of type Handler
        """

        if check_annotation(fn, "Handler"):
            self.__slots[Event.ConduitStart].append(fn)


    def on_conduit_stop(self, fn: Callable[["Handler"], Any]) -> None:
        """
        Decorator that calls the function every time conduit is about to stop.

        The function must only take a single argument of type Handler
        """

        if check_annotation(fn, "Handler"):
            self.__slots[Event.ConduitStop].append(fn)

    
    def on_server_start(self, fn: Callable[["Server"], Any]) -> None:
        """
        Decorator that calls the function every time a server is started.

        The function must only take a single argument of type Server
        """

        if check_annotation(fn, Server):
            self.__slots[Event.ServerStart].append(fn)


    def on_server_stop(self, fn: Callable[["Server"], Any]) -> None:
        """
        Decorator that calls the function every time a server stops.

        The function must only take a single argument of type Server
        """

        if check_annotation(fn, Server):
            self.__slots[Event.ServerStop].append(fn)

    
    def execute(self, command: Union[List[str], str]) -> Optional[Union[List[str], str]]:
        """
        Executes a command with Rcon
        """

        with self.__lock:
            return self.__rcon(command)
        

    def __call__(self, command: Union[List[str], str]) -> Optional[Union[List[str], str]]:
        """
        execute() alis, executes a command with Rcon
        """

        return self.execute(command)

    
    def _on_player_event(self, ctx: Context) -> None:
        """
        Dispatches player events and calls them
        """

        for fn in self.__slots[ctx.event_type]:

            try:
                if ctx.event_type in [Event.ServerStart, Event.ServerStop]:
                    fn(ctx.server) # type: ignore
                else:
                    # NOTE: Conduit events are not sent here
                    # this method is called only by event_handler which recieves only logs events
                    fn(ctx)
            except:
                pass

    
    def _on_conduit_start(self) -> None:
        """
        Handles ConduitStart event
        """

        for fn in self.__slots[Event.ConduitStart]:
            fn(self.handler)


    def _join_input_thread(self) -> None:
        """
        Joins the server input loop thread
        """

        for fn in self.__slots[Event.ConduitStop]:
            fn(self.handler)

        self.__runner.stop()
        self.__text_handler.reset()

    
    def on_player_rigth_click(self): ...
    def on_player_left_click(self): ...
    def on_player_shift(self): ...