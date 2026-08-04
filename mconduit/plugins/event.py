from __future__ import annotations
from typing import Callable, Optional, Any, overload, TYPE_CHECKING

from mconduit.event import Event

if TYPE_CHECKING:
    from mconduit._types import EventFunc


class EventListener:
    """
    Internal class used to register events
    """
    
    _callback: EventFunc
    _event: Event


    def __init__(
        self,
        callback: EventFunc,
        event: Optional[Event] = None
    ) -> None:

        self._callback = callback

        if event is None:
            self._event = {
                "on_player_join":    Event.PLAYER_JOIN,
                "on_player_left":    Event.PLAYER_LEFT,
                "on_player_death":   Event.PLAYER_DEATH,
                "on_player_message": Event.PLAYER_CHAT,
                "on_player_command": Event.PLAYER_COMMAND,
                "on_server_start":   Event.SERVER_START,
                "on_server_stop":    Event.SERVER_STOP
            }[callback.__name__]
        
        else:
            self._event = event
    

@overload
def event(event: Event,  /) -> Callable:
    ...


@overload
def event(fn: EventFunc, /) -> EventListener:
    ...


@overload
def event(*, event: Event) -> Callable:
    ...


def event(
    fn_or_event: Any = None,
    *,
    event: Any = None
) -> Any:
    """
    A decorator that links the function to the given event (or the event named as the function if not provided)

    Examples::

        @plugins.event
        def on_player_command(self, ctx: Context):
            ...

        @plugins.event(Event.PLAYER_JOIN)
        def greet(self, ctx: Context):
            ctx.reply(f"Hello {player}!")
    """

    def decorator(fn: EventFunc) -> EventListener:

        assert isinstance(fn_or_event, Event)
        return EventListener(fn, fn_or_event)

    if fn_or_event is not None and isinstance(fn_or_event, Event):
        return decorator

    if event is not None:
        fn_or_event = event
        return decorator

    if fn_or_event is not None and callable(fn_or_event):
        return EventListener(fn_or_event)

    return decorator