from typing import Union, Optional, NoReturn, Tuple, TYPE_CHECKING
import time

from .Types.player import Player
from .Types.message import Message
from .event import Event

if TYPE_CHECKING:
    from .server import Server


class Context:
    """
    Event / command context

    Provides some useful informations and utility methods
    """


    __player: Union[Player, str]
    __message: Optional[str]
    __time: Tuple
    __server: "Server"
    __event_type: "Event"
    

    def __init__(self, player: str, time: Tuple, server: "Server", event_type: "Event", message: Optional[str]=None) -> NoReturn:
        
        self.__player = server.get_player_by_name(player) or player
        self.__time = time
        self.__server = server
        self.__message = message
        self.__event_type = event_type

    
    def wait_for_player(self, timeout: float=10) -> bool:
        """
        Tries to fetch the player every 0.5 seconds

        This operation could take quite a bit of time (even some seconds!)

        Use only with the PlayerJoin Event and you don't need just the playername

        Returns True only if it manages to fetch the player in the given timeout
        """

        if (
            self.__event_type != Event.PlayerJoin or
            isinstance(self.__player, Player)
            ):
            return True
        
        start_time = time.time()

        while time.time() - start_time < timeout:
            
            if player:= self.__server.get_player_by_name(self.__player):

                self.__player = player
                return True
            
            time.sleep(0.5)

        return False

    
    @property
    def player(self) -> Union[Player, str]:
        """
        Player this context is referring to.

        If the event is PlayerLeft returs only the playername
        If the event is PlayerJoin you can call wait_for_player() method if you don't need just the playername 
        """

        return self.__player
    

    @property
    def death_message(self) -> Optional[str]:
        """
        Player death message

        None, if hes not death
        """

        if self.__event_type == Event.PlayerDeath:
            return self.__message
    

    @property
    def message(self) -> Optional[str]:
        """
        The player message

        None, if theres no message
        """

        if self.__event_type == Event.PlayerChat:
            return self.__message


    @property
    def command(self) -> Optional[str]:
        """
        The player command

        None, if theres no command
        """

        if self.__event_type == Event.PlayerCommand:
            return self.__message
    

    @property
    def time(self) -> Tuple:
        """
        When the event happened

        hrs, mins, secs
        """

        return self.__time
    

    @property
    def server(self) -> "Server":
        """
        The server in where the event was triggered
        """

        return self.__server


    @property
    def event_type(self) -> Event:
        """
        Event type
        """

        return self.__event_type


    def say(self, message: str, author: str="[Server]") -> NoReturn:
        """
        Sends something to the server where the event was triggered
        """

        self.__server.execute(f"""/tellraw @a {{"text":"{author} {message}"}}""")
    
    
    def reply(self, message: Message) -> NoReturn:
        """
        Tellraw something to the player that triggered the event

        Avaiable only if the event is different than PlayerLeft
        """

        if not self.wait_for_player():
            return
        
        if self.__event_type != Event.PlayerLeft:

            if isinstance(message, str):
                self.__server.execute(f"""/tellraw {self.__player} {{"text": "{message}"}}""")
            else:
                self.__server.execute(f"""/tellraw {self.__player} {message}""")