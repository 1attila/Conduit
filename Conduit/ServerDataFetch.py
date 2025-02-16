from typing import NoReturn, Optional, List, TYPE_CHECKING
import configparser
import json
import parse
from .Enums import Difficulty, Gamemode

from Conduit.ServerCommands import ServerCommandsAPI
from .Types import Player
from .utils.Rcon import Rcon

if TYPE_CHECKING:
    from .ConduitConfig import ServerRunnerConfig


class ServerDataFetchAPI(ServerCommandsAPI):
    """
    Server data fetching methods

    It doesnt fetch private data such as IPs or Rcon passwords

    They are all grouped here for redability
    """

    __high_permission_level: bool = True
    __rcon: Rcon # This will be initialized from Server


    def init(self, config: "ServerRunnerConfig", rcon: Rcon) -> NoReturn:

        self.__config = config
        self.__rcon = rcon
        self.PROPERTIES_FILENAME = self.__config.path + "\\server.properties"
        super().init(config, rcon)
        
        with open(self.PROPERTIES_FILENAME) as f:
            prop_data = "[dummy-section]\n" + f.read()
            c = configparser.RawConfigParser()
            c.read_string(prop_data)

            self.__prop = dict(c["dummy-section"])


    def __change_data(self, attr, new) -> NoReturn:
        """
        Utility function used to edit properties
        """

        if self.__high_permission_level:
            
            data: str
            old: str

            with open(self.PROPERTIES_FILENAME) as f:
                prop_data = "[dummy-section]\n" + f.read()
                c = configparser.RawConfigParser()
                c.read_string(prop_data)

                old = dict(c["dummy-section"]).get(attr)

            with open(self.PROPERTIES_FILENAME) as f:
                data = f.read()

            with open(self.PROPERTIES_FILENAME, "w") as f:
                    data = data.replace(old, new)
                    f.write(data)


    @property
    def motd(self) -> str:
        """
        Message displayed in the server list under the server name
        """

        return self.__prop.get("motd")
    

    @motd.setter
    def motd(self, value: str) -> NoReturn:
        self.__change_data(f"motd", f"motd={value}")
    

    @property
    def simulation_distance(self) -> int:
        """
        Maxinum distance of entity from player for being ticket

        3 - 32
        """

        return int(self.__prop.get("simulation-distance"))


    @simulation_distance.setter
    def simulation_distance(self, value: int) -> NoReturn:

        if 3 < value < 32:
            self.__change_data(f"simulation-distance", f"simulation-distance={value}")


    @property
    def view_distance(self) -> int:
        """
        Radious in chunks of the portion of the world the server sends to the client
        """

        return int(self.__prop.get("view-distance"))
    

    @view_distance.setter
    def view_distance(self, value: int) -> NoReturn:

        if 3 < value < 32:
            self.__change_data(f"view-distance", f"view-distance={value}")


    @property
    def gamemode(self) -> Gamemode:
        """
        Default server gamemode
        """

        return self.__prop.get("gamemode")


    @gamemode.setter
    def gamemode(self, value: Gamemode) -> NoReturn:
        self.__change_data(f"gamemode", f"gamemode={value}")


    @property
    def difficulty(self) -> Difficulty:
        """
        Default server difficulty
        """

        self.__prop.get("difficulty")


    @difficulty.setter
    def difficulty(self, value: Difficulty) -> NoReturn:
        self.__change_data(f"difficulty", f"difficulty={value}")


    @property
    def whitelist(self) -> List[str]:
        """
        From whitelist.json
        """

        data = json.load(open(self.__config.path + "\\whitelist.json"))
        
        return [player["name"] for player in data]


    @property
    def op(self) -> List[str]:
        """
        From ops.json
        """
        
        data = json.load(open(self.__config.path + "\\ops.json"))

        return [player["name"] for player in data]


    @property
    def banned_ips(self) -> List[str]:
        """
        From banned-ips.json
        """


    @property
    def banned_players(self) -> List[str]:
        """
        From banned-players.json
        """

        data = json.load(open(self.__config.path + "\\banned-players.json"))

        return [player["name"] for player in data]
    

    def get_online_players(self) -> List[Player.Player]:
        """
        Returns a list of all online players

        Heavily inspired from https://github.com/TISUnion/ChatBridge/blob/master/chatbridge/impl/online/entry.py
        """

        formatters = (
            r"There are {amount:d} of a max {limit:d} players online:{players}",  # <1.16
			r"There are {amount:d} of a max of {limit:d} players online:{players}",  # >=1.16
        )

        response = self.__rcon.execute("/list")

        for formatter in formatters:
            parsed_response = parse.parse(formatter, response)

            if parsed_response is not None and parsed_response["players"].startswith(" "):
                                
                players = parsed_response["players"][1:]

                if len(players) > 0:

                    player_list = players.split(", ")
                    
                    return [Player.Player(name, self) for name in player_list]
                

    def get_player_by_name(self, name: str) -> Optional[Player.Player]:
        """
        Returns the player that matches the specified name if online
        """
        
        for player in self.get_online_players() or []:
            if player.name == name:
                return player
    

    def get_player_by_uuid(self, uuid: str) -> Optional[Player.Player]:
        """
        Returns the player that matches the specified uuid if online
        """

        for player in self.get_online_players() or []:
            if player.uuid == uuid:
                return player