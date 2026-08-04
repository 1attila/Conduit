from __future__ import annotations
from typing import Optional, Union, Dict, List, TYPE_CHECKING
from pathlib import Path
import threading
import copy

from mconduit.utils.rcon import Rcon, AllAtOnce
from mconduit.text._text_handler import TextHandler
from mconduit._types import Player

if TYPE_CHECKING:
    from mconduit.handler import Handler
    from mconduit.server_runner import ServerRunner
    from mconduit.conduit_config import ServerRunnerConfig


class BaseServer:
    """
    Contains all the attributes needed for the higher-level APIs
    """

    _names: List[str]
    _path: Path
    _runner: ServerRunner
    _config: ServerRunnerConfig
    _rcon: Rcon
    _lock: threading.RLock
    _text_handler: TextHandler
    _players: Dict[str, Player]


    def __init__(
        self,
        runner: ServerRunner
    ) -> None:

        config = runner.config

        self._config = config
        self._path = config.path
        self._names = config.names
        self._runner = runner

        self._rcon = Rcon(
            config.rcon_config.address,
            config.rcon_config.port,
            config.rcon_config.password
        )

        self._lock = threading.RLock()
        self._text_handler = TextHandler(self)
        self._players = {}


    def __repr__(self) -> str:
        return self._names[0]
    
        
    @property
    def name(self) -> str:
        """
        Server main name
        """
    
        return str(self._names[0])
        
    
    @property
    def names(self) -> List[str]:
        """
        All servers names
        """
    
        return list(self._names)
        
    
    @property
    def path(self) -> Path:
        """
        Server folder path
        """
    
        return Path(self._path)
        
    
    @property
    def handler(self) -> Handler:
        """
        Servers handler
        """
    
        return self._runner.handler
        
    
    @property
    def config(self) -> ServerRunnerConfig:
        """
        Copy of Servers config, Rcon and Machine configs are None for security reasons
        """
            
        config = copy.deepcopy(self._config)
        config.rcon_config = None # type: ignore
        config.machine_config = None # type: ignore
    
        return config


    @property
    def online_players(self) -> Dict[str, Player]:
        """
        Players that are currently playing
        """

        return dict(self._players)


    def execute(self, command: Union[List[str], str]) -> Optional[Union[List[str], str]]:
        """
        Executes a command with Rcon
        """
    
        with self._lock:
            return self._rcon(command)
            
    
    def __call__(self, command: Union[List[str], str]) -> Optional[Union[List[str], str]]:
        """
        execute() alis, executes a command with Rcon
        """
    
        return self.execute(command)

    
    def all_at_once(self) -> AllAtOnce:
        """
        Builds a ContextManager that executes all the commands that have been called in it's context at the end
        """

        with self._lock:
            return self._rcon.all_at_once()


    def read_file(
        self,
        relative_path: str | Path
    ) -> Optional[str]:
        """
        Returns the content of the given file.

        This should be used ONLY if the file is located to the server machine (like server.properties)
        """
        
        return self._runner._read_file(relative_path)

    
    def write_file(
        self,
        relative_path: str | Path,
        content: Union[str, bytes]
    ) -> None:
        """
        Writes the given file with the specified content.

        This should be used ONLY if the file is located to the server machine (like server.properties)
        """
        
        self._runner._write_file(relative_path, content)


    def start(self) -> None:
        """
        Starts the server
        """

        raise NotImplementedError
        self._runner.start()


    def stop(self) -> None:
        """
        Stops the server process
        """

        self._runner.stop()