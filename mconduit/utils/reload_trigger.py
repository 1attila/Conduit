from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mconduit.handler import Handler


def reload_trigger(handler: "Handler") -> None:
    """
    This function simply triggers the handler._reload() function if the _reload_flag is set to True.

    This is needed because calling handler._reload() directly raises RuntimeError since the execution isn't fully finished 
    """
    
    if handler._reload_flag is True:
        handler._reload()