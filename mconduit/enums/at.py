from typing import Union, Dict, Any
import json

from .gamemode import Gamemode
from .sort import Sort


S = "@s"
P = "@p"
A = "@a"
E = "@e"
R = "@r"


class Selector:
    """
    Minecraft entity selector
    """
    
    base_value: str
    selectors: Dict[str, Any]


    def __init__(
        self,
        base_value: str
    ) -> None:

        self.base_value = str(base_value)
        self.selectors = {}

    
    def _clone(self) -> "Selector":

        clone = Selector(self.base_value)
        clone.selectors = self.selectors.copy()

        return clone
    

    def advancements(self, *advancements: str) -> "Selector":

        clone = self._clone()
        clone.selectors["advancements"] = list(*advancements)
        
        return clone


    def distance(self, distance: float) -> "Selector":
        
        clone = self._clone()
        clone.selectors["distance"] = distance

        return clone


    def dx(self, dx: float) -> "Selector":

        clone = self._clone()
        clone.selectors["dx"] = dx

        return clone
    

    def dy(self, dy: float) -> "Selector":
        
        clone = self._clone()
        clone.selectors["dy"] = dy

        return clone


    def dz(self, dz: float) -> "Selector":

        clone = self._clone()
        clone.selectors["dz"] = dz

        return clone

    
    def gamemode(self, gamemode: Union[str, Gamemode]) -> "Selector":
        
        clone = self._clone()

        if not isinstance(gamemode, str):
            gamemode = gamemode.value
        
        clone.selectors["gamemode"] = gamemode
        return clone

    
    def level(self, level: int) -> "Selector":

        clone = self._clone()
        clone.selectors["level"] = level
        
        return clone
    
    
    def limit(self, limit: int) -> "Selector":

        clone = self._clone()
        clone.selectors["limit"] = limit

        return clone
    
    
    def name(self, name: str) -> "Selector":

        clone = self._clone()
        clone.selectors["name"] = name

        return clone

    
    def x(self, x: float) -> "Selector":

        clone = self._clone()
        clone.selectors["x"] = x
        
        return clone


    def y(self, y: float) -> "Selector":
        
        clone = self._clone()
        clone.selectors["y"] = y
        
        return clone


    def z(self, z: float) -> "Selector":

        clone = self._clone()
        clone.selectors["z"] = z
        
        return clone


    def nbt(self, nbt: Dict[str, Any]) -> "Selector":

        clone = self._clone()

        clone.selectors["nbt"] = json.dumps(nbt)
        return clone


    def predicate(self, predicate: str) -> "Selector":

        clone = self._clone()
        clone.selectors["predicate"] = predicate

        return clone
    

    def scores(self, scores: Dict[str, Any]) -> "Selector":
        
        clone = self._clone()
        formatted = "{" + ",".join([f"{k}={v}" for k, v in scores.items()]) + "}"
        clone.selectors["scores"] = formatted

        return clone
    

    def sort(self, sort: Union[str, Sort]) -> "Selector":

        clone = self._clone()

        if not isinstance(sort, str):
            sort = sort.value

        clone.selectors["sort"] = sort

        return clone


    def tag(self, tag: str) -> "Selector":

        clone = self._clone()
        clone.selectors["tag"] = tag
        
        return clone
    

    def team(self, team: str) -> "Selector":

        clone = self._clone()
        clone.selectors["team"] = team
        
        return clone


    def x_rotation(self, x_rotation: float) -> "Selector":

        clone = self._clone()
        clone.selectors["x_rotation"] = x_rotation
        
        return clone


    def y_rotation(self, y_rotation: float) -> "Selector":

        clone = self._clone()
        clone.selectors["y_rotation"] = y_rotation
        
        return clone


    def __str__(self) -> str:

        out = self.base_value

        if len(self.selectors) > 0:
            
            selectors = []

            for k, v in self.selectors.items():
                selectors.append(f"{k}={v}")
            
            out += "[" + ", ".join(selectors) + "]"

        return out


class At:
    """
    Minecraft entity selector
    """


    SELF         = Selector(S)
    NEAREST      = Selector(P)
    ALL_PLAYERS  = Selector(A)
    ALL_ENTITIES = Selector(E)
    RANDOM       = Selector(R)

    S            = Selector(S)
    N            = Selector(P)
    A            = Selector(A)
    E            = Selector(E)
    R            = Selector(R)