from typing import Optional
import parse

from ..Enums import Dimension, Gamemode
from . import Location, Rot, Vec3d


BASE_FORMATTER = r"{player} has the following entity data: {data}"
LOCATION_FORMATTER = r"{pos: [I; {:d}, {:d}, {:d}], dimension: \"{}\"}"


def _parse_location(data: str) -> Optional[Location]:

    parsed = parse.parse(LOCATION_FORMATTER, data)

    if parsed:
        ...


def _convert_data(data: str, _type: object) -> object:
    """
    Utility function that can be used recursively to unpack and convert data
    """
    
    if _type is str:
        return data

    if _type is int or _type is float or _type is bool:
        
        suffixes = ["b", "f", "d", "s"]

        for suffix in suffixes:
            if data.endswith(suffix):
                return _type(data[0:-1])

    if _type is list:
        return data[1:-1].split(", ")
    
    if _type is Location:
        ...

    if _type is Rot:
        ...

    if _type is Vec3d:
        ...


class EntityDataFetcher:
    """
    Contains utility methods to fetch entity data
    """
    
    
    def _fetch(self, attribute: str, _type: object=str) -> Optional[object]:
        """
        Fetches a specific player/mob/entity attribute and casts it automatically with the given type
        """
        
        response = self._server.execute(f"/data get entity {self._name} {attribute}")
        
        if not response.startswith("Found no elements matching "):
            
            parsed = parse.parse(BASE_FORMATTER, response)
            
            data = parsed["data"]

            data = _convert_data(str(data).strip(), _type)
            
            return data

        if _type is bool:
            return False