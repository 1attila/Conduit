from typing import List, Callable, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from mconduit.server import Server


class Event(enum.Enum):
    """
    Conduit Events.
    
    ```
    |Categories | ParameterType|
    |Player     | Context      |
    |Server     | Server       |
    |Conduit    | Handler      |
    |Misc       | /            |
    ```
    """

    # Player
    PLAYER_JOIN            = enum.auto()
    PLAYER_LEFT            = enum.auto()
    PLAYER_DEATH           = enum.auto()
    PLAYER_CHAT            = enum.auto()
    PLAYER_COMMAND         = enum.auto()
    PLAYER_KICKED          = enum.auto()
    PLAYER_OPPED           = enum.auto()
    PLAYER_DEOPPED         = enum.auto()
    PLAYER_WHITELISTED     = enum.auto()
    PLAYER_UNWHITELISTED   = enum.auto()
    PLAYER_ADVANCEMENT     = enum.auto()
    PLAYER_CHALLENGE       = enum.auto()
    SET_SCOREBOARD_VALUE   = enum.auto()
    ADD_SCOREBOARD_VALUE   = enum.auto()
    SUB_SCOREBOARD_VALUE   = enum.auto()
    RESET_SCOREBOARD_VALUE = enum.auto()
    PLAYER_TRIGGER         = enum.auto()
    PLAYER_ITEM_GIVE       = enum.auto()
    PLAYER_SET_GAMEMODE    = enum.auto()
    PLAYER_SUMMONED_ENTITY = enum.auto()
    PLAYER_KILLED_PLAYER   = enum.auto()
    PLAYER_SAVED_THE_GAME  = enum.auto()
    PLAYER_SHIFT           = enum.auto()
    PLAYER_RIGHT_CLICK     = enum.auto()
    PLAYER_LEFT_CLICK      = enum.auto()

    # Server
    SERVER_START           = enum.auto()
    SERVER_STOP            = enum.auto()
    GAME_SAVED             = enum.auto()
    ON_LOG                 = enum.auto()

    # Conduit
    CONDUIT_START          = enum.auto()
    CONDUIT_STOP           = enum.auto()
    
    # Misc
    TEXT_CLICK             = enum.auto() # This should be newer used!


class EventListener:
    """
    Listener that runs in loop to look for an event, like scoreboard changes
    """


    _server: "Server"
    _detach_flag: bool # Used in EventHandler
    fallbacks: List[Callable]
    enabled: bool


    def __init__(
        self,
        server: "Server"
    ) -> None:
        
        self._server = server
        self._detach_flag = False
        self.enabled = True
        self.fallbacks = []

    
    def add_fallback(self, fallback: Callable) -> None:
        """
        Adds a new fallback.

        This function exists to assert that the function passed has the rigth parameters
        """

        self.fallbacks.append(fallback)


    def _run_fallbacks(self, *args) -> None:
        """
        Calls all the fallbacks
        """

        for fallback in self.fallbacks:
            try:
                fallback(*args)
            except:
                pass


    def tick(self) -> None:
        """
        Implement this function to look for a certain event.

        Note: if the event is succeded, you must call `self._run_fallbacks(*args)`manually!
        """

        raise NotImplementedError()
    

    def detach(self):
        """
        Removes this listeners from the server listeners
        """

        self._detach_flag = True


    @property
    def server(self) -> "Server":
        """
        The server where this listener is running
        """

        return self._server


SCOREBOARDS_EVENTS = [
    Event.SET_SCOREBOARD_VALUE,
    Event.ADD_SCOREBOARD_VALUE,
    Event.SUB_SCOREBOARD_VALUE,
    Event.RESET_SCOREBOARD_VALUE
]

SERVER_EVENTS = [
    Event.SERVER_START,
    Event.SERVER_STOP,
    Event.GAME_SAVED,
    Event.ON_LOG
]