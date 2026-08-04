from __future__ import annotations
from typing import Optional, Callable, List, Dict, Any, TYPE_CHECKING
from pathlib import Path
import traceback
import parse # type: ignore[import-untyped]

from mconduit.server_api import ServerAPI
from mconduit.event_handler import EventHandler
from mconduit.utils.version import Version
from mconduit.utils.version_fetcher import VersionFetcher
from mconduit.utils.check_annotation import check_annotation
from mconduit.perms.manager import PermissionManager
from mconduit.resource_pack import ResourcePack
from mconduit.lang.lang import Lang
from mconduit.plugin_manager import PluginManager
from mconduit.event import Event, SERVER_EVENTS
from mconduit.context import Context
from mconduit._types import Player

from mconduit._types import EventFunc

if TYPE_CHECKING:
    from mconduit.server_runner import ServerRunner
    from mconduit.handler import Handler


class Server(ServerAPI):
    """
    Minecraft server interface

    Contains all the fetching and Rcon API and some useful attributes 
    """


    _event_handler: EventHandler
    _slots: Dict[Event, List[EventFunc]]
    _plugin_manager: PluginManager
    _perm_manager: PermissionManager
    _is_running: bool
    _is_v1_21_5: bool
    _lang: Lang
    _resource_pack: ResourcePack
    _version: Optional[Version]


    def __init__(
        self,
        runner: ServerRunner
    ) -> None:

        super().__init__(runner)

        config = runner.config

        self._slots = {event: [] for event in Event}

        self._version = None
        self._perm_manager = PermissionManager(self)

        def on_start(self: Server):

            self._is_running = True
            self.execute("/gamerule sendCommandFeedback false")
            self._is_v1_21_5 = VersionFetcher.is_v1_21_5(self)
            self.execute("/scoreboard objectives add mconduit-sneak minecraft.custom:minecraft.sneak_time")
            self.execute("save-off")
            
            version = VersionFetcher.check_version(self)

            if version is not None:
                self._version = Version.from_string(version)
            
            self._text_handler.reset()
            self._resource_pack._serve()

            self._players = {player.name: player for player in self.fetch_online_players()}
        
        def on_stop(self: Server):
            self._is_running = False
            self._resource_pack._stop_and_update()

        self._slots[Event.SERVER_START].append(on_start)
        self._slots[Event.SERVER_STOP].append(on_stop)
        self._slots[Event.PLAYER_JOIN].append(lambda c: self._players.setdefault(c.player.name, c.player))
        self._slots[Event.PLAYER_LEFT].append(lambda c: self._players.pop(c.player.name))
        
        self._event_handler = EventHandler(self)

        self._slots[Event.GAME_SAVED].append(
            lambda s: (
                self._world_snapshot.sync_world_copy(), # type: ignore
                self._world_reader.clear_cache(),       # type: ignore
                self._scoreboard_reader.clear_cache()   # type: ignore
            )
        )

        self.handler.parallel_tasks.add_task(self._world_snapshot.tick_save)
        self._is_running = self.seed is not None
        self._is_v1_21_5 = False # PlaceHolder

        self._lang = Lang(Path.cwd() / "resources", config.language) # NOTE: This may raise
        self._resource_pack = ResourcePack(self)

        if self._is_running:
            on_start(self)
        else:
            self._resource_pack._stop_and_update()
        
        self._plugin_manager = PluginManager(self)
    

    @property
    def event_handler(self) -> EventHandler:
        """
        Server event handler
        """

        return self._event_handler


    @property
    def plugin_manager(self) -> PluginManager:
        """
        Server plugin manager
        """

        return self._plugin_manager

    
    @property
    def permissions(self) -> Dict[str, List[str]]:
        """
        Permission -> players
        """

        return self._perm_manager.perms
    

    @property
    def permission_manager(self) -> PermissionManager:
        """
        Server permission manager
        """

        return self._perm_manager


    @property
    def is_running(self) -> bool:
        """
        True if the Minecraft server is running with Rcon enabled, False otherwise
        """

        with self._lock:
            
            self._is_running = self.seed is not None

            return self._is_running


    @property
    def slots(self) -> Dict[Event, List[EventFunc]]:
        return dict(self._slots)


    @property
    def seed(self) -> Optional[int]:
        """
        Retrieves the server seed with Rcon.
        """

        res = self.execute("/seed")
        
        if res is not None and len(res) > 0:

            res = res[7:-2]
            return int(res) # type: ignore
        
        return None


    @property
    def is_v1_21_5(self) -> bool:
        """
        Returns True, if the server version >= 1.21.5

        This exists mainly due to debug purposes, since Json Text has changed since 1.21.5+
        """

        return self._is_v1_21_5
    

    @property
    def resource_pack(self) -> ResourcePack:
        """
        Server resource pack.

        Can be used to add custom sounds/textures etc.

        Note: To apply changes you must restart the server!
        """

        return self._resource_pack


    @property
    def version(self) -> Optional[Version]:
        """
        Minecraft server version, if avaiable
        """

        return self._version


    @property
    def lang(self) -> Lang:
        """
        Server language
        """

        return self._lang
    

    def set_lang(self, lang: str) -> bool:
        """
        Sets the main language to the server and all it's plugins.

        Updates configs aswell
        """
        
        with self._lock:
        
            if self._lang.set_lang(lang):

                self._runner.handler._config.save()
                self._plugin_manager.set_lang(lang)

                return True

        return False


    def fetch_online_players(self) -> List[Player]:
        """
        Retrieves all the players online with Rcon.

        Note: use `online_players` attribute if you want to get a list of all the online players.

        Heavily inspired from https://github.com/TISUnion/ChatBridge/blob/master/chatbridge/impl/online/entry.py
        """

        formatters = (
            r"There are {amount:d} of a max {limit:d} players online:{players}",  # <1.16
            r"There are {amount:d} of a max of {limit:d} players online:{players}",  # >=1.16
        )

        response = self.execute("/list")

        for formatter in formatters:
            parsed_response = parse.parse(formatter, response)

            if parsed_response is not None and parsed_response["players"].startswith(" "):
                                
                players = parsed_response["players"][1:]

                if len(players) > 0:

                    player_list = players.split(", ")
                    
                    return [Player(name, self) for name in player_list]

        return []


    def get_permissions_for(self, player_name: str) -> List[str]:

        return self.permission_manager.get_player_perms(player_name)

    
    def _add_event_fallback(
        self,
        event: Event,
        fallback: EventFunc
    ) -> None:
        """
        Adds the given fallback to the specified event name.

        This function exist only to be called by the Plugin to link it's events
        """

        with self._lock:
            self._slots.setdefault(event, []).append(fallback)
    

    def event(self, fn: EventFunc) -> None:
        """
        Calls the function every time the event of the function name occours.

        The function must only take a single argument of type Context
        """
        
        match fn.__name__:
            case "on_player_join":
                self.on_player_join(fn) # type: ignore
            case "on_player_left":
                self.on_player_left(fn) # type: ignore
            case "on_player_death":
                self.on_player_death(fn) # type: ignore
            case "on_player_message":
                self.on_player_message(fn) # type: ignore
            case "on_player_command":
                self.on_player_command(fn) # type: ignore
            case "on_server_start":
                self.on_server_start(fn) # type: ignore
            case "on_server_stop":
                self.on_server_stop(fn) # type: ignore
            case _:
                raise Exception("The function name doesn't match any event name!")


    def on_player_join(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time player joins.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self._slots[Event.PLAYER_JOIN].append(fn)


    def on_player_left(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time a player left the server.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self._slots[Event.PLAYER_LEFT].append(fn)


    def on_player_death(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time a player is killed.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self._slots[Event.PLAYER_DEATH].append(fn)


    def on_player_message(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time a player sends a message.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self._slots[Event.PLAYER_CHAT].append(fn)


    def on_player_command(self, fn: Callable[[Context], Any]) -> None:
        """
        Decorator that calls the function every time a player sends a command.

        The function must only take a single argument of type Context
        """
        
        if check_annotation(fn, Context):
            self._slots[Event.PLAYER_COMMAND].append(fn)

    
    def on_conduit_start(self, fn: Callable[[Handler], Any]) -> None:
        """
        Decorator that calls the function every time conduit is started.

        The function must only take a single argument of type Handler
        """

        if check_annotation(fn, "Handler"):
            self._slots[Event.CONDUIT_START].append(fn)


    def on_conduit_stop(self, fn: Callable[[Handler], Any]) -> None:
        """
        Decorator that calls the function every time conduit is about to stop.

        The function must only take a single argument of type Handler
        """

        if check_annotation(fn, "Handler"):
            self._slots[Event.CONDUIT_STOP].append(fn)

    
    def on_server_start(self, fn: Callable[[Server], Any]) -> None:
        """
        Decorator that calls the function every time a server is started.

        The function must only take a single argument of type Server
        """

        if check_annotation(fn, Server):
            self._slots[Event.SERVER_START].append(fn)


    def on_server_stop(self, fn: Callable[[Server], Any]) -> None:
        """
        Decorator that calls the function every time a server stops.

        The function must only take a single argument of type Server
        """

        if check_annotation(fn, Server):
            self._slots[Event.SERVER_STOP].append(fn)

    
    def _on_player_event(self, ctx: Context) -> None:
        """
        Dispatches player events and calls them
        """

        for fn in self._slots[ctx.event_type]:

            try:
                if ctx.event_type in SERVER_EVENTS:
                    fn(ctx.server) # type: ignore
                else:
                    # NOTE: Conduit events are not sent here
                    # this method is called only by event_handler which recieves only logs events
                    fn(ctx) # type: ignore
            except:
                traceback.print_exc()

    
    def _on_conduit_start(self) -> None:
        """
        Handles ConduitStart event
        """

        for fn in self._slots[Event.CONDUIT_START]:
            fn(self.handler) # type: ignore


    def _join_input_thread(self) -> None:
        """
        Joins the server input loop thread
        """

        for fn in self._slots[Event.CONDUIT_STOP]:
            fn(self.handler) # type: ignore

        self._runner.stop()
        self._text_handler.reset()

    
    def on_player_rigth_click(self): ...
    def on_player_left_click(self): ...
    def on_player_shift(self): ...