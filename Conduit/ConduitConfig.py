from pathlib import Path
from typing import Optional, List


class RconConfig:
    enable: bool = True
    address: Optional[str] = "127.0.0.1" 
    port: Optional[int] = 25565
    password: Optional[str]  = "password"


class ServerRunnerConfig:
    
    name: str
    names: List[str] = []
    path: Path
    start_command: str = "java -Xms1024M -Xmx2048M -jar server.jar --nogui"
    language: Optional[str] = None
    high_permissions: bool = False
    rcon_config: RconConfig


class HandlerConfig:

    default_language: str = "en_us"
    command_prefix: str = "!!"
    
    servers_config: List[ServerRunnerConfig] = []