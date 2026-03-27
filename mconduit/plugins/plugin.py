from typing import (
    Callable,
    Optional,
    Dict,
    List,
    Tuple,
    Iterable,
    Mapping,
    Generic,
    Type,
    TypeVar,
    Any,
    get_origin,
    get_args,
    TYPE_CHECKING
)
from pathlib import Path
import multiprocessing
import datetime
import logging
import inspect
import copy

from .plugin_process import PluginProcess
from .plugin_command import Command
from .persistent import Persistent, P
from .event import EventListener
from .config import Config, C
from  .. import constants

if TYPE_CHECKING:
    from ..event import Event
    from ..context import Context
    from ..server import Server
    from ..lang.lang import Lang
    from ..plugin_manager import PluginManager


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


class Plugin(Generic[C, P]):
    """
    Conduit Plugin base class

    Inherit this class for every plugin you want to make
    """
    
    __manager: "PluginManager"
    __metadata: Dict
    __events: Dict["Event", List[Callable]]
    __commands: List[Command]
    __running_processes: List[PluginProcess]
    __server: "Server"
    __lang: Optional["Lang"]
    __config: Optional[Type[C]]
    logger: logging.Logger
    persistent: Type[P]


    def __init__(
        self,
        manager: "PluginManager",
        metadata: Dict,
        lang: Optional["Lang"]
    ) -> None:
        
        self.__manager = manager
        self.__metadata = metadata
        self.__server = manager.server
        self.__lang = lang
        self.__config = None
        self.logger = logging.getLogger(self.name)
        self._initialize_datas()
        
        self.__commands = []
        self.__events = {}
        self.__running_processes = []

        for item in dir(self.__class__):
            attr = getattr(self.__class__, item)

            if isinstance(attr, Command):
                
                cmd_clone = self._clone_command_tree(attr)
                self.__commands.append(cmd_clone)

            elif isinstance(attr, EventListener):
                attr._callback = attr._callback.__get__(self, self.__class__)
                self.__events.setdefault(attr._event, []).append(attr._callback)

        try:
            self.on_load()
        except Exception as e:
            raise e
    

    def _initialize_datas(self) -> None:
        """
        Loads the persistent and config classes from the rispective files
        """

        for base in type(self).__orig_bases__: # type: ignore

            if get_origin(base) is Plugin:

                args = get_args(base)

                if args is not None:

                    for arg in args:
                        
                        if arg is None:
                            continue

                        if isinstance(arg, type) and issubclass(arg, Config):
                            self.__config = arg.load(self) # type: ignore

                        elif isinstance(arg, type) and issubclass(arg, Persistent):
                            self.persistent = arg.load(self) # type: ignore

        if not hasattr(self, "persistent"):
            self.persistent = Persistent.load(self)

    
    def _clone_command_tree(self, command: Command) -> Command:
        """
        Clones and binds the command `self` argument recursively
        """
        
        cmd_copy = copy.copy(command)

        original_fallback = getattr(command, "_Command__fallback")

        if inspect.ismethod(original_fallback):
            func = original_fallback.__func__
        else:
            func = original_fallback

        try:
            bound = func.__get__(self, self.__class__)
        except Exception:
            bound = original_fallback

        setattr(cmd_copy, "_Command__fallback", bound)

        original_subs = getattr(command, "_Command__subcommands", [])
        new_subs = []

        for sub in original_subs:
            if isinstance(sub, Command):
                new_subs.append(self._clone_command_tree(sub))
            else:
                new_subs.append(sub)

        setattr(cmd_copy, "_Command__subcommands", new_subs)

        return cmd_copy

    
    def __repr__(self) -> str:
        return self.name
    

    @property
    def name(self) -> str:
        """
        Plugin name
        """

        return self.__metadata["name"]


    @property
    def version(self) -> str:
        """
        Plugin version
        """

        return self.__metadata["version"]

    
    @property
    def desc(self) -> str:
        """
        Plugin description
        """
        
        return self.__metadata["description"]

    
    @property
    def manager(self) -> "PluginManager":
        """
        Plugin manager
        """

        return self.__manager
    

    @property
    def lang(self) -> Optional["Lang"]:
        """
        Plugin lang
        """

        return self.__lang
    

    @property
    def config(self) -> Optional[Type[C]]:
        """
        Plugin config, if any
        """

        return self.__config
    

    @property
    def server(self) -> "Server":
        """
        Server instance that is running this instance
        """
        
        return self.__server
    

    @property
    def servers(self) -> List["Server"]:
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
    def events(self) -> Dict["Event", List[Callable]]:
        """
        Plugin events
        """

        return self.__events
    
    
    @property
    def commands(self) -> List[Command]:
        """
        Plugins commands
        """

        return self.__commands

    
    @property
    def running_processes(self) -> List[PluginProcess]:
        """
        Threads this plugin currently runs
        """

        return self.__running_processes
    
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

    
    def get_command_named(self, name: str, *sub_names: str) ->  Optional[Command]:
        """
        Returns the command with the given name, if exists.

        If you want to search for a subcommand, just use multiple string (each for one command).

        E.g: `configs modify reset` -> `get_command_named("config", "modify", "reset")`
        """

        for command in self.__commands:
            if name in command.names:

                if len(sub_names) == 0:
                    return command
                
                return self._search_command_recursively(command, sub_names)
    

    def on_load(self) -> None:
        """
        This method is called once this plugin has been created.

        You should overwrite this instead of __init__()
        """

    
    def _about_to_stop(self) -> None:
        """
        Stops the running processes of this plugin and calls about_to_stop()
        """

        try:
            self.on_unload()
        except:
            pass

        for process in self.__running_processes:

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
        args: Iterable[Any]=(),
        kwargs: Optional[Mapping[str, Any]]=None,
        *,
        force_stop_after_secs: Optional[float]=None
    ) -> None:
        """
        Runs the given function in a process
        """
        
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
        
        self.__running_processes.append(
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
    

    def _get_command_completion(self, cmd: List[str], ctx: "Context") -> List[str]:
        
        command_completions = []

        for command in self.commands:

            completions = command._get_command_completions(cmd, ctx)
            command_completions.extend(completions)
        
        return command_completions