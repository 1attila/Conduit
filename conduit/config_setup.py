from typing import NoReturn, Optional, List
from pathlib import Path
import os

import configparser

from .conduit_config import RconConfig


def _find_servers_recursive(directory: str, server_list: List) -> NoReturn:
    
    for root, dirs, files in os.walk(directory):
        
        for dir in dirs:
            _find_servers_recursive(dir, server_list)

        if {"server.jar", "server.properties", "eula.txt"}.issubset(files):
            server_list.append(str(Path(root).absolute()))


def find_servers() -> List[str]:
    """
    Finds all the possible servers across all the machine
    """

    server_list = []
    start_dir = str(Path(os.getcwd()).absolute().root)

    for dir in os.listdir(start_dir):
        if os.path.isdir(start_dir + dir):
            
            _find_servers_recursive(start_dir + dir, server_list)

    return server_list


def fetch_rcon_config(server_path: Path) -> Optional[RconConfig]:
    """
    Builds RconConfig fetching data from server.properties if possible
    """

    with open(server_path + "\\server.properties") as f:

        prop_data = "[dummy-section]\n" + f.read()
        c = configparser.RawConfigParser()
        c.read_string(prop_data)

        prop = dict(c["dummy-section"])

        rcon_port = prop.get("rcon.port")
        rcon_passwd = prop.get("rcon.password")
        server_ip = prop.get("server-ip")

        if rcon_port and rcon_passwd:

            rcon_port = int(rcon_port.strip())
            rcon_passwd = rcon_passwd.strip()
            server_ip = server_ip.strip()

            if not server_ip:
                server_ip = "127.0.0.1"

            if rcon_port and rcon_passwd:

                config = RconConfig()
                config.address = server_ip
                config.port = rcon_port
                config.password = rcon_passwd

                return config