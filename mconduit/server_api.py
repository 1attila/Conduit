from __future__ import annotations
from typing import Optional, Dict, List, Set, Any, TYPE_CHECKING
from pathlib import Path
import json
import time

from mconduit.server_commands import ServerCommandsAPI
from mconduit.enums import Gamemode, Difficulty
from mconduit.world import WorldSnapshot, CachedWorldReader
from mconduit.scoreboard import ScoreboardReader
from mconduit._types import Player

if TYPE_CHECKING:
    from mconduit.server_runner import ServerRunner
    from mconduit.world import CachedWorldReader, Overworld, Nether, End
    from mconduit.scoreboard import Scoreboard, Objective, Team, DisplaySlot


class Properties:
    """
    Server properties
    """

    _path: Path
    _server: Optional[ServerAPI]
    _cache: Dict[str, Any]


    def __init__(
        self,
        *,
        path: Optional[Path] = None,
        server: Optional[ServerAPI] = None
    ) -> None:

        self._server = server
        
        if server is not None:
            self._path = server.path / "server.properties"

        elif path is not None:
            self._path = path / "server.properties"

        else:
            ValueError("Both server path are None!")

        self._cache = {}
        self.load()

    
    def _read(self) -> Optional[str]:

        if self._server is not None:
            return self._server.read_file(self._path)
        
        with open(self._path) as f:
            return f.read()
        

    def _save(self, data: str) -> None:
        
        if self._server is not None:

            self._server.write_file(self._path, data)
            return
        
        with open(self._path, "w") as f:
            f.write(data)

    
    def _get_lines(self) -> List[str]:

        raw = self._read()

        if raw is None:
            raise RuntimeError("Eror while reading server.properties")
        
        return [line.strip() for line in raw.splitlines(keepends=True)]
            

    def load(self) -> None:
        
        lines = self._get_lines()
        self._cache.clear()

        for line in lines:

            line = line.strip()

            if (
                len(line) == 0 or
                line.startswith("#") or
                "=" not in line
            ):
                continue

            key, value = line.split("=", 1)
            self._cache[key] = value


    def has_attribute(self, attribute: str) -> bool:
        return attribute in self._cache
    

    def get(
        self,
        key: str,
        default: Any | None = None
    ) -> Any:
        return self._cache.get(key, default)

    
    def set(
        self,
        key: str,
        value: Any
    ) -> None:

        key_prefix = f"{key}="
        updated = False
        new_lines = []

        if type(value) is bool:
            value = "true" if value else "false"

        value = str(value)

        for line in self._get_lines():

            if line.startswith(key_prefix):

                new_lines.append(f"{key_prefix}{value}")
                updated = True
            
            else:
                new_lines.append(line)

        if not updated:
            new_lines.append(f"{key_prefix}{value}")

        self._save("\n".join(new_lines))
        self.load()

    
    def as_dict(self) -> Dict[str, str]:
        return dict(self._cache)


