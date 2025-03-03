from typing import NoReturn, TYPE_CHECKING

from .utils.rcon import Rcon

if TYPE_CHECKING:
    from .conduit_config import ServerRunnerConfig


class ServerCommandsAPI:
    """
    Server commands container

    They are all grouped here for redability
    """

    
    __rcon: Rcon # Initialized from Server
    

    def init(self, config: "ServerRunnerConfig", rcon: Rcon) -> NoReturn:
        
        self.__rcon = rcon

    
    def _exe(self, command: str) -> NoReturn:

        if self.__rcon:
            self.__rcon(command)

    # Comunication

    def say(self, string: str):
        self._exe(f"/say {string}")

    def tellraw():
        ...

    def team():
        ...

    def whitelist():
        ...

    def kick():
        ...

    def ban():
        ...

    def ban_ip():
        ...

    def pardon():
        ...

    def pardon_ip():
        ...

    def ops():
        ...

    def op():
        ...

    def deop():
        ...

    # Player action

    def gamemode():
        ...

    # Entity interactions

    def summon():
        ...

    def kill():
        ...

    def tp():
        ...

    def rotate():
        ...

    def ride():
        ...

    def give():
        ...

    def enchant():
        ...

    def effect():
        ...

    def xp():
        ...

    def damage():
        ...

    def particle():
        ...

    def playsound():
        ...

    def scoreboard():
        ...

    # World interactions

    def time():
        ...

    def event():
        ...

    def setblock():
        ...

    def fill():
        ...

    def loot():
        ...