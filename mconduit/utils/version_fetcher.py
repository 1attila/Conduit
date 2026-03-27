from typing import Union, Dict, List, Iterator, Optional, TYPE_CHECKING
from tempfile import NamedTemporaryFile
from pathlib import Path
import subprocess
import requests
import time

if TYPE_CHECKING:
    from ..server import Server

EULA_CONTENTS = "# This file indicates acceptance of the Minecraft EULA\n# https://www.minecraft.net/en-us/eula\neula=true\n"
MOJANG_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"


def fetch_vanilla_versions(
    include_snapthots: bool = False,
    include_url: bool = False
) -> Union[List[str], Dict[str, str]]:
    """
    Fetches all the Minecraft versions with avaiable download.
    """

    res = requests.get(MOJANG_MANIFEST_URL)

    try:
        res.raise_for_status()
    except:
        return {} if include_url else []

    manifest = res.json()
    versions = {} if include_url else []

    for v in manifest.get("versions", []):

        id = v.get("id")
        
        if not id:
            continue

        if v.get("type") == "snapshot" and not include_snapthots:
            continue
        
        if include_url is True:
            versions[id] = v.get("url")
        else:
            versions.append(id)

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

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    dest_path = folder / filename

    tmp = NamedTemporaryFile(delete=False, dir=str(folder))
    tmp_path = Path(tmp.name)

    try:
        with requests.get(url, stream=True, timeout=30) as resp:

            resp.raise_for_status()

            total = resp.headers.get("Content-Length")
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

    server_dir = Path(server_dir)
    server_dir.mkdir(parents=True, exist_ok=True)
    eula_path = server_dir / "eula.txt"
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

    server_dir = Path(server_dir)
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


#Unknown item 'minecraft:lol'
# give @s lol
# No player was found


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

""" VERSIONS_CHECKS = {
    "1.13": {"commands"},
    "1.16",   # "locate biome swamp", "The nearest minecraft:swamp is at"
    "1.17",
    "1.18": ,
    "1.18.2", # "jfr" "Started flight recorder profiling"
    "1.19",   # "locate biome swamp", "The nearest minecraft:swamp is at"
    "1.19.3",
    "1.19.4",
    "1.20",
    "1.20.2", # "random value 0..1" "Randomized value:"
    "1.21.5"
} """


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
    def check_version(server: "Server") -> Optional[str]:
        """
        Fetches the server version by detecting if some blocks exists.

        Returns None if Rcon doesn't work or the player is not found
        """

        for version, item in VERSION_BLOCKS.items():

            resp = server.execute(f"/give @s {item}")

            if resp is not None and resp.startswith("Added"): # type: ignore
                return version