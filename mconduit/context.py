from __future__ import annotations
from typing import Union, Optional, Tuple, TYPE_CHECKING
import time

from mconduit._types import Player, Message
from mconduit.utils.errors import ConduitError
from mconduit.text import text
from mconduit.event import Event, SCOREBOARDS_EVENTS, SERVER_EVENTS

if TYPE_CHECKING:
    from mconduit.server import Server


class Context:
    """
    Event / command context

    Provides some useful informations and utility methods
    """


    _player: Optional[Player]
    _other_player: Optional[Player]
    _message: Optional[str]
    _amount: Optional[int]
    _value: Optional[int]
    _id: Optional[int]
    _time: Tuple
    _server: Server
    _event_type: Event
    _is_server_event: bool
    

    def __init__(
        self,
        player: str,
        time: Tuple,
        server: Server,
        event_type: Event,
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
        
        self._is_server_event = event_type in SERVER_EVENTS

        if not self._is_server_event:
            self._player = Player(player, server)
        else:
            self._player = None

        if other_player is not None:
            self._other_player = Player(other_player, server)
        else:
            self._other_player = None

        if advancement is not None:
            message = advancement

        elif scoreboard is not None:
            message = scoreboard

        elif trigger is not None:
            message = trigger

        self._amount = amount
        self._value = value
        self._id = id
        self._time = time
        self._server = server
        self._message = message
        self._event_type = event_type

    
    def wait_for_player(self, timeout: float = 10) -> bool: # NOTE This is very outdated
        """
        Tries to fetch the player every 0.5 seconds

        This operation could take quite a bit of time (even some seconds!)

        Use only with the PlayerJoin Event and you don't need just the playername

        Returns True only if it manages to fetch the player in the given timeout
        """

        if self._is_server_event:
            return False

        if (
            self._event_type != Event.PLAYER_JOIN or
            isinstance(self._player, Player)
        ):
            return True
        
        start_time = time.time()

        while time.time() - start_time < timeout:

            assert self._player is not None
            
            if player:= self._server.get_player_by_name(self._player):

                self._player = player
                return True
            
            time.sleep(0.5)

        return False

    
    @property
    def player(self) -> Optional[Player]:
        """
        Player this context is referring to
        """

        if self._is_server_event:
            return None

        return self._player
    

    @property
    def other_player(self) -> Optional[Player]:
        """
        Returns the player that has been:
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

        return self._other_player
    

    @property
    def advancement(self) -> Optional[str]:
        """
        Player advancement, if any
        """

        if self._event_type == Event.PLAYER_ADVANCEMENT:
            return self._message

        return None

    
    @property
    def challenge(self) -> Optional[str]:
        """
        Player challenge, if any
        """

        if self._event_type == Event.PLAYER_CHALLENGE:
            return self._message

        return None
        

    @property
    def scoreboard(self) -> Optional[str]:
        """
        Event scoreboard, if any
        """

        if self._event_type in SCOREBOARDS_EVENTS:
            return self._message

        return None

    
    @property
    def trigger(self) -> Optional[str]:
        """
        Trigger name, if any
        """

        return self._message
        

    @property
    def value(self) -> Optional[int]:
        """
        Scoreboard objective value, if any
        """

        return self._value
    

    @property
    def amount(self) -> Optional[int]:
        """
        Scoreboard objective increase/decrease amount, if any 
        """

        return self._amount
    

    @property
    def death_message(self) -> Optional[str]:
        """
        Player death message

        None, if hes not death
        """

        if self._event_type == Event.PLAYER_DEATH:
            return self._message

        return None
    

    @property
    def message(self) -> Optional[str]:
        """
        The player message

        None, if theres no message
        """

        if self._event_type == Event.PLAYER_CHAT:
            return self._message

        return None


    @property
    def command(self) -> Optional[str]:
        """
        The player command

        None, if theres no command
        """

        if self._event_type == Event.PLAYER_COMMAND:
            return self._message

        return None
    

    @property
    def id(self) -> Optional[int]:
        """
        Button id, if any.

        Ids are automatically set to 0 and increased by 1 for every button you create with the same click function.

        This is used when you want to assign same or similar behaviour to lots of buttons and you need to distingue them
        """
        
        if self._event_type == Event.TEXT_CLICK:
            return self._id

        return None
    

    @property
    def time(self) -> Tuple:
        """
        When the event happened

        HH:MM:SS
        """

        return self._time
    

    @property
    def server(self) -> Server:
        """
        The server on which the event was triggered
        """

        return self._server


    @property
    def event_type(self) -> Event:
        """
        Event type
        """

        return self._event_type


    def say(
        self,
        message: Message,
        *messages: Message
    ) -> None:
        """
        Sends something to the server where the event was triggered
        """

        if self.event_type == Event.SERVER_STOP:
            return None

        if len(messages):
            joint_messages = message

            for msg in messages:
                joint_messages = joint_messages + msg

            message = joint_messages
        
        if self._event_type != Event.PLAYER_LEFT:
            self._server.tellraw("@a", message)

        return None

    
    def reply(
        self,
        message: Message,
        *messages: Message
    ) -> None:
        """
        Tellraw something to the player that triggered the event

        Avaiable only if the event is different than PlayerLeft
        """

        if self._is_server_event:
            return None

        if not self.wait_for_player():
            return None

        if len(messages):
            joint_messages = message

            for msg in messages:
                joint_messages = joint_messages + msg

            message = joint_messages
        
        if self._event_type != Event.PLAYER_LEFT:

            assert isinstance(self._player, Player)

            self._server.tellraw(self._player.name, message)

        return None
    

    def info(self, info: Union[text.Text, str]) -> None:
        """
        Replies the user with the given message in gray
        """

        if isinstance(info, text.Text):
            
            info.gray()
            self.reply(info)
            return None
        
        self.reply(text.gray(info))

        return None


    def success(self, msg: Union[text.Text, str]) -> None:
        """
        Replies the user with the given message in green
        """

        if isinstance(msg, text.Text):
            
            msg.green()
            self.reply(msg)
            return None

        self.reply(text.green(msg))

        return None

    
    def error(self, err: Union[Exception, text.Text, str]) -> None:
        """
        Replies the user with the name of the exception in red
        """

        if isinstance(err, text.Text):
            
            err.red()
            self.reply(err)
            return None
        
        if isinstance(err, Exception):
            
            self.reply(ConduitError.from_exception(err).to_text())
            return None

        self.reply(text.red(err))

        return None

    
    def warn(self, warn: Union[Warning, text.Text, str]) -> None:
        """
        Replies the user with the name of the warning in gold
        """
        
        if isinstance(warn, text.Text):
            
            warn.gold()
            self.reply(warn)
            return None

        if not isinstance(warn, str):
            warn = type(warn).__name__

        self.reply(text.gold(warn))

        return None


    def notify(
        self,
        *messages: Message,
        fade_in: int = 2,
        duration: int = 15, # AKA: stay
        fade_out: int = 5
    ) -> None:
        """
        Displays the current text in the player actionbar
        """

        message = messages[0]

        for msg in messages[1:]:
            message += msg

        if isinstance(message, text.Text):
            message = str(message) # NOTE: colors / styles are version indipendent, no need to pass v1_21_5

        self.server.execute([
            f"title {self.player} times {fade_in} {duration} {fade_out}",
            f"title {self.player} actionbar {message}"
        ])

        return None

    
    def notify_success(
        self,
        *messages: Message,
        fade_in: int = 2,
        duration: int = 15, # AKA: stay
        fade_out: int = 5
    ) -> None:
        """
        Displays the given message in green in the player actionbar
        """

        message = messages[0]

        for msg in messages[1:]:
            message += msg

        if isinstance(message, text.Text):
            message.green()
        
        else:
            message = text.green(message)

        self.notify(
            message,
            fade_in=fade_in,
            duration=duration,
            fade_out=fade_out
        )

        return None