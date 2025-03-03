from typing import Optional, NoReturn, List, TYPE_CHECKING

from .entity_data_fetcher import EntityDataFetcher
from .vec3d import Vec3d
from .rot import Rot
from ..Text import Text

if TYPE_CHECKING:
    from Conduit.server import Server


class Entity(EntityDataFetcher):
    """
    Entity class containing every field
    returned from 'data entity <entity>'

    Note that all the fields have been converted from camel-case to
    snake-case to follow Python's naming convention.
    Most boolean fields are a bit different to better follow
    Python's naming convention
    (E.g. 'custon_name_visible' -> 'is_custom_name visible').
    """

    __name: str
    __server: "Server"

    def __init__(self, name: str, server: "Server") -> NoReturn:
        self.__name = name
        self.__server = server


    @property
    def _name(self) -> str:
        """
        Entity name used in commands
        """

        return self.__name

    
    @property
    def _server(self) -> "Server":
        """
        Entity server
        """

        return self.__server
    
    
    @property
    def air(self) -> int:
        """
        How much air the entity has
        """

        return self._fetch("Air", int)


    @property
    def custom_name(self) -> Optional[Text]:
        """
        Entity custom Text name.

        It may not exist
        """

        return Text.from_dict(self._fetch("CustomName"))
    
    
    @property
    def is_custom_name_visible(self) -> bool:
        """
        True if custom name is displayed above entity.

        If custom name doesn't exist returns False
        """

        return self._fetch("CustomNameVisible", bool)


    @property
    def fall_distance(self) -> float:
        """
        Distance the entity has fallen
        """

        return self._fetch("FallDistance", float)


    @property   
    def fire(self) -> int:
        """
        Number of ticks until the fire is put out.

        Default is -20 when the entity is not on fire
        """

        return self._fetch("Fire", int)
    
    
    @property
    def is_glowing(self) -> bool:
        """
        Warning: Not following naming conventions.

        True if the entity has a glowing outline.

        Not avaiable for players
        """

        return self._fetch("Glowing", bool)
    

    @property
    def has_visual_fire(self) -> bool:
        """
        True if the entity even appears on fire, even if it's not.

        Not avaiable for players
        """

        return self._fetch("HasVisualFire", bool)
    

    @property
    def id(self) -> int:
        """
        Entity ID.

        Not avaiable for players
        """

        return self._fetch("id", bool)
    

    @property
    def invulnerable(self) -> bool:
        """
        True if the entity doesn't take damage
        """

        return self._fetch("Invulnerable", bool)


    @property
    def motion(self) -> Vec3d:
        """
        Entity motion
        """

        return Vec3d.from_string(self._fetch("Motion"))


    @property
    def no_gravity(self) -> bool:
        """
        True if the entity doesn't fall down naturally.

        Not avaiable for players
        """

        return self._fetch("NoGravity", bool)


    @property    
    def is_on_ground(self) -> bool:
        """
        Warning: Not following naming conventions.

        True if the entity is touching the ground
        """

        return self._fetch("OnGround", bool)
    

    @property
    def portal_cooldown(self) -> int:
        """
        Number of ticks before which the entity may be teleported back through a nether portal
        """

        return self._fetch("PortalCooldown", int)
    

    @property
    def pos(self) -> Vec3d:
        """
        Entity pos
        """

        return Vec3d.from_string(self._fetch("Pos"))
    

    @property
    def rotation(self) -> Rot:
        """
        Entity rotation
        """

        return Rot.from_string(self._fetch("Rotation"))
    

    @property
    def is_silent(self) -> Optional[bool]:
        """
        Warning: Not following naming conventions.

        True if the entity is silenced.
        It may not exist.

        Not avaiable for players
        """

        return self._fetch("Silent", bool)
    

    @property
    def tags(self) -> Optional[List[str]]:
        """
        List of all the entity tags.

        It may not exist
        """

        return self._fetch("Tags", list)
    

    @property
    def ticks_frozen(self) -> Optional[int]:
        """
        How many ticks the entity has been freezing.

        It may not exist.

        Not avaiable for players
        """

        return self._fetch("TicksFrozen", int)
    

    @property
    def uuid(self) -> str:
        """
        Entity UUID
        """

        return self._fetch("UUID", str)