from typing import Optional, NoReturn, List, TYPE_CHECKING
from pathlib import Path

from .ServerDataFetch import ServerDataFetchAPI
from .utils.Rcon import Rcon

if TYPE_CHECKING:
    from .ServerRunner import ServerRunner
    from .ConduitConfig import ServerRunnerConfig
    from .Handler import Handler


class Server(ServerDataFetchAPI):
    """
    Minecraft server interface

    Contains all the fetching and rcon API and some useful attributes 
    """

    __name: str
    __names: Optional[List[str]]
    __path: Path
    __rcon: Optional[Rcon] = None
    __runner: "ServerRunner"
    __config: "ServerRunnerConfig"


    def __init__(self, runner: "ServerRunner") -> "Server":

        config = runner.config
        self.__runner = runner
        self.__config = config
        self.__path = config.path
        self.__name = config.name
        self.__names = config.names
        
        if config.rcon_config.enable:
            self.__rcon = Rcon(
                config.rcon_config.address,
                config.rcon_config.port,
                config.rcon_config.password
            )
        
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
        Servers config
        """

        return self.config
    
    
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

    
    def execute(self, command: str) -> Optional[str]:
        """
        Executes a command with Rcon
        """

        if self.__rcon:
            return self.__rcon(command)
        else:
            return None
        

    def __call__(self, command: str) -> Optional[str]:
        """
        execute() alis, executes a command with Rcon
        """

        return self.execute(command)
    
    # Events
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