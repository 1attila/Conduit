from typing import Callable, Optional, NoReturn, List
import os

from .ConduitConfig import HandlerConfig
from .ServerRunner import ServerRunner
from .Server import Server
from .cli.Cli import Cli
from Conduit.Lang.Lang import Lang


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
            self.__server_runners.append(ServerRunner(server_config))
        
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
        self.__lang.set_lang(lang)


    @property
    def servers(self) -> List[Server]:
        """
        All the minecraft servers
        """

        return [runner.server for runner in self.__server_runners]


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


    def add_server(self):
        ...

    def remove_server(self):
        ...


    def to_all_servers(self, fn: Callable) -> NoReturn:
        """
        Runs the specified lambda for every server.

        lambda must have a parameter wich is the server
        """
        
        for runner in self.__server_runners:
            fn(runner.server)


    def on_player_joined(): ...
    def on_player_leave(): ...
    def on_player_chat(): ...
    def on_player_command(): ...
    def on_player_death(): ...
    def on_player_rigth_click(): ...
    def on_player_left_click(): ...
    def on_player_shift(): ...
    def on_player_move(): ...
    def on_player_shift(): ...
    def on_player_rotate(): ...