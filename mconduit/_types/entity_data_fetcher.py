from __future__ import annotations
from typing import TypeVar, Type, Optional, Dict, Any, overload, cast, TYPE_CHECKING
import nbtlib # type: ignore[import-untyped]
import parse # type: ignore[import-untyped]

from mconduit.enums import Dimension, Gamemode
from .location import Location
from .vec3d import Vec3d

if TYPE_CHECKING:
    from mconduit.server import Server


BASE_FORMATTER = r"{player} has the following entity data: {data}"
DIMENSION_FORMATTER = r'minecraft:{dimension}'
LOCATION_FORMATTER = r"{{pos: [I; {x}, {y}, {z}], dimension: {dimension}}}"

_T = TypeVar("_T")


class ParsingError(Exception):
    """
    Unable to parse the string as expected
    """


def _parse_dimension(data: str) -> Dimension:

    if parsed := parse.parse(DIMENSION_FORMATTER, data):
        
        data = parsed["dimension"]
        
        match data:

            case "the_end":
                return Dimension.END
            
            case "overworld":
                return Dimension.OVERWORLD
            
            case "the_nether":
                return Dimension.NETHER

    raise ParsingError
            

def _parse_gamemode(gamemode_id: int) -> Gamemode:

    match gamemode_id:
        case 1:
            return Gamemode.CREATIVE
        
        case 0:
            return Gamemode.SURVIVAL
        
        case 3:
            return Gamemode.SPECTATOR
        
        case 2:
            return Gamemode.ADVENTURE

    raise ParsingError


def _parse_location(data: nbtlib.Compound) -> Optional[Location]:
        
    pos = _cast_data(data["pos"], list)

    location = Location()
    location.pos = Vec3d(*pos)
    location.dimension = _parse_dimension(data["dimension"])

    return location


def _cast_data(data: Any, _type: Type[_T]) -> _T:
    """
    Utility function that can be used recursively to unpack and cast data
    """
    
    if _type is str:
        return cast(_T, data)
    
    if _type is Dimension:
        return cast(_T, _parse_dimension(data))

    if _type is Gamemode:
        return cast(_T, _parse_gamemode(data))
    
    if _type is Location:
        return cast(_T, _parse_location(data))

    return cast(_T, cast(Any, _type)(data))


class UnableToFetchData(Exception):
    """
    Probably because of bad Rcon connection, attempt again
    """


class AttributeNotFound(Exception):
    """
    The attribute is not present in the nbt, it may be optional!
    """


class EntityDataFetcher:
    """
    Contains utility methods to fetch entity data
    """


    _name: str
    _server: Server
    _nbt_cache: Optional[Dict[str, Any]]


    def __init__(
        self,
        name: str,
        server: Server
    ) -> None:

        self._name = name
        self._server = server
        self._nbt_cache = None


    def clean_cache(self) -> None:
        """
        Empties the nbt cache
        """

        self._nbt_cache = None

    
    def _get_full_nbt(self) -> None:
        """
        Fetches the full nbt via Rcon, if cache is empty
        """

        if self._nbt_cache is not None:
            return None

        response = self._server.execute(f"data get entity {self._name}")

        if not isinstance(response, str) or response.startswith("Found no elements"): # Rcon connection failed

            self._nbt_cache = {}
            return None

        parsed = parse.parse(BASE_FORMATTER, response)

        if parsed is None: # Data fetching fails with carpet bots smh
            raise RuntimeError("Unable to parse the entity data")

        data = parsed["data"]
        
        self._nbt_cache = nbtlib.parse_nbt(data).unpack()
        
        return None


    @overload
    def _fetch(
        self,
        attribute: str
    ) -> str:
        ...


    @overload
    def _fetch(
        self,
        attribute: str,
        _type: Type[_T]
    ) -> _T:
        ...
    
    
    def _fetch(
        self,
        attribute: str,
        _type: Any = str
    ) -> Any:
        """
        Fetches a specific player/mob/entity attribute and casts it automatically with the given type
        """

        self._get_full_nbt()

        if self._nbt_cache is None:
            raise UnableToFetchData
        
        if attribute not in self._nbt_cache:
            raise AttributeNotFound

        return _cast_data(self._nbt_cache[attribute], _type)