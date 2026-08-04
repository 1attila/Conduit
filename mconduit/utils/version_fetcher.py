from typing import Union, Dict, List, Iterator, Optional, TYPE_CHECKING
from tempfile import NamedTemporaryFile
from pathlib import Path
import subprocess
import requests
import gzip
import glob
import time
import re
import os

if TYPE_CHECKING:
    from mconduit.server import Server

EULA_CONTENTS = "# This file indicates acceptance of the Minecraft EULA\n# https://www.minecraft.net/en-us/eula\neula=true\n"

MOJANG_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"

FABRIC_GAME_VERSIONS_URL = "https://meta.fabricmc.net/v2/versions/game"
FABRIC_LOADER_VERSIONS_URL = "https://meta.fabricmc.net/v2/versions/loader"
FABRIC_INSTALLER_VERSIONS_URL = "https://meta.fabricmc.net/v2/versions/installer"


def fetch_vanilla_versions(
    include_snapthots: bool = False,
    include_url: bool = False
) -> Union[List[str], Dict[str, str]]:
    """
    Fetches all the Minecraft vanilla versions with avaiable download
    """

    res = requests.get(MOJANG_MANIFEST_URL)

    try:
        res.raise_for_status()
    except:
        return {} if include_url else []

    manifest = res.json()
    versions: Union[List[str], Dict[str, str]] = {} if include_url else []

    for v in manifest.get("versions", []):

        id = v.get("id")
        
        if not id:
            continue

        if v.get("type") == "snapshot" and not include_snapthots:
            continue
        
        if include_url is True:
            versions[id] = v.get("url")
        else:
            versions.append(id) # type: ignore

    return versions


def fetch_fabric_versions(
    include_snapshots: bool = False,
    include_url: bool = False
) -> Union[List[str], Dict[str, str]]:
    """
    Fetches all the Minecraft vanilla versions with avaiable download
    """

    try:
        game_res = requests.get(FABRIC_GAME_VERSIONS_URL, timeout=10)
        loader_res = requests.get(FABRIC_LOADER_VERSIONS_URL, timeout=10)
        installer_res = requests.get(FABRIC_INSTALLER_VERSIONS_URL, timeout=10)

        game_res.raise_for_status()
        loader_res.raise_for_status()
        installer_res.raise_for_status()

    except requests.RequestException:
        return {} if include_url else []

    game_versions = game_res.json()
    loader_versions = loader_res.json()
    installer_versions = installer_res.json()

    loader = next(v["version"] for v in loader_versions if v["stable"])
    installer = next(v["version"] for v in installer_versions if v["stable"])

    versions: Union[List[str], Dict[str, str]] = {} if include_url else []

    for v in game_versions:

        version = v.get("version")
        stable = v.get("stable", False)

        if not version:
            continue

        if not stable and not include_snapshots:
            continue

        if include_url:

            url = (
                f"https://meta.fabricmc.net/v2/versions/loader/"
                f"{version}/{loader}/{installer}/server/jar"
            )

            versions[version] = url

        else:
            versions.append(version) # type: ignore

    return versions


def fetch_vanilla_url(basic_url: str) -> str:
    """
    fetch_vanilla_versions() doesnt fetch the server.jar download URL.

    To get thr rigth URL a new request has to be made with the URL given by fetch_vanilla_version()

    It's done here, to avoid doing it for every version
    """

    res = requests.get(basic_url)

    try:
        res.raise_for_status()

        meta = res.json()

        return meta.get("downloads", {}).get("server", {}).get("url")
    except Exception as e:
        raise e


def download_server_jar(
    url: str,
    folder: str,
    filename: str = "server.jar",
    chunk_size = 8192
) -> None:
    """
    Downloads a Minecraft server from the given URL at the given path
    """

    folder = Path(folder) # type: ignore
    folder.mkdir(parents=True, exist_ok=True) # type: ignore
    dest_path = folder / filename # type: ignore

    tmp = NamedTemporaryFile(delete=False, dir=str(folder))
    tmp_path = Path(tmp.name)

    try:
        with requests.get(url, stream=True, timeout=30) as resp:

            resp.raise_for_status()
            written = 0

            for chunk in resp.iter_content(chunk_size=chunk_size):

                if len(chunk) > 0:

                    tmp.write(chunk)
                    written += len(chunk)

        tmp.close()
        tmp_path.replace(dest_path)
    
    except Exception as e:

        tmp.close()
        tmp_path.unlink(missing_ok=True)

        raise e


