from typing import List, Callable, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from .server import Server


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
    PlayerJoin           = enum.auto()
    PlayerLeft           = enum.auto()
    PlayerDeath          = enum.auto()
    PlayerChat           = enum.auto()
    PlayerCommand        = enum.auto()
    PlayerKicked         = enum.auto()
    PlayerOpped          = enum.auto()
    PlayerDeopped        = enum.auto()
    PlayerWhitelisted    = enum.auto()
    PlayerUnwhitelisted  = enum.auto()
    PlayerAdvancement    = enum.auto()
    PlayerChallenge      = enum.auto()
    SetScoreboardValue   = enum.auto()
    AddScoreboardValue   = enum.auto()
    SubScoreboardValue   = enum.auto()
    ResetScoreboardValue = enum.auto()
    PlayerTrigger        = enum.auto()
    PlayerItemGive       = enum.auto()
    PlayerSetGamemode    = enum.auto()
    PlayerSummonedEntity = enum.auto()
    PlayerKilledPlayer   = enum.auto()
    PlayerShift          = enum.auto()
    PlayerRigthClick     = enum.auto()
    PlayerLeftClick      = enum.auto()

    # Server
    ServerStart          = enum.auto()
    ServerStop           = enum.auto()
    GameSaved            = enum.auto()
    OnLog                = enum.auto()

    # Conduit
    ConduitStart         = enum.auto()
    ConduitStop          = enum.auto()
    
    # Misc
    TextClick            = enum.auto() # This should be newer used!


class EventListener:
    """
    Listener that runs in loop to look for an event, like scoreboard changes
    """


    __server: "Server"
    __detach_flag: bool # Used in EventHandler
    fallbacks: List[Callable]
    enabled: bool


    def __init__(self, server: "Server") -> None:
        
        self.__server = server
        self.__detach_flag = False
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

        self.__detach_flag = True


    @property
    def server(self) -> "Server":
        """
        The server where this listener is running
        """

        return self.__server