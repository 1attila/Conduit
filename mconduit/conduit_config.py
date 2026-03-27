from typing import Optional, Dict, List
from pathlib import Path
import json
import os


class MachineConfig:
    """
    To access the server if it's on another machine
    """

    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    key_filename: Optional[str]


    def to_json(self) -> Dict:

        machine_config = {
            "host": self.host,
            "port": self.port,
        }

        if self.username is not None:
            machine_config["username"] = self.username

        if self.password is not None:
            machine_config["password"] = self.password
        
        if self.key_filename is not None:
            machine_config["key_filename"] = self.key_filename

        return machine_config
    

class ResourcePackConfig:
    """
    Resource pack config
    """

    server_address: str
    server_port: int
    enabled: bool


    def to_json(self) -> Dict:

        return {
            "server_address": self.server_address,
            "server_port": self.server_port,
            "enabled": self.enabled
        }


class RconConfig:
    """
    Rcon config
    """
    
    address: str
    port: int
    password: str


    def to_json(self) -> Dict:
        
        return {
            "address": self.address,
            "port": self.port,
            "password": self.password
        }


class ServerRunnerConfig:
    """
    Server Config
    """
    
    names: List[str]
    path: Path
    start_command: str
    language: str
    high_permissions: bool
    rcon_config: RconConfig
    resource_pack_config: Optional[ResourcePackConfig]
    machine_config: Optional[MachineConfig]
    

    def to_json(self) -> Dict:

        config_dict = {
            "names": self.names,
            "path": str(self.path),
            "start_command": self.start_command,
            "high_permissions": self.high_permissions,
            "rcon_config": self.rcon_config.to_json()
        }

        if self.resource_pack_config is not None:
            config_dict["resource_pack_config"] = self.resource_pack_config.to_json()

        if self.machine_config is not None:
            config_dict["machine_config"] = self.machine_config.to_json()

        return config_dict


class HandlerConfig:
    """
    Handler config
    """

    default_language: str = "en_us"
    command_prefix: str = "!!"
    collect_telemetry_data: bool = True
    servers_config: List[ServerRunnerConfig] = []


    def to_json(self) -> Dict:

        return {
            "default_language": self.default_language,
            "command_prefix": self.command_prefix,
            "collect_telemetry_data": self.collect_telemetry_data,
            "servers": [config.to_json() for config in self.servers_config]
        }


    def save(self, path: Optional[Path]=None) -> None:
        
        if not path:
            path = Path.cwd() / "config.json"

        with open(path, "w") as f:
            f.write(json.dumps(self.to_json(), indent=4))