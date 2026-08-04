from typing import Union, Callable, Concatenate, ParamSpec, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mconduit.context import Context
    from mconduit.server import Server
    from mconduit.handler import Handler


P = ParamSpec("P")

CommandEventFunc = Callable[Concatenate["Context", P], Any]
PlayerEventFunc = Callable[["Context"], Any]
ServerEventFunc = Callable[["Server"], Any]
HandlerEventFunc = Callable[["Handler"], Any]

EventFunc = Union[
    CommandEventFunc,
    PlayerEventFunc,
    ServerEventFunc,
    HandlerEventFunc
]