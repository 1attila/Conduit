from typing import Optional, List, TYPE_CHECKING
from math import sin, cos, pi

from .entity_data_fetcher import EntityDataFetcher, AttributeNotFound
from .vec3d import Vec3d
from .rot import Rot
from mconduit.text.text import Text

if TYPE_CHECKING:
    from mconduit.server import Server


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


    def __init__(
        self,
        name: str,
        server: "Server"
    ) -> None:

        super().__init__(name, server)
    
    
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

        try:
            custom_name = self._fetch("CustomName", dict)
            return Text.from_dict(custom_name)
        
        except AttributeNotFound:
            return None
    
    
    @property
    def is_custom_name_visible(self) -> Optional[bool]:
        """
        True if custom name is displayed above entity.

        If custom name doesn't exist returns None
        """

        try:
            return self._fetch("CustomNameVisible", bool)

        except AttributeNotFound:
            return None


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

        motion = self._fetch("Motion", list)
            
        return Vec3d(*motion)


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

        pos = self._fetch("Pos", list)
        
        return Vec3d(*pos)
    

    @property
    def rotation(self) -> Rot:
        """
        Entity rotation
        """

        rot = self._fetch("Rotation", list)
        
        return Rot(*rot)
    

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

        try:
            return self._fetch("Tags", list)

        except AttributeNotFound:
            return None
    

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
        
        return "-".join([hex(bit)[2:] for bit in self._fetch("UUID", list)])


    @property
    def forward_vec(self) -> Vec3d:
        """
        Indicates where the entity it's looking
        """

        rot = self.rotation
        
        rot = rot * pi / 180
        
        return Vec3d(
            -sin(rot.yaw) * cos(rot.pitch),
            -sin(rot.pitch),
            cos(rot.yaw) * cos(rot.pitch)
        ).normalize()