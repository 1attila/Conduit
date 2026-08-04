from __future__ import annotations
from typing import TYPE_CHECKING
import enum
import copy

from mconduit.text.text import Text

if TYPE_CHECKING:
    from mconduit.server_api import ServerAPI


class RenderType(enum.StrEnum):
    """
    Score rendering type
    
    Could be:

    - Integer

    - Hearts
    """

    INTEGER = "integer"
    HEARTS  = "hearts"


class Objective:
    """
    Represents a Minecraft scoreboard objective
    """


    _criteria_name: str
    _display_name: Text
    _name: str
    _render_type: RenderType
    _display_auto_update: bool
    _server: ServerAPI


    def __init__(
        self,
        criteria_name: str,
        display_name: Text,
        name: str,
        render_type: RenderType = RenderType.INTEGER,
        display_auto_update: bool = False,
        *,
        server: ServerAPI
    ) -> None:
        
        self._criteria_name = criteria_name
        self._display_name = display_name
        self._name = name
        self._render_type = render_type
        self._display_auto_update = display_auto_update

        self._server = server
    

    @property
    def criteria_name(self) -> str:
        """
        Name of the objective criteria
        """

        return self._criteria_name


    @property
    def display_name(self) -> Text:
        """
        Name displayed in scoreboards
        """

        return copy.copy(self._display_name)


    @property
    def name(self) -> str:
        """
        Internal objective name
        """

        return self._name

    
    @property
    def render_type(self) -> RenderType:
        """
        Could be interger or hearts
        """

        return self._render_type


    @property
    def display_auto_update(self) -> bool:
        """
        If True, sidebar is updated automatically when the scores changes
        """

        return self._display_auto_update