from __future__ import annotations
from typing import Optional, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from mconduit.ui.component import BaseComponent
    from mconduit.server import Server


C = TypeVar("C", bound=BaseComponent)


class UiRenderer:
    """
    Main class responsible to render all the UI components and text click events too
    """

    
    _server: Server


    def __init__(
        self,
        server: Server
    ) -> None:
        
        self._server = server


    def create_component_base_id(self, component: C) -> None:
        return f"mconduit-{type(component).__name__.lower()}-"

    
    def edit_data(
        self,
        name: str,
        value: str,
        action: str = "set",
        *,
        at: Optional[int] = None # Needed only if action = "insert"
    ) -> None:
        
        cmd = f"data entity modify {name} {action} "

        if action == "insert":
            
            if at is None:
                raise ValueError("The at parameter cannot be None if you want to insert data")
            
            cmd += f"{at} "

        cmd += f"value {value}"

        self._server.execute(cmd)