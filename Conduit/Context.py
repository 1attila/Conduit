from typing import Union, Optional, NoReturn, Tuple, TYPE_CHECKING

from .Types.Player import Player
from .Types.Message import Message
from .Event import Event

if TYPE_CHECKING:
    from Server import Server


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

    
    @property
    def player(self) -> Player:
        """
        Player this context is referring to.

        If the event is PlayerJoin or PlayerLeft player is a string
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
    def type(self) -> Event:
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

        if self.__event_type != Event.PlayerLeft:

            if isinstance(message, str):
                self.__server.execute(f"""/tellraw {self.__player} {{"text": "{message}"}}""")
            else:
                self.__server.execute(f"""/tellraw {self.__player} {message}""")