from typing import NoReturn, List, TYPE_CHECKING

from .EntityDataFetcher import EntityDataFetcher
from .Vec3d import Vec3d
from .Rot import Rot

if TYPE_CHECKING:
    from Conduit.Server import Server


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
        return self.__name

    
    @property
    def _server(self) -> "Server":
        return self.__server
    
    
    @property
    def air(self) -> int:
        return int(self.__fetch("Air"))

    custom_name: str # ATTENTION: This type it's temporary, it will be replaced soon!
    
    @property
    def is_custom_name_visible(self) -> bool:
        return bool(self.__fetch("CustomNameVisible"))


    @property
    def fall_distance(self) -> float:
        return float(self.__fetch("FallDistance"))


    @property   
    def fire(self) -> int:
        return int(self.__fetch("Fire"))
    
    
    @property
    def is_glowing(self) -> bool: # Not following naming convention
        return bool(self.__fetch("Glowing"))
    

    @property
    def has_visual_fire(self) -> bool:
        return bool(self.__fetch("HasVisualFire"))
    

    @property
    def id(self) -> int:
        return int(self.__fetch("id"))
    

    @property
    def invulnerable(self) -> bool:
        return bool(self.__fetch("Invulnerable"))


    @property
    def motion(self) -> Vec3d:
        return Vec3d.fetch(self.__fetch("Motion"))


    @property
    def no_gravity(self) -> bool:
        return bool(self.__fetch("NoGravity"))


    @property    
    def is_on_ground(self) -> bool: # Not following naming convention
        return bool(self.__fetch("OnGround"))
    

    passengers: List["Entity"]

    @property
    def portal_cooldown(self) -> int:
        return int(self.__fetch("PortalCooldown"))
    

    @property
    def pos(self) -> Vec3d:
        return Vec3d.fetch(self.__fetch("Pos"))
    

    @property
    def rotation(self) -> Rot:
        return Rot.fetch(self.__fetch("Rotation"))
    

    @property
    def is_silent(self) -> bool: # Not following naming convention
        return bool(self.__fetch("Silent"))
    

    @property
    def tags(self) -> List[str]:
        return list(self.__fetch("Tags"))
    

    @property
    def ticks_frozen(self) -> int:
        return int(self.__fetch("TicksFrozen"))
    

    @property
    def uuid(self) -> int:
        return int(self.__fetch("UUID"))