def agree_eula(server_dir: str) -> None:
    """
    Agrees Eula automatically
    """

    server_dir = Path(server_dir) # type: ignore
    server_dir.mkdir(parents=True, exist_ok=True) # type: ignore
    eula_path = server_dir / "eula.txt" # type: ignore
    eula_path.write_text(EULA_CONTENTS, encoding="utf8")


def generate_server_properties(
    server_dir: str,
    *,
    jar_name: str = "server.jar",
    java_cmd: str = "java",
    max_wait: int = 90,
    heap: str = "1G"
) -> Iterator[str]:
    """
    Starts the server so it generates the server.properties file.

    After the file is generated, server process is stopped cleanly
    """

    server_dir = Path(server_dir) # type: ignore
    jar = server_dir / jar_name # type: ignore
    properties = server_dir / "server.properties" # type: ignore

    # needed for logging
    logs_dir = server_dir / "logs" # type: ignore
    world_dir = server_dir / "world" # type: ignore
    libraries_dir = server_dir / "libraries" # type: ignore
    versions_dir = server_dir / "versions" # type: ignore

    if not server_dir.exists(): # type: ignore
        raise RuntimeError("Server directory doesnt exist")

    if not jar.exists(): # type: ignore
        raise RuntimeError(f"{jar} not found")

    cmd = [
        java_cmd,
        f"-Xms{heap}",
        f"-Xmx{heap}",
        "-jar",
        str(jar),
        "nogui",
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=server_dir,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    passed_events = set()

    try:
        start_time = time.time()

        while time.time() - start_time < max_wait:

            if properties.exists():
                break

            if logs_dir.exists() and "logs" not in passed_events:

                passed_events.add("logs")
                yield "Created logs directory"

            if world_dir.exists() and "world" not in passed_events:

                passed_events.add("world")
                yield "Created world directory"

            if libraries_dir.exists() and "libraries" not in passed_events:

                passed_events.add("libraries")
                yield "Created libraries directory"

            if versions_dir.exists() and "versions" not in passed_events:

                passed_events.add("versions")
                yield "Created versions directory"


            if proc.poll() is not None:
                raise RuntimeError("Server exited before generating server.properties")

            time.sleep(0.5)
        else:
            raise RuntimeError("Timeout waiting for server.properties")
        
        assert proc.stdin is not None
        proc.stdin.write("stop\n")
        proc.stdin.flush()

        try:
            proc.wait(timeout=15)
        except:
            proc.terminate()
            proc.wait(timeout=5)

    finally:

        if proc.poll() is None:
            proc.kill()

    yield "Done"


def fetch_server_type(server_path: Path) -> str:
    """
    Returns the server type ("vanilla", "fabric", etc)
    """

    logs_dir = server_path / "logs"

    log_files = []
    latest_log = logs_dir / "latest.log"

    if (latest_log).exists():
        log_files.append(str(latest_log))
        
    if logs_dir.exists():
        
        gz_files = glob.glob(os.path.join(logs_dir, "*.log.gz"))
        gz_files.sort(key=os.path.getmtime, reverse=True)
        log_files.extend(gz_files[:5])

    log_prefix = r"^(\[[^\]]+\]\s*)+:\s*"

    signatures = [
        ("Velocity (Proxy)", r"Velocity .* \d+\.\d+"),
        ("BungeeCord (Proxy)", r"Listening on .*:25577"), 
        ("Purpur", r"This server is running Purpur"),
        ("Pufferfish", r"This server is running Pufferfish"),
        ("Paper", r"This server is running Paper"),
        ("Spigot", r"This server is running .*Spigot"),
        ("CraftBukkit", r"This server is running CraftBukkit"),
        ("Fabric", r"Loading Minecraft .* with Fabric Loader"),
        ("Quilt", r"Loading Minecraft .* with Quilt Loader"),
        ("NeoForge", r"(?:NeoForge mod loading|NeoForge v.* Initialized)"),
        ("Forge", r"(?:Forge mod loading|MinecraftForge v.* Initialized)"),
        ("Sponge", r"SpongePowered")
    ]
    
    compiled_sigs = [(name, re.compile(log_prefix + pattern, re.IGNORECASE)) for name, pattern in signatures]
    vanilla_sig = re.compile(log_prefix + r"Starting minecraft server version", re.IGNORECASE)

    for log_file in log_files:

        try:
            
            open_func = gzip.open if log_file.endswith(".gz") else open

            with open_func(log_file, "rt", encoding="utf-8", errors="ignore") as f:
                found_vanilla_startup = False
                
                for line in f:
                    
                    for name, regex in compiled_sigs:

                        if regex.match(line):
                            return name

                    if vanilla_sig.match(line):
                        found_vanilla_startup = True
                
                if found_vanilla_startup:
                    return "Vanilla"
                    
        except:
            pass
    
    if (server_path / "velocity.toml").exists(): return "Velocity (Proxy)"
    if (server_path / "waterfall.yml").exists(): return "Waterfall (Proxy)"
    if (server_path / "config.yml").exists() and not (server_path / "server.properties").exists(): return "BungeeCord (Proxy)"

    if (server_path / "purpur.yml").exists(): return "Purpur"
    if (server_path / "pufferfish.yml").exists(): return "Pufferfish"
    if (server_path / "config" / "paper-global.yml").exists() or (server_path / "paper.yml").exists(): return "Paper"
    if (server_path / "spigot.yml").exists(): return "Spigot"
    if (server_path / "bukkit.yml").exists(): return "CraftBukkit"

    if (server_path / "fabric-server-launcher.properties").exists() or (server_path / ".fabric").exists(): return "Fabric"
    if (server_path / "libraries" / "net" / "neoforged").exists(): return "NeoForge"
    if (server_path / "libraries" / "net" / "minecraftforge").exists(): return "Forge"
    if (server_path / "user_jvm_args.txt").exists(): return "Forge/NeoForge"

    return "Vanilla"


VERSION_BLOCKS = {
    "1.21": "crafter",
    "1.20": "cherry_log",
    "1.19": "mangrove_log",
    "1.18": "music_disc_otherside",
    "1.17": "azalea",
    "1.16": "crimson_stem",
    "1.15": "honey_block",
    "1.14": "lectern",
    "1.13": "brain_coral",
    "1.12": "white_concrete",
    "1.11": "observer",
    "1.10": "magma_block",
    "1.9": "end_rod",
    "1.8": "diorite",
    "1.7": "black_stained_glass"
}


class UnableToFetchVersion(Exception):
    ...


class VersionFetcher:
    """
    Detects the rigth Minecraft version of the server.

    This is needed mainly due to the changes to the Text API and other json formatting stuffs
    """


    @classmethod
    def is_v1_21_5(cls, server: "Server") -> bool:
        """
        Needed to know how to create the Json Text schema.
        """

        # 1.21.5+ : tellraw @p {"text": "", "click_event": {"action":"suggest_command", "value": ""}}
        # 1.21.4- : tellraw @p {"text": "", "clickEvent": {"action":"suggest_command", "command": ""}}

        output = server.execute("""/tellraw @p {"text": "", "clickEvent": {"action":"suggest_command", "command": ""}}""")
        
        if output is None:
            raise UnableToFetchVersion()
        
        return not output.startswith("""Invalid chat component: No key value in MapLike[{"action":"suggest_command","command":""}]""") # type: ignore
    

    @classmethod
    def check_version(cls, server: "Server") -> Optional[str]:
        """
        Fetches the server version by detecting if some blocks exists.

        Returns None if Rcon doesn't work or the player is not found
        """

        versions_commands = [f"/give @s {item}" for item in VERSION_BLOCKS.values()]
        resp = server.execute(versions_commands)

        for version, r in zip(VERSION_BLOCKS.keys(), resp): # type: ignore

            if r is not None and r == "No player was found": # type: ignore
                return version

        return None