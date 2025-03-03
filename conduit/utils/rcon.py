from rcon import Client


class Rcon:
    """
    Utility class to send commands to a Minecraft server via Rcon
    """

    server_ip: str
    server_port: int
    rcon_password: str
    timeout: float


    def __init__(self,
                 server_ip: str,
                 server_port: int,
                 rcon_password: str,
                 timeout: float = 10
                ) -> "Rcon":
        """
        Build and connects the client automatically
        """

        self.server_ip = server_ip
        self.server_port = server_port
        self.rcon_password = rcon_password
        self.timeout = timeout

    
    def execute(self, command: str) -> str:
        """
        Sends a command to the server.

        It might fail for some reasons, in that case returns an empty string
        """

        try:
            with Client(self.server_ip,
                        self.server_port,
                        passwd=self.rcon_password,
                        timeout=self.timeout) as client:

                return client.run(command)
                
        except Exception as e:
            print(f"Rcon error: {e}")
            print(f"Rcon command: {command}")

            return ""

    
    def __call__(self, command: str) -> str:
        """
        execute() alias, sends a command to the server.

        It might fail for some reasons, in that case returns an empty string
        """

        return self.execute(command)