from typing import Callable, Optional, NoReturn, List
import os

from .conduit_config import HandlerConfig
from .server_runner import ServerRunner
from .server import Server
from .cli.cli import Cli
from .Lang.lang import Lang
from .utils.check_annotation import check_annotation


class Handler:
    """
    Handles all the minecraft server processes

    Contains some utility methods to broadcast between servers
    """


    __config: HandlerConfig
    __server_runners: List[ServerRunner]
    __lang: Lang
    __cli: Optional[Cli]


    def __init__(self, config: HandlerConfig, cli: bool=True):
        
        self.__config = config
        self.__server_runners = []

        for server_config in self.__config.servers_config:
            self.__server_runners.append(ServerRunner(server_config, self))
        
        try:
            self.__lang = Lang(os.getcwd() + "\\Conduit\\Resources", self.__config.default_language)
        except ValueError:
            raise ValueError

        if cli:
            self.__cli = Cli(self, self.__lang)


    @property
    def lang(self) -> Lang:
        """
        Main lang
        """

        return self.__lang
    

    def set_lang(self, lang: str):
        """
        Sets the main language
        """

        self.__lang.set_lang(lang)
        self.__config.save()


    @property
    def servers(self) -> List[Server]:
        """
        All the minecraft servers
        """

        return [runner.server for runner in self.__server_runners]
    

    @property
    def command_prefix(self) -> str:
        return self.__config.command_prefix


    def start_servers(self) -> NoReturn:
        """
        Starts all the servers
        """

        self.to_all_servers(lambda s: s.start())


    def stop_servers(self) -> NoReturn:
        """
        Stops all the servers
        """

        self.to_all_servers(lambda s: s.stop())


    def to_all_servers(self, fn: Callable) -> NoReturn:
        """
        Runs the specified lambda for every server.

        lambda must have a parameter wich is the server
        """
        
        for runner in self.__server_runners:
            fn(runner.server)

    
    def event(self, fn: Callable) -> NoReturn:
        """
        Calls the function every time the event of the function name occours.

        The function must only take a single argument of type Context or subclasses of it, depending on the event type
        """

        self.to_all_servers(lambda s: s.event(fn))

    
    def on_player_join(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time player joins.

        The function must only take a single argument of type Context
        """
        
        self.to_all_servers(lambda s: s.on_player_join(fn))


    def on_player_left(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time a player left the server.

        The function must only take a single argument of type Context
        """
        
        self.to_all_servers(lambda s: s.on_player_left(fn))


    def on_player_death(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time a player is killed.

        The function must only take a single argument of type PlayerDeathContext
        """
        
        self.to_all_servers(lambda s: s.on_player_death(fn))


    def on_player_message(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time a player sends a message.

        The function must only take a single argument of type PlayerMessageContext
        """
        
        self.to_all_servers(lambda s: s.on_player_message(fn))


    def on_player_command(self, fn: Callable) -> NoReturn:
        """
        Decorator that calls the function every time a player sends a command.

        The function must only take a single argument of type PlayerCommandContext
        """
        
        self.to_all_servers(lambda s: s.on_player_command(fn))