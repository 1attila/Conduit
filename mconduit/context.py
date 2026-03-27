from typing import Union, Optional, Tuple, List, TYPE_CHECKING
import time

from ._types import Player, Message
from .utils import ConduitError
from .text import text
from .event import Event

if TYPE_CHECKING:
    from .server import Server


class Context:
    """
    Event / command context

    Provides some useful informations and utility methods
    """


    __player: Optional[Player]
    __other_player: Optional[Player]
    __message: Optional[str]
    __amount: Optional[int]
    __value: Optional[int]
    __id: Optional[int]
    __time: Tuple
    __server: "Server"
    __event_type: Event
    __is_server_event: bool
    

    def __init__(
        self,
        player: str,
        time: Tuple,
        server: "Server",
        event_type: "Event",
        *,
        message: Optional[str] = None,
        advancement: Optional[str] = None,
        trigger: Optional[str] = None,
        other_player: Optional[str] = None,
        scoreboard: Optional[str] = None,
        amount: Optional[int] = None,
        value: Optional[int] = None,
        id: Optional[int] = None
    ) -> None:
        
        self.__is_server_event = event_type in [Event.ServerStart, Event.ServerStop]

        if not self.__is_server_event:
            self.__player = Player(player, server)
        else:
            self.__player = None

        if other_player is not None:
            self.__other_player = Player(other_player, server)
        else:
            self.__other_player = None

        if advancement is not None:
            message = advancement

        elif scoreboard is not None:
            message = scoreboard

        elif trigger is not None:
            message = trigger

        self.__amount = amount
        self.__value = value
        self.__id = id
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

        if self.__is_server_event:
            return False

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
    def player(self) -> Optional[Player]:
        """
        Player this context is referring to.

        If the event is ServerStart or ServerStop returns None
        If the event is PlayerJoin you can call wait_for_player() method if you don't need just the player name 
        """

        if self.__is_server_event:
            return

        return self.__player
    

    @property
    def other_player(self) -> Optional[Player]:
        """
        Returns the player that has:
        - whitelisted
        - unwhitelisted
        - opped
        - deopped

        this Context player, if any.

        E.g. 
        ```
        <Steve> /whitelist add Jack

        Context.player: Jack
        Context.other_player: Steve
        ```
        """

        return self.__other_player
    

    @property
    def advancement(self) -> Optional[str]:
        """
        Player advancement, if any
        """

        if self.__event_type == Event.PlayerAdvancement:
            return self.__message

    
    @property
    def challenge(self) -> Optional[str]:
        """
        Player challenge, if any
        """

        if self.__event_type == Event.PlayerChallenge:
            return self.__message
        

    @property
    def scoreboard(self) -> Optional[str]:
        """
        Event scoreboard, if any
        """

        if self.__event_type in [Event.SetScoreboardValue, Event.AddScoreboardValue, Event.SubScoreboardValue, Event.ResetScoreboardValue]:
            return self.__message

    
    @property
    def trigger(self) -> Optional[str]:
        """
        Trigger name, if any
        """

        return self.__message
        

    @property
    def value(self) -> Optional[int]:
        """
        Scoreboard objective value, if any
        """

        return self.__value
    

    @property
    def amount(self) -> Optional[int]:
        """
        Scoreboard objective increase/decrease amount, if any 
        """

        return self.__amount
    

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
    def id(self) -> Optional[int]:
        """
        Button id, if any.

        Ids are automatically set to 0 and increased by 1 for every button you create with the same click function.

        This is used when you want to assign same or similar behaviour to lots of buttons and you need to distingue them
        """
        
        if self.__event_type == Event.TextClick:
            return self.__id
    

    @property
    def time(self) -> Tuple:
        """
        When the event happened

        HH:MM:SS
        """

        return self.__time
    

    @property
    def server(self) -> "Server":
        """
        The server on which the event was triggered
        """

        return self.__server


    @property
    def event_type(self) -> Event:
        """
        Event type
        """

        return self.__event_type


    def say(
        self,
        message: Message,
        *messages: Message
    ) -> None:
        """
        Sends something to the server where the event was triggered
        """

        if self.event_type == Event.ServerStop:
            return

        if len(messages):
            joint_messages = message

            for msg in messages:
                joint_messages = joint_messages + msg

            message = joint_messages
        
        if self.__event_type != Event.PlayerLeft:
            self.__server.tellraw("@a", message)

    
    def reply(
        self,
        message: Message,
        *messages: Message
    ) -> None:
        """
        Tellraw something to the player that triggered the event

        Avaiable only if the event is different than PlayerLeft
        """

        if self.__is_server_event:
            return

        if not self.wait_for_player():
            return

        if len(messages):
            joint_messages = message

            for msg in messages:
                joint_messages = joint_messages + msg

            message = joint_messages
        
        if self.__event_type != Event.PlayerLeft:
            self.__server.tellraw(self.__player.name, message)
    

    def info(self, info: Union[text.Text, str]) -> None:
        """
        Replies the user with the given message in gray
        """

        if isinstance(info, text.Text):
            
            info.color = text.Color.Gray
            self.reply(info)
            return
        
        self.reply(text.gray(info))


    def success(self, msg: Union[text.Text, str]) -> None:
        """
        Replies the user with the given message in green
        """

        if isinstance(msg, text.Text):
            
            msg.color = text.Color.Green
            self.reply(msg)
            return

        self.reply(text.green(msg))

    
    def error(self, err: Union[Exception, text.Text, str]) -> None:
        """
        Replies the user with the name of the exception in red
        """

        if isinstance(err, text.Text):
            
            err.color = text.Color.Red
            self.reply(err)
            return
        
        if isinstance(err, Exception):
            
            self.reply(ConduitError.from_exception(err).to_text())
            return

        self.reply(text.red(err))

    
    def warn(self, warn: Union[Warning, text.Text, str]) -> None:
        """
        Replies the user with the name of the warning in gold
        """
        
        if isinstance(warn, text.Text):
            
            warn.color = text.Color.Gold
            self.reply(warn)
            return

        if not isinstance(warn, str):
            warn = type(warn).__name__

        self.reply(text.gold(warn))