from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
import enum
import copy

from mconduit._types.player import Player
from mconduit.enums.color import Color
from mconduit.text.text import Text

if TYPE_CHECKING:
    from mconduit.server import ServerAPI


class VisibilityOption(enum.StrEnum):
    NEWER                = "newer"
    HIDE_FOR_OTHER_TEAMS = "hideForOtherTeams"
    HIDE_FOR_OWN_TEAM    = "hideForOwnTeam"
    ALWAYS               = "always"


class CollisionRule(enum.StrEnum):
    ALWAYS           = "always"
    PUSH_OWN_TEAM    = "pushOwnTeam"
    NEWER            = "newer"
    PUSH_OTHER_TEAMS = "pushOtherTeams"


class Team:
    """
    Represents a Minecraft team
    """

    
    _allow_friendly_fire: bool
    _see_friendly_invisibles: bool
    _name_tag_visibility: VisibilityOption
    _death_message_visibility: VisibilityOption
    _collision_rule: CollisionRule
    _display_name: Text
    _name: str
    _member_name_prefix: Text
    _member_name_suffix: Text
    _team_color: Optional[Color]
    _players: List[Player]
    _server: ServerAPI


    def __init__(
        self,
        allow_friendly_fire: bool,
        see_friendly_invisibles: bool,
        name_tag_visibility: VisibilityOption,
        death_message_visibility: VisibilityOption,
        collision_rule: CollisionRule,
        display_name: Text,
        name: str,
        member_name_prefix: Text,
        member_name_suffix: Text,
        team_color: Optional[Color],
        players: List[Player],
        *,
        server: ServerAPI
    ) -> None:
        
        self._allow_friendly_fire = allow_friendly_fire
        self._see_friendly_invisibles = see_friendly_invisibles
        self._name_tag_visibility = name_tag_visibility
        self._death_message_vibility = death_message_visibility
        self._collision_rule = collision_rule
        self._display_name = display_name
        self._name = name
        self._member_name_prefix = member_name_prefix
        self._member_name_suffix = member_name_suffix
        self._team_color = team_color
        self._players = players
        
        self._server = server


    @property
    def allow_friendly_fire(self) -> bool:
        """
        If True player can hard each other
        """

        return self._allow_friendly_fire


    @property
    def see_friendly_invisibles(self) -> bool:
        """
        If True, player of this team can see invisible teammates
        """

        return self._see_friendly_invisibles
    

    @property
    def name_tag_visibility(self) -> VisibilityOption:
        """
        Nametag visibility option of this team
        """

        return self._name_tag_visibility


    @property
    def death_message_visibility(self) -> VisibilityOption:
        """
        Death message visibility option of this team 
        """

        return self._death_message_vibility


    @property
    def collision_rule(self) -> CollisionRule:
        """
        Collision rule option of this team
        """

        return self._collision_rule

    
    @property
    def display_name(self) -> Text:
        """
        Text used to display this team
        """

        return copy.copy(self._display_name)

    
    @property
    def name(self) -> str:
        """
        Internal name of this team
        """

        return self._name


    @property
    def member_name_prefix(self) -> Text:
        """
        Text prepended to the name of the players inside this team
        """

        return copy.copy(self._member_name_prefix)


    @property
    def member_name_suffix(self) -> Text:
        """
        Text appended to the name of the players inside this team
        """

        return copy.copy(self._member_name_suffix)

    
    @property
    def team_color(self) -> Optional[Color]:
        """
        Color of this team
        """

        return self._team_color


    @property
    def players(self) -> List[Player]:
        """
        All the players inside this team
        """

        return self._players
    

    @property
    def server(self) -> ServerAPI:
        """
        The server this belongs to
        """

        return self._server

    
    def create(self) -> None:
        raise NotImplementedError


    def delete(self) -> None:
        raise NotImplementedError

    
    def add_player(self) -> None:
        raise NotImplementedError


    def remove_player(self) -> None:
        raise NotImplementedError