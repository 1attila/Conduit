from pathlib import Path
from typing import NoReturn, Optional, Dict, List
import json
import os


class RconConfig:
    
    address: Optional[str] = "127.0.0.1" 
    port: Optional[int] = 25565
    password: Optional[str]  = "password"

    def to_json(self) -> Dict:
        
        return {
            "address": self.address,
            "port": self.port,
            "password": self.password
        }


class ServerRunnerConfig:
    
    name: str
    names: List[str] = []
    path: Path
    start_command: str = "java -Xms1024M -Xmx2048M -jar server.jar --nogui"
    language: str = "en_us"
    high_permissions: bool = False
    rcon_config: RconConfig

    def to_json(self) -> Dict:

        return {
            "name": self.name,
            "names": self.names[1:],
            "path": self.path,
            "start_command": self.start_command,
            "high_permissions": self.high_permissions,
            "rcon_config": self.rcon_config.to_json()
        }


class HandlerConfig:

    default_language: str = "en_us"
    command_prefix: str = "!!"
    
    servers_config: List[ServerRunnerConfig] = []
    
    def to_json(self) -> Dict:

        return {
            "default_language": self.default_language,
            "command_prefix": self.command_prefix,
            "servers": [config.to_json() for config in self.servers_config]
        }


    def save(self, path: Optional[Path]=None) -> NoReturn:
        
        if not path:
            path = os.getcwd() + "\\config.json"

        with open(path, "w") as f:
            f.write(json.dumps(self.to_json(), indent=4))