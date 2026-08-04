from typing import Optional, Dict
from pathlib import Path, PurePosixPath
import logging
import shutil
import json
import os

from mconduit.conduit_config import (
    HandlerConfig,
    ServerRunnerConfig,
    RconConfig,
    ResourcePackConfig,
    MachineConfig
)
from mconduit.config_setup import generate_rcon_password
from mconduit.server_api import Properties
from mconduit.constants import CONDUIT_PATH


logger = logging.getLogger("mconduit-config-syncer")

DEFAULT_CONFIG = {
    "default_language": "en_us",
    "command_prefix": "!!",
    "servers": []
}


def sync_rcon_config(
    server_path: Path,
    old_config: RconConfig
) -> RconConfig:
    """
    Syncs server rcon configs present in configs.json with server.properties.

    If a field is missing a default value is set in both configs.json and server.properties
    """

    prop = Properties(path=server_path)

    ip: str = prop.get("server-ip", None)

    if ip is None:
        ip = "127.0.0.1"
        
    port = prop.get("rcon.port", "25575")

    if port == "":

        port = 25575 # type: ignore
        
        print("Setting rcon port")
        prop.set("rcon.port", 25575)

    password = prop.get("rcon.password", generate_rcon_password())
        
    if password == "":

        password = generate_rcon_password()
        logger.info("Setting rcon password")

        prop.set("rcon.password", password)

    if ip != old_config.address and old_config.address != "127.0.0.1":

        logger.info("Synced server ip")
        old_config.address = ip

    if int(port) != old_config.port:

        logger.info("Synced rcon port")
        old_config.port = int(port)
    
    if password != old_config.password:

        logger.info("Synced rcon password")
        old_config.password = password
    
    if prop.get("enable-rcon", False) is False:

        logger.info("Set 'enable-rcon' from 'false' to 'true'")
        prop.set("enable-rcon", True)

    return old_config


def load_server_config(
    data: Dict,
    handler_config: Optional[HandlerConfig]
) -> ServerRunnerConfig:
    """
    Loads a server config from a json dict
    """

    server_config = ServerRunnerConfig()
    server_config.names = data["names"]

    path_type = PurePosixPath if data.get("machine_config", None) else Path
    server_config.path = path_type(data["path"]) # type: ignore

    start_command_path = os.path.join(server_config.path, "server.jar")
    server_config.start_command = data.get("start_command", f"java -Xms1024M -Xmx2048M -jar {start_command_path} --nogui")

    server_config.high_permissions = data.get("high_permissions", False)

    rcon_config = data.get("rcon_config", {})
    server_config.rcon_config = RconConfig()
    server_config.rcon_config.address = rcon_config.get("address", None)
    server_config.rcon_config.port = rcon_config.get("port", None)
    if server_config.rcon_config.port is not None:
        server_config.rcon_config.port = int(server_config.rcon_config.port)
    server_config.rcon_config.password = rcon_config.get("password", None)

    if resource_data := data.get("resource_pack_config", None):

        resource_config = ResourcePackConfig()
        resource_config.enabled = resource_data.get("enabled", True)
        resource_config.server_address = resource_data.get("server_address", "127.0.0.1")
        resource_config.server_port = resource_data.get("server_port", 8000)

        server_config.resource_pack_config = resource_config
    else:
        server_config.resource_pack_config = None

    if machine_data := data.get("machine_config", None):
        
        machine_config = MachineConfig()
        machine_config.host = machine_data.get("host", None)
        machine_config.port = machine_data.get("port", 22)
        machine_config.username = machine_data.get("username", None)
        machine_config.password = machine_data.get("password", None)
        machine_config.key_filename = machine_data.get("key_filename", None)

        if not (machine_config.host and machine_config.username):
            raise RuntimeError("Machine config incompleted!")
        
        server_config.machine_config = machine_config
    else:

        server_config.rcon_config = sync_rcon_config(server_config.path, server_config.rcon_config)
        server_config.machine_config = None

    if language := data.get("language"):
        server_config.language = language
    elif handler_config:
        server_config.language = handler_config.default_language
    else:
        server_config.language = "en_us"

    return server_config


def setup_resources() -> None:
    """
    Creates the `resources` folder and pastes `en_us.yml`, `death_messages.json` and `player_actions.json`
    """

    resources_dir = Path("resources")
    resources_path = CONDUIT_PATH.joinpath("resources")

    resources_dir.mkdir(exist_ok=True, parents=True)

    for item in resources_path.iterdir():

        dest = resources_dir / item.name

        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    pycache_path = resources_dir / "__pycache__"

    if pycache_path.exists():
        shutil.rmtree(pycache_path)
    

def load_config(
    file_path: str = "config.json"
) -> Optional[HandlerConfig]:
    """
    Loads all handler configs
    """

    setup_resources()

    if not Path(file_path).exists():
        return # type: ignore
    
    try:
        data = json.load(open(file_path))
    except:
        return # type: ignore 

    config = HandlerConfig()
    config.default_language = data["default_language"]
    config.command_prefix = data["command_prefix"]
    config.collect_telemetry_data = data.get("collect_telemetry_data", True)

    for server_config in data["servers"]:
        config.servers_config.append(load_server_config(server_config, config))

    config.save(Path(file_path))

    return config