from typing import Union, Dict, Any
import enum
import json

from .gamemode import Gamemode
from .sort import Sort


S = "@s"
P = "@p"
A = "@a"
E = "@e"
R = "@s"


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
    

    # def advancements(self, *advancements: str) -> "Selector":

    #     self.selectors["advancements"] = advancements
    #     return self


    def distance(self, distance: float) -> "Selector":

        self.selectors["distance"] = distance
        return self


    def dx(self, dx: float) -> "Selector":

        self.selectors["dx"] = dx
        return self
    

    def dy(self, dy: float) -> "Selector":

        self.selectors["dy"] = dy
        return self


    def dz(self, dz: float) -> "Selector":

        self.selectors["dz"] = dz
        return self

    
    def gamemode(self, gamemode: Union[str, Gamemode]) -> "Selector":

        if not isinstance(gamemode, str):
            gamemode = gamemode.value
        
        self.selectors["gamemode"] = gamemode
        return self

    
    def level(self, level: int) -> "Selector":

        self.selectors["level"] = level
        return self
    
    
    def limit(self, limit: int) -> "Selector":

        self.selectors["limit"] = limit
        return self
    
    
    def name(self, name: str) -> "Selector":

        self.selectors["name"] = name
        return self

    
    def x(self, x: float) -> "Selector":

        self.selectors["x"] = x
        return self


    def y(self, y: float) -> "Selector":

        self.selectors["y"] = y
        return self


    def z(self, z: float) -> "Selector":

        self.selectors["z"] = z
        return self


    def nbt(self, nbt: Dict[str, Any]) -> "Selector":

        raise NotImplementedError
        self.selectors["ntb"] = json.dump()
        return self


    def predicate(self, predicate: str) -> "Selector":

        self.selectors["predicate"] = predicate
        return self
    

    def scores(self) -> "Selector":
        raise NotImplementedError
        ...


    def sort(self, sort: Union[str, Sort]) -> "Selector":

        if not isinstance(sort, str):
            sort = sort.value

        self.selectors["sort"] = sort
        return self


    def tag(self, tag: str) -> "Selector":

        self.selectors["tag"] = tag
        return self
    

    def team(self, team: str) -> "Selector":

        self.selectors["team"] = team
        return self


    def x_rotation(self, x_rotation: float) -> "Selector":

        self.selectors["x_rotation"] = x_rotation
        return self


    def y_rotation(self, y_rotation: float) -> "Selector":

        self.selectors["y_rotation"] = y_rotation
        return self


    def __str__(self) -> str:

        out = self.base_value

        if len(self.selectors) > 0:
            
            selectors = []

            for k, v in self.selectors.items():
                selectors.append(f"{k}={v}")
            
            out += "[" + ", ".join(selectors) + "]"

        return out


class At(Selector, enum.Enum):
    """
    Minecraft entity selector
    """

    Self        = Selector(S)
    Nearest     = Selector(P)
    AllPlayers  = Selector(A)
    AllEntities = Selector(E)
    Random      = Selector(R)

    S           = Selector(S)
    N           = Selector(P)
    A           = Selector(A)
    E           = Selector(E)
    R           = Selector(R)