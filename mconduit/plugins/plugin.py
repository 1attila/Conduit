from __future__ import annotations
from typing import (
    Callable,
    Optional,
    Union,
    Dict,
    List,
    Tuple,
    Iterable,
    Mapping,
    Type,
    TypeVar,
    Any,
    get_type_hints,
    get_origin,
    get_args,
    TYPE_CHECKING
)
from pathlib import Path
import multiprocessing
import datetime
import logging
import inspect
import types
import copy

from mconduit.plugins.plugin_process import PluginProcess
from mconduit.plugins.plugin_command import Command
from mconduit.plugins.persistent import Persistent, P
from mconduit.plugins.event import EventListener
from mconduit.plugins.config import Config, C
from mconduit.utils import Version, create_plg_debug
from mconduit import constants

if TYPE_CHECKING:
    from mconduit.event import Event
    from mconduit.context import Context
    from mconduit.server import Server
    from mconduit.lang.lang import Lang
    from mconduit.plugin_manager import PluginManager


T = TypeVar("T")


class CommandCompletion:
    """
    Contains all the useful data for the completer
    """
    
    command: str
    description: Optional[str]

    def __init__(self, command: str, description: Optional[str]) -> None:
        
        self.command = command
        self.description = description


class Plugin:
    """
    Conduit Plugin base class

    Inherit this class for every plugin you want to make
    """
    
    _manager: PluginManager
    _metadata: Dict
    _events: Dict[Event, List[Callable]]
    _commands: List[Command]
    _running_processes: List[PluginProcess]
    _server: Server
    _lang: Optional[Lang]
    config: Optional[Config]
    logger: logging.Logger
    persistent: Persistent
    debug: Callable[[Any], None]


    def __init__(
        self,
        manager: PluginManager,
        metadata: Dict,
        lang: Optional[Lang]
    ) -> None:
        
        self._manager = manager
        self._metadata = metadata
        self._server = manager.server
        self._lang = lang
        self.debug = create_plg_debug(self)
        self.logger = logging.getLogger(self.name)
        self._initialize_datas()
        
        self._commands = []
        self._events = {}
        self._running_processes = []

        for item in dir(self.__class__):
            attr = getattr(self.__class__, item)

            if isinstance(attr, Command):
                
                cmd_clone = self._clone_command_tree(attr)
                self._commands.append(cmd_clone)

            elif isinstance(attr, EventListener):
                attr._callback = attr._callback.__get__(self, self.__class__)
                self._events.setdefault(attr._event, []).append(attr._callback)

        try:
            self.on_load()
        except Exception as e:
            raise e
    

    def _initialize_datas(self) -> None:
        """
        Loads the persistent and config classes from the rispective files
        """

        try:
            hints = get_type_hints(self.__class__)
        except:
            hints = getattr(self, "__annotations__", {})

        def extract_base_type(hint: Any, base_class: Type) -> Optional[Type]:

            if isinstance(hint, type) and issubclass(hint, base_class):
                return hint
            
            origin = get_origin(hint)

            if origin is Union or origin is getattr(types, "UnionType", None):

                for arg in get_args(hint):
                    
                    if isinstance(arg, type) and issubclass(arg, base_class):
                        return arg

            return None
        
        config_type = extract_base_type(hints.get("config"), Config)
        persistent_type = extract_base_type(hints.get("persistent"), Persistent)

        if config_type is not None:
            self.config = config_type.load(self)
        else:
            self.config = None

        if persistent_type is not None:
            self.persistent = persistent_type.load(self)
        else:
            self.persistent = Persistent.load(self)

    
    def _clone_command_tree(self, command: Command) -> Command:
        """
        Clones and binds the command `self` argument recursively
        """
        
        cmd_copy = copy.copy(command)

        original_fallback = getattr(command, "_fallback")

        if inspect.ismethod(original_fallback):
            func = original_fallback.__func__
        else:
            func = original_fallback

        try:
            bound = func.__get__(self, self.__class__)
        except Exception:
            bound = original_fallback

        setattr(cmd_copy, "_fallback", bound)

        original_subs = getattr(command, "_subcommands", [])
        new_subs = []

        for sub in original_subs:
            if isinstance(sub, Command):
                new_subs.append(self._clone_command_tree(sub))
            else:
                new_subs.append(sub)

        setattr(cmd_copy, "_subcommands", new_subs)

        return cmd_copy

    
    def __repr__(self) -> str:
        return self.name
    

    @property
    def name(self) -> str:
        """
        Plugin name
        """

        return self._metadata["name"]


    @property
    def version(self) -> Version:
        """
        Plugin version
        """

        return Version.from_string(self._metadata["version"])

    
    @property
    def desc(self) -> str:
        """
        Plugin description
        """
        
        return self._metadata["description"]

    
    @property
    def manager(self) -> PluginManager:
        """
        Plugin manager
        """

        return self._manager
    

    @property
    def lang(self) -> Optional[Lang]:
        """
        Plugin lang
        """

        return self._lang
    

    @property
    def server(self) -> Server:
        """
        Server instance that is running this instance
        """
        
        return self._server
    

    @property
    def servers(self) -> List[Server]:
        """
        All the Server istances that are running this plugin.

        Note: this may change arbitrarly at ANY time
        """

        servers = []
        
        for server in self.server.handler.servers:

            if server.plugin_manager.are_plugins_loaded(self.name):
                servers.append(server)

        return servers
    

    @property
    def events(self) -> Dict[Event, List[Callable]]:
        """
        Plugin events
        """

        return dict(self._events)
    
    
    @property
    def commands(self) -> List[Command]:
        """
        Plugins commands
        """

        return list(self._commands)

    
    @property
    def running_processes(self) -> List[PluginProcess]:
        """
        Threads this plugin currently runs
        """

        return list(self._running_processes)
    
    
    @property
    def path(self) -> Path:
        """
        Path of the folder where this plugin is stored with it's metadata/configs/persistent files
        """

        return Path(constants.PLUGINS_DIR) / self.name

    
    def _search_command_recursively(self, command: Command, sub_names: Tuple[str]) -> Optional[Command]:
        """
        Searches the given subcommand recursively
        """

        for subcommand in command.subcommands:
            
            if sub_names[0] in subcommand.names:
                
                if len(sub_names) == 1:
                    return subcommand

                return self._search_command_recursively(subcommand, sub_names[1:])

        return None

    
    def get_command_named(self, name: str, *sub_names: str) ->  Optional[Command]:
        """
        Returns the command with the given name, if exists.

        If you want to search for a subcommand, just use multiple string (each for one command).

        E.g: `configs modify reset` -> `get_command_named("config", "modify", "reset")`
        """

        for command in self._commands:
            if name in command.names:

                if len(sub_names) == 0:
                    return command
                
                return self._search_command_recursively(command, sub_names) # type: ignore

        return None
    

    def on_load(self) -> None:
        """
        This method is called once this plugin has been created.

        You should overwrite this instead of `__init__()`
        """

    
    def _about_to_stop(self) -> None:
        """
        Stops the running processes of this plugin and calls `about_to_stop()`
        """

        try:
            self.on_unload()
        except:
            pass

        for process in self._running_processes:

            if process.process.is_alive():
                process.process.terminate()

    
    def on_unload(self) -> None:
        """
        This method gets called every time the plugin is about to being stopped, at every OnConduitStop event.

        You can overwrite this to customize it's behaviour
        """
        ...


    def on_plugin_loaded(self, plugin: "Plugin") -> None:
        """
        This method is called every time a plugin is loaded.

        You can overwrite this to customize it's behaviour
        """
        ...


    def on_plugin_unloaded(self, plugin: "Plugin") -> None:
        """
        This method is called every time a plugin is unloaded.

        You can overwrite this to customize it's behaviour
        """
        ...


    def on_plugin_reloaded(self, plugin: "Plugin") -> None:
        """
        This method is called every time a plugin is reloaded.

        You can overwrite this to customize it's behaviour
        """
        ...


    def on_plugin_downloaded(self, plugin_name: str) -> None:
        """
        This method is called every time a plugin is downloaded.

        You can overwrite this to customize it's behaviour
        """
        ...


    def run_process(
        self,
        fn: Callable[[Any], T],
        args: Iterable[Any] = (),
        kwargs: Optional[Mapping[str, Any]] = None,
        *,
        force_stop_after_secs: Optional[float] = None
    ) -> None:
        """
        Runs the given function in a process
        """

        if kwargs is None:
            kwargs = {}
        
        p = multiprocessing.Process(
            target=fn,
            args=args,
            kwargs=kwargs,
            name=f"{self.name}-{fn.__name__}",
            daemon=False
        )

        now = datetime.datetime.now()
        stop_time = None

        if force_stop_after_secs is not None:
            stop_time = now + datetime.timedelta(seconds=force_stop_after_secs)
        
        self._running_processes.append(
            PluginProcess(
                process=p,
                start_time=now,
                stop_time=stop_time
            )
        )
        
        try:
            p.start()
        except:
            pass
    
    
    def _running_check(self) -> bool:
        """
        Called by PluginManager to assert this plugin didn't crash
        """

        return True
    

    def _get_command_completion(self, cmd: List[str], ctx: Context) -> List[str]:
        
        command_completions = []

        for command in self.commands:

            completions = command._get_command_completions(cmd, ctx)
            command_completions.extend(completions)
        
        return command_completions