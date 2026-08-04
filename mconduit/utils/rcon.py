from typing import Optional, Union, List
import logging
import math

import rcon # type: ignore[import-untyped]


logger = logging.getLogger(__name__)


class Rcon:
    """
    Utility class to send commands to a Minecraft server via Rcon
    """

    server_ip: str
    server_port: int
    rcon_password: str
    timeout: float
    log_errors: bool
    _all_at_once_active: bool
    _suspended_commands: List[str]


    def __init__(
        self,
        server_ip: str,
        server_port: int,
        rcon_password: str,
        timeout: float = 10,
        log_errors: bool = False
    ) -> None:
        """
        Build and connects the client automatically
        """

        self.server_ip = server_ip
        self.server_port = server_port
        self.rcon_password = rcon_password
        self.timeout = timeout
        self.log_errors = log_errors

        self._all_at_once_active = False
        self._suspended_commands = []


    @property
    def _all_at_once(self):
        return self._all_at_once_active
    
    
    @_all_at_once.setter
    def _all_at_once(self, value: bool):

        self._all_at_once_active = value

        if not self._all_at_once_active:

            self.execute(self._suspended_commands)
            self._suspended_commands = []
    

    def all_at_once(self) -> "AllAtOnce":
        """
        Builds a ContextManager that executes all the commands that have been called in it's context at the end
        """

        return AllAtOnce(self)

    
    def _execute(
        self,
        command: Union[List[str], str]
    ) -> Union[List[str], str]:

        timeout = self.timeout * (1 if isinstance(command, str) else math.sqrt(len(command)))

        try:
            with rcon.Client(
                self.server_ip,
                self.server_port,
                passwd=self.rcon_password,
                timeout=timeout
            ) as client:

                if isinstance(command, str):
                    return client.run(command)
                
                outputs = []

                for cmd in command:
                    outputs.append(client.run(cmd))

                return outputs
            
        except rcon.SessionTimeout:
            return ""
        
        except Exception as e:

            if self.log_errors is True:
                
                logger.error(f"Rcon error: {e}")
                logger.error(f"Rcon command: {command}")
        
        return ""


    def execute(
        self,
        command: Union[List[str], str]
    ) -> Optional[Union[List[str], str]]:
        """
        Sends a command to the server.

        It can also sends multiple commands at the same time, but it won't return any output.

        It might fail for some reasons, in that case returns an empty string
        """

        if self._all_at_once_active:

            if isinstance(command, str):
                self._suspended_commands.append(command)
            else:
                self._suspended_commands.extend(command)
            return None
        
        else:
            return self._execute(command)
    
    
    def __call__(
        self,
        command: Union[List[str], str]
    ) -> Optional[Union[List[str], str]]:
        """
        execute() alias, sends a command to the server.

        It might fail for some reasons, in that case returns an empty string
        """

        return self.execute(command)


class AllAtOnce:
    """
    Context manager to execute all Rcon commands all at once at the end
    """

    rcon: Rcon


    def __init__(self, rcon: Rcon) -> None:
        self.rcon = rcon


    def __enter__(self) -> None:
        self.rcon._all_at_once = True

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.rcon._all_at_once = False