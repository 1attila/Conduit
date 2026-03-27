from typing import Optional, TypeVar, Dict, List, Any, TYPE_CHECKING
from pathlib import Path
import configparser
import threading
import parse
import json

from .server_commands import ServerCommandsAPI
from .enums import Gamemode, Difficulty
from .plugins import Permission
from .utils.rcon import Rcon
from ._types import Player

if TYPE_CHECKING:
    from .conduit_config import ServerRunnerConfig
    from .server import Server


_T = TypeVar("_T")


class Properties:
    """
    Server properties
    """


    def __init__(
        self,
        *,
        server: Optional["Server"] = None,
        path: Optional[Path]= None
    ) -> None:
        
        if server is None and path is None:
            ValueError("Both server path are None!")
        
        self.__server = server

        if server is not None:
            self.__path = server.path / "server.properties"
        else:
            self.__path = path / "server.properties"
            
        self.__cache = {}
        self.load()

    
    def _read(self) -> Optional[str]:

        if self.__server is not None:
            return self.__server.read_file(self.__path)
        
        with open(self.__path) as f:
            return f.read()
        

    def _save(self, data: str) -> None:
        
        if self.__server is not None:

            self.__server.read_file(self.__path)
            return
        
        with open(self.__path, "w") as f:
            f.write(data)

    
    def _get_lines(self) -> List[str]:

        raw = self._read()

        if raw is None:
            raise RuntimeError("Eror while reading server.properties")
        
        return [line.strip() for line in raw.splitlines(keepends=True)]
            

    def load(self) -> None:
        
        lines = self._get_lines()
        self.__cache.clear()

        for line in lines:

            line = line.strip()

            if (
                len(line) == 0 or
                line.startswith("#") or
                "=" not in line
                ):
                continue

            key, value = line.split("=", 1)
            self.__cache[key] = value


    def has_attribute(self, attribute: str) -> bool:
        return attribute in self.__cache
    

    def get(
        self,
        key: str,
        default: _T | None = None
    ) -> _T:
        return self.__cache.get(key, default)

    
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
        return dict(self.__cache)


