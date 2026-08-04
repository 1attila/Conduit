from typing import Optional, Dict, List, Iterator
from pathlib import Path
import platform
import random
import os

from mconduit.conduit_config import ServerRunnerConfig
from mconduit.server_api import Properties


def generate_rcon_password(length: int = 10) -> str:
    """
    Generates a random password for Rcon
    """

    CHARS = "ABCDEFGHILMNOPQRSTUVZWJYKXabcdefghilmnopqrstuvzwjykx1234567890"

    return "".join([CHARS[random.randrange(0, len(CHARS) - 1)] for _ in range(length)])


def get_ip_port_mappings(
    servers_configs: List[ServerRunnerConfig]
) -> Dict[str, List[int]]:
    
    mappings: Dict[str, List[int]] = {}

    for config in servers_configs:
        
        server_prop = Properties(path=config.path)
        server_port = int(server_prop.get("server-port"))
        
        mappings.setdefault(config.rcon_config.address, []).extend([int(config.rcon_config.port), server_port])

    return mappings


def get_port(
    ip: str,
    default_port: int,
    *,
    configs: Optional[List[ServerRunnerConfig]] = None,
    mappings: Optional[Dict[str, List[int]]] = None
) -> int:
    """
    Generates the server port (for rcon too) for the given server ip.

    It checks for all servers that have the same ip and chooses different ports
    """
    
    if configs is not None:
        mappings = get_ip_port_mappings(configs)
    
    assert mappings is not None
    
    used_ports: List[int] = []
    
    for s_ip, ports in mappings.items():

        if s_ip == ip:
            used_ports.extend(ports)
    
    port = int(default_port)

    while port in used_ports and port < 65533:
        port += 1

    if port not in used_ports:
        return port
    
    port = default_port - 1

    while port in used_ports and port > 2:
        port -= 1

    if port not in used_ports:
        return port
    
    raise RuntimeError("Unable to set a new port!")


def get_root_dirs() -> List[str]:
    """
    Returns a list of root directories to scan depending on the operative system
    """

    if platform.system() == "Windows":
        
        import string
        from ctypes import windll

        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()

        for letter in string.ascii_uppercase:

            if bitmask & 1:
                drives.append(f"{letter}:\\")

            bitmask >>= 1

        return drives
    else:
        return ["/"]
    

def find_servers() -> Iterator[Path]:

    REQUIRED_FILES = {"server.properties", "eula.txt"}
    IGNORED_DIRS = {
        'Windows', 'Program Files', 'Program Files (x86)', 'ProgramData',
        '$Recycle.Bin', 'System Volume Information', 'proc', 'sys', 'dev', 
        'node_modules', '.git', '.idea', '__pycache__', 'AppData'
    }

    roots = get_root_dirs()

    for start_dir in roots:

        try:

            for root, dirs, files in os.walk(start_dir, topdown=True):

                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith('.')]

                if REQUIRED_FILES.issubset(files):
                    yield Path(root).absolute()

        except (OSError, PermissionError):
            continue