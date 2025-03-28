from pathlib import Path
from typing import Optional, Dict
import json
import os

from .conduit_config import HandlerConfig, ServerRunnerConfig, RconConfig
from .config_setup import find_servers, fetch_rcon_config
from .lang.lang import Lang


def load_server_config(data: Dict, handler_config: Optional[HandlerConfig]) -> ServerRunnerConfig:
    """
    Loads a server config from a json dict
    """

    server_config = ServerRunnerConfig()
    server_config.name = data["name"]
    server_config.path = data["path"]
    server_config.start_command = data.get("start_command", f"java -Xms1024M -Xmx2048M -jar {server_config.path}\\server.jar --nogui")
    server_config.high_permissions = data.get("high_permissions", False)

    rcon_config = data.get("rcon_config", {})
    server_config.rcon_config = RconConfig()
    server_config.rcon_config.address = rcon_config.get("address")
    server_config.rcon_config.port = rcon_config.get("port")
    server_config.rcon_config.password = rcon_config.get("password")

    if not (
        server_config.rcon_config.address or
        server_config.rcon_config.port or
        server_config.rcon_config.password
        ):
        server_config.rcon_config = fetch_rcon_config(server_config.path)
    
    if names := data.get("names"):
        names.insert(0, data["name"])
        server_config.names = names

    if language := data.get("language"):
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

    l = Lang(os.getcwd() + "\\Conduit\\Resources", config.default_language)

    if not len(data["servers"]):

        print(l["No server was found in <file_path>", file_path])
        print(l["Do you want conduit to find them for you (Y/N)?"])
        find = input(l["proceed? >"]) or ""

        if find.lower().strip() in ["1", "true", "y", "yes"]:

            print(l["Finding all possible servers, this operation can take some time"])

            for path in find_servers():
                
                print(l["Found one at <path> how should be called? (press send to skip)", path])
                name = input("server.name > ") or ""

                if len(name.strip()) > 0:
                    data["servers"].append({"name": name, "path": path})

            print(l["Found all possible servers"])

        else:
            raise RuntimeError("Missing server config")

    for server_config in data["servers"]:
        config.servers_config.append(load_server_config(server_config, config))

    config.save(file_path)

    return config