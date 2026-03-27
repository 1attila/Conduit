from typing import Optional, Dict, TYPE_CHECKING
import parse
import json
import re

from ..enums import Dimension, Gamemode
from .location import Location
from .vec3d import Vec3d

if TYPE_CHECKING:
    from ..server import Server


BASE_FORMATTER = r"{player} has the following entity data: {data}"
DIMENSION_FORMATTER = r'"minecraft:{dimension}"'
LOCATION_FORMATTER = r"{{pos: [I; {x}, {y}, {z}], dimension: {dimension}}}"


def _parse_dimension(data: str) -> Dimension:
    
    if parsed := parse.parse(DIMENSION_FORMATTER, data):
        
        data = parsed["dimension"]
        
        match data:

            case "the_end":
                return Dimension.End
            
            case "overworld":
                return Dimension.Overworld
            
            case "the_nether":
                return Dimension.Nether
            

def _parse_gamemode(data: str) -> Gamemode:

    match data:
        case "1":
            return Gamemode.Creative
        
        case "0":
            return Gamemode.Survival
        
        case "3":
            return Gamemode.Spectator
        
        case "2":
            return Gamemode.Adventure


def _parse_location(data: str) -> Optional[Location]:
    
    if parsed := parse.parse(LOCATION_FORMATTER, data):
        
        x, y, z = parsed["x"], parsed["y"], parsed["z"]

        location = Location()
        location.pos = Vec3d(x, y, z)
        location.dimension = _parse_dimension(parsed["dimension"])

        return location


def _cast_data(data: str, _type: object) -> object:
    """
    Utility function that can be used recursively to unpack and cast data
    """
    
    if _type is str:
        return data

    if isinstance(_type, (int, float, bool)):
        
        suffixes = ["b", "f", "d", "s"]

        for suffix in suffixes:
            if data.endswith(suffix):
                return _type(data[0:-1]) # type: ignore

        return _type(data) # type: ignore

    if isinstance(_type, Dict):

        data = data.replace("count:", '"count":') # item, inventory
        data = data.replace("Slot:", '"Slot":') # inventory
        data = data.replace("id:", '"id":') # item, inventory
        
        data = re.sub(r'"Slot": (\d+)b', r'"Slot": "\1"', data)

        return json.loads(data)

    if isinstance(_type, list):
        return data[1:-1].split(", ")
    
    if _type is Dimension:
        return _parse_dimension(data)

    if _type is Gamemode:
        return _parse_gamemode(data)
    
    if _type is Location:
        return _parse_location(data)


class EntityDataFetcher:
    """
    Contains utility methods to fetch entity data
    """


    _name: str
    _server: "Server"

    
    def _fetch(
        self,
        attribute: str,
        _type: object = str
    ) -> Optional[object]:
        """
        Fetches a specific player/mob/entity attribute and casts it automatically with the given type
        """
        
        response = self._server.execute(f"/data get entity {self._name} {attribute}")
        
        if not response: # Rcon connection failed
            return # type: ignore

        if not response.startswith("Found no elements matching "): # type: ignore
            
            parsed = parse.parse(BASE_FORMATTER, response)
            
            if parsed is None: # data fetching fails with carpet bots smh
                return # type: ignore

            data = parsed["data"]
            
            try:
                data = _cast_data(str(data).strip(), _type)
            except:
                return # type: ignore

            return data

        if _type is bool:
            return False