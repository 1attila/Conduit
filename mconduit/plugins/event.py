from typing import Callable, Union, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..event import Event
    from ..context import Context
    from ..server import Server
    from ..handler import Handler


EventFunc = Callable[[Union["Context", "Handler", "Server", str]], Any]


class EventListener:
    """
    Internal class used to register events
    """
    
    _callback: Callable
    _event: "Event"

    def __init__(
        self,
        callback: EventFunc,
        event: Optional[str]=None
    ) -> None:

        self._callback = callback
        self._event = event
    

def event(event: "Event") -> Callable:
    ...

def event(fn: EventFunc) -> EventListener:
    ...

def event(
    fn: Optional[EventFunc]=None,
    event: Optional["Event"]=None
) -> Union[EventListener, Callable]:
    """
    A decorator that links the function to the given event (or the event named as the function if not provided)

    Examples:

    ```
    @plugins.event
    def on_player_command(self, ctx: Context):
        ...

    @plugins.event(event=Event.PlayerJoin)
    def greet(self, ctx: Context):
        ctx.reply(f"Hello {player}!")
    ```
    """

    def decorator(fn: Callable) -> EventListener:
        return EventListener(fn, event)

    if fn:
        return EventListener(fn, event)
    else:
        return decorator