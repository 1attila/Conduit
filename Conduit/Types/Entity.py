from typing import NoReturn, Optional, List, Dict, TYPE_CHECKING

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
    def air(self) -> int:
        return int(self.__fetch("Air"))

    custom_name: str # ATTENTION: This type it's temporary, it will be replaced soon!
    is_custom_name_visible: bool

    @property
    def fall_distance(self) -> float:
        return float(self.__fetch("FallDistance"))

    @property   
    def fire(self) -> int:
        return int(self.__fetch("Fire"))
    
    @property
    def is_glowing(self) -> bool: # Not following naming convention
        return bool(self.__fetch("Glowing"))
    
    has_visual_fire: bool
    id: int
    invulnerable: bool
    motion: Vec3d
    no_gravity: bool
    is_on_ground: bool # Not following naming convention
    passengers: List["Entity"]
    portal_cooldown: int
    pos: Vec3d
    rotation: Rot
    is_silent: bool # Not following naming convention
    tags: List[str]
    ticks_frozen: int
    uuid: str


    @classmethod
    def from_dict(dict: Dict) -> "Entity":
        
        entity = Entity()

        for k, v in dict:
            
            if hasattr(entity, k):
                entity.__dict__[k] = v