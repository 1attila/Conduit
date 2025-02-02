from pathlib import Path
from typing import Optional, Union, List, Dict
import json

from .ConduitConfig import HandlerConfig, ServerRunnerConfig, RconConfig


def _get_config(dict: Dict, key: str) -> Union[List, str, int, bool]:
    try:
        return dict[key]
    except KeyError:
        return None
    

def load_server_config(data: Dict, handler_config: Optional[HandlerConfig]) -> ServerRunnerConfig:
    """
    Loads a server config from a json dict
    """

    server_config = ServerRunnerConfig()
    server_config.name = data["name"]
    server_config.path = data["path"]
    server_config.start_command = data["start_command"]
    server_config.high_permissions = data["high_permissions"]

    rcon_config = data["rcon_config"]
    server_config.rcon_config = RconConfig()
    server_config.rcon_config.enable = _get_config(rcon_config, "enable")
    server_config.rcon_config.address = _get_config(rcon_config, "address")
    server_config.rcon_config.port = _get_config(rcon_config, "port")
    server_config.rcon_config.password = _get_config(rcon_config, "password")

    if names := _get_config(data, "names"):
        names.insert(0, data["name"])
        server_config.names = names

    if language := _get_config(data, "language"):
        server_config.language = language
    elif handler_config:
        server_config.language = handler_config.default_language
    else:
        server_config.language = "en_us"

    return server_config


def load_config(file_path: Path="config.json") -> HandlerConfig:
    """
    Loads all handler configs
    """

    data = json.load(open(file_path))

    config = HandlerConfig()
    config.default_language = data["default_language"]
    config.command_prefix = data["command_prefix"]

    for server_config in data["servers"]:
        config.servers_config.append(load_server_config(server_config, config))

    return config