class ServerAPI(ServerCommandsAPI):
    """
    Server data fetch and commands API

    It doesnt fetch private data such as IPs or Rcon passwords

    They are all grouped here for redability
    """

    
    _properties: Properties
    _world_snapshot: WorldSnapshot
    _world_reader: CachedWorldReader
    _scoreboard_reader: ScoreboardReader


    def __init__(
        self,
        runner: ServerRunner
    ) -> None:

        super().__init__(runner)

        self._properties = Properties(server=self)

        self._world_snapshot = WorldSnapshot(self)
        self._world_reader = CachedWorldReader(self._world_snapshot)
        self._scoreboard_reader = ScoreboardReader(self, self._world_snapshot)


    @property
    def properties(self) -> Properties:
        """
        Wrapper of server.properties
        """

        return self._properties


    @property
    def motd(self) -> str:
        """
        Message displayed in the server list under the server name
        """

        return self.properties.get("motd")
    

    @motd.setter
    def motd(self, value: str) -> None:
        self.properties.set("motd", value)
    

    @property
    def simulation_distance(self) -> int:
        """
        Maxinum distance of entity from player for being ticket

        3 - 32
        """

        return int(self.properties.get("simulation-distance"))


    @simulation_distance.setter
    def simulation_distance(self, value: int) -> None:

        if 3 < value < 32:
            self.properties.set("simulation-distance", value)


    @property
    def view_distance(self) -> int:
        """
        Radious in chunks of the portion of the world the server sends to the client
        """

        return int(self.properties.get("view-distance"))
    

    @view_distance.setter
    def view_distance(self, value: int) -> None:

        if 3 < value < 32:
            self.properties.set("view-distance", value)


    @property
    def gamemode(self) -> Gamemode:
        """
        Default server gamemode
        """

        return self.properties.get("gamemode") # TODO: Parse gamemode


    @gamemode.setter
    def gamemode(self, value: Gamemode) -> None:
        self.properties.set("gamemode", value)


    @property
    def difficulty(self) -> Difficulty:
        """
        Default server difficulty
        """

        return self.properties.get("difficulty") # TODO: Parse


    @difficulty.setter
    def difficulty(self, value: Difficulty) -> None:
        self.properties.set("difficulty", value)

    
    @property
    def require_resource_pack(self) -> bool:
        """
        If enable, player must download the resource pack to play
        """

        return self.properties.get("require-resource-pack", False)
    

    @require_resource_pack.setter
    def require_resource_pack(self, value: bool) -> None:
        self.properties.set("require-resource-pack", value)


    @property
    def resource_pack_sha1(self) -> Optional[str]:
        """
        Resource pack sha1
        """

        return self.properties.get("resource-pack-sha1", None)
    

    @resource_pack_sha1.setter
    def resource_pack_sha1(self, value: str) -> None:
        self.properties.set("resource-pack-sha1", value)

    
    @property
    def resource_pack_url(self) -> Optional[str]:
        """
        Resource pack url
        """

        return self.properties.get("resource-pack", None)

    
    @resource_pack_url.setter
    def resource_pack_url(self, value: str) -> None:
        self.properties.set("resource-pack", value)


    @property
    def whitelist(self) -> List[str]: #TODO: Add machine support
        """
        From whitelist.json
        """

        data = json.load(open(self.path / "whitelist.json"))
        
        return [player["name"] for player in data]


    @property
    def ops(self) -> List[str]: #TODO: Add machine support
        """
        From ops.json
        """
        
        data = json.load(open(self.path / "ops.json"))

        return [player["name"] for player in data]


    @property
    def banned_ips(self) -> List[str]:
        """
        From banned-ips.json
        """

        data = json.load(open(self.path / "banned-ips.json"))

        return [player ["ip"] for player in data]


    @property
    def banned_players(self) -> List[str]: #TODO: Add machine support
        """
        From banned-players.json
        """

        data = json.load(open(self.path / "banned-players.json"))

        return [player["name"] for player in data]
                

    def get_player_by_name(self, name: str) -> Optional[Player]:
        """
        Returns the player that matches the specified name if online
        """

        return self.online_players.get(name, None)


    def get_player_named(self, name: str) -> Optional[Player]:
        """
        Alias of `get_player_by_name`
        """

        return self.get_player_by_name(name)
    

    def get_player_by_uuid(self, uuid: str) -> Optional[Player]:
        """
        Returns the player that matches the specified uuid if online
        """

        for player in (self.online_players or {}).values():
            if player.uuid == uuid:
                return player
        
        return None
    

    @property
    def world(self) -> CachedWorldReader:
        return self._world_reader


    @property
    def overworld(self) -> Overworld:
        return self._world_reader.overworld

    
    @property
    def nether(self) -> Nether:
        return self._world_reader.nether


    @property
    def end(self) -> End:
        return self._world_reader.end

    
    @property
    def objectives(self) -> Dict[str, Objective]:
        return self._scoreboard_reader.objectives


    @property
    def scoreboards(self) -> Dict[str, Scoreboard]:
        return self._scoreboard_reader.scoreboards

    
    @property
    def teams(self) -> Dict[str, Team]:
        return self._scoreboard_reader.teams


    @property
    def display_slots(self) -> Dict[DisplaySlot, str]:
        return self._scoreboard_reader.display_slots


    @property
    def data_version(self) -> int:
        """
        Data version of the nbt structures inside the `/world` folder
        """

        return self._world_reader.data_version


    @property
    def latest_world_save_time(self) -> float:
        """
        Latest time the world got saved
        """

        return self._world_snapshot.latest_world_save_time
    

    @property
    def secs_since_last_world_save(self) -> float:
        """
        Time passed (in seconds) since the latest world save
        """

        return time.time() - self.latest_world_save_time



    def get_all_joined_players(self) -> List[str]:
        """
        Returns a lists with all names of the players who joined in this server
        """

        joined_players: Set[str] = set()

        usercache_path = self.path / "usercache.json"

        try:
            with open(usercache_path) as f:
                
                all_players = json.load(f)

                for entry in all_players:

                    if "name" in entry:
                       joined_players.add(entry["name"])

                return list(joined_players)

        except (json.JSONDecodeError, IOError):
            return []