class ServerAPI(ServerCommandsAPI):
    """
    Server data fetch and commands API

    It doesnt fetch private data such as IPs or Rcon passwords

    They are all grouped here for redability
    """


    PROPERTIES_FILENAME = "server.properties"
    __high_permission_level: bool
    __rcon: Rcon # This will be initialized from Server
    __lock: threading.Lock


    def init(
        self,
        config: "ServerRunnerConfig",
        rcon: Rcon
    ) -> None:

        self.__config = config
        self.__rcon = rcon
        self.__high_permission_level = config.high_permissions

        super().init(config, rcon)
        
        properties = self.read_file(self.PROPERTIES_FILENAME)
        
        if properties is None:
            raise FileNotFoundError("Missing `server.properties` file!")

        prop_data = "[dummy-section]\n" + properties
        c = configparser.RawConfigParser()
        c.read_string(prop_data)
        
        self.__prop = dict(c["dummy-section"])
        self.__lock = threading.Lock()


    def __change_data(self, key: str, value: Any) -> None:
        """
        Utility function used to edit properties
        """

        if type(value) is bool:
            value = "true" if value else "false"

        with self.__lock:
            
            raw = self.read_file(self.PROPERTIES_FILENAME)

            if raw is None:
                raise FileNotFoundError(self.PROPERTIES_FILENAME)
            
            lines = raw.splitlines(keepends=True)
            key_prefix = f"{key}="

            found = False
            new_lines = []

        for line in lines:
            stripped = line.lstrip()

            if stripped.startswith(key_prefix):
                new_lines.append(f"{key_prefix}{value}\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"\n{key_prefix}{value}\n")

        self.write_file(self.PROPERTIES_FILENAME, "".join(new_lines))


    @property
    def motd(self) -> str:
        """
        Message displayed in the server list under the server name
        """

        return self.__prop.get("motd")
    

    @motd.setter
    def motd(self, value: str) -> None:
        self.__change_data("motd", value)
    

    @property
    def simulation_distance(self) -> int:
        """
        Maxinum distance of entity from player for being ticket

        3 - 32
        """

        return int(self.__prop.get("simulation-distance"))


    @simulation_distance.setter
    def simulation_distance(self, value: int) -> None:

        if 3 < value < 32:
            self.__change_data("simulation-distance", value)


    @property
    def view_distance(self) -> int:
        """
        Radious in chunks of the portion of the world the server sends to the client
        """

        return int(self.__prop.get("view-distance"))
    

    @view_distance.setter
    def view_distance(self, value: int) -> None:

        if 3 < value < 32:
            self.__change_data("view-distance", value)


    @property
    def gamemode(self) -> Gamemode:
        """
        Default server gamemode
        """

        return self.__prop.get("gamemode")


    @gamemode.setter
    def gamemode(self, value: Gamemode) -> None:
        self.__change_data("gamemode", value)


    @property
    def difficulty(self) -> Difficulty:
        """
        Default server difficulty
        """

        return self.__prop.get("difficulty")


    @difficulty.setter
    def difficulty(self, value: Difficulty) -> None:
        self.__change_data("difficulty", value)

    
    @property
    def require_resource_pack(self) -> bool:
        """
        If enable, player must download the resource pack to play
        """

        return self.__prop.get("require-resource-pack")
    

    @require_resource_pack.setter
    def require_resource_pack(self, value: bool) -> None:
        self.__change_data("require-resource-pack", value)


    @property
    def resource_pack_sha1(self) -> str:
        """
        Resource pack sha1
        """

        return self.__prop.get("resource-pack-sha1")
    

    @resource_pack_sha1.setter
    def resource_pack_sha1(self, value: str) -> None:
        self.__change_data("resource-pack-sha1", value)

    
    @property
    def resource_pack_url(self) -> str:
        """
        Resource pack url
        """

        return self.__prop.get("resource-pack")

    
    @resource_pack_url.setter
    def resource_pack_url(self, value: str) -> None:
        self.__change_data("resource-pack", value)


    @property
    def whitelist(self) -> List[str]: #TODO: Add machine support
        """
        From whitelist.json
        """

        data = json.load(open(Path(self.__config.path) / "whitelist.json"))
        
        return [player["name"] for player in data]


    @property
    def ops(self) -> List[str]: #TODO: Add machine support
        """
        From ops.json
        """
        
        data = json.load(open(Path(self.__config.path) / "ops.json"))

        return [player["name"] for player in data]


    @property
    def banned_ips(self) -> List[str]:
        """
        From banned-ips.json
        """


    @property
    def banned_players(self) -> List[str]: #TODO: Add machine support
        """
        From banned-players.json
        """

        data = json.load(open(Path(self.__config.path) / "banned-players.json"))

        return [player["name"] for player in data]
    

    def get_online_players(self) -> List[Player]:
        """
        Returns a list of all online players

        Heavily inspired from https://github.com/TISUnion/ChatBridge/blob/master/chatbridge/impl/online/entry.py
        """

        formatters = (
            r"There are {amount:d} of a max {limit:d} players online:{players}",  # <1.16
			r"There are {amount:d} of a max of {limit:d} players online:{players}",  # >=1.16
        )

        response = self.execute("/list")

        for formatter in formatters:
            parsed_response = parse.parse(formatter, response)

            if parsed_response is not None and parsed_response["players"].startswith(" "):
                                
                players = parsed_response["players"][1:]

                if len(players) > 0:

                    player_list = players.split(", ")
                    
                    return [Player(name, self) for name in player_list]

                return []
                

    def get_player_by_name(self, name: str) -> Optional[Player]:
        """
        Returns the player that matches the specified name if online
        """
        
        for player in self.get_online_players() or []:
            if player.name == name:
                return player
    

    def get_player_by_uuid(self, uuid: str) -> Optional[Player]:
        """
        Returns the player that matches the specified uuid if online
        """

        for player in self.get_online_players() or []:
            if player.uuid == uuid:
                return player

    
    def get_permissions_for(self, player_name: str) -> Permission:

        permissions_names = ["Guest", "Member", "Helper", "Admin", "Owner"]
        
        player = self.get_player_by_name(player_name)
        
        if player is not None:
            return player.permissions

        for perm, teams in self.permissions.items():

            for team in teams:
                data = self.execute(f"/team list {team}") or ""
                
                data = parse.parse(r"Team [{team}] has {n} member(s): {members}", data)

                if data:

                    players = data["members"].split(", ")
                    
                    if player_name in players:
                        
                        return permissions_names[perm]

        return Permission.Guest