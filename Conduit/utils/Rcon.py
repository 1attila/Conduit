from typing import Any
from rcon import Client


class Rcon:
    """
    Utility class to send commands to a Minecraft server via Rcon
    """

    server_ip: str
    server_port: int
    rcon_password: str
    timeout: int

    def __init__(self,
                 server_ip: str,
                 server_port: int,
                 rcon_password: str,
                 timeout: int = 10
                ) -> "Rcon":
        
        self.server_ip = server_ip
        self.server_port = server_port
        self.rcon_password = rcon_password
        self.timeout = timeout

    
    def execute(self, command: str) -> str:
        """
        Sends a command to the server.

        It might fail for some reasons but it doesnt throw any error
        """

        try:
            with Client(self.server_ip, self.server_port, self.rcon_password, self.timeout) as client:
                return client.run(command)
        except Exception as e:
            pass

    
    def __call__(self, command: str) -> str:
        """
        execute() alias, sends a command to the server.

        It might fail for some reasons but it doesnt throw any error
        """

        return self.execute(command)