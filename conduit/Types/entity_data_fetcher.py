from typing import Optional, Dict
import parse
import json
import re

from ..Enums import Dimension, Gamemode
from .location import Location
from .vec3d import Vec3d


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

    if _type is int or _type is float or _type is bool:
        
        suffixes = ["b", "f", "d", "s"]

        for suffix in suffixes:
            if data.endswith(suffix):
                return _type(data[0:-1])

        return _type(data)

    if _type is Dict:

        data = data.replace("count:", '"count":')
        data = data.replace("Slot:", '"Slot":')
        data = data.replace("id:", '"id":')
        data = re.sub(r'"Slot": (\d+)b', r'"Slot": "\1"', data)

        return json.loads(data)

    if _type is list:
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
    

    def _get_loop(self, attribute: str, timeout: float=10) -> Optional[object]:
        """
        
        """

        response = self._server.execute(f"/data get entity {self._name} {attribute}")

    
    def _fetch(self, attribute: str, _type: object=str) -> Optional[object]:
        """
        Fetches a specific player/mob/entity attribute and casts it automatically with the given type
        """
        
        response = self._server.execute(f"/data get entity {self._name} {attribute}")
        
        if not response: #TODO: handle this in a better way
            return

        if not response.startswith("Found no elements matching "):
            
            parsed = parse.parse(BASE_FORMATTER, response)
            
            data = parsed["data"]
            
            data = _cast_data(str(data).strip(), _type)
            
            return data

        if _type is bool:
            return False