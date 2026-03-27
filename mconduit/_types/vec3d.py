from typing import Tuple, Union, Optional
from math import sqrt

import parse


class Vec3d:
    """
    Tiny 3d vector class that can be used to store motion/position values.
    
    Supports some basic arythmetic operations (+-*/=).
    """

    x: float
    y: float
    z: float


    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0
    ) -> None:

        self.x = x
        self.y = y
        self.z = z


    @staticmethod
    def from_vec(vec3d: "Vec3d") -> "Vec3d":
        return Vec3d(vec3d.x, vec3d.y, vec3d.z)

    
    @staticmethod
    def from_string(string: str) -> "Vec3d":

        pattners = (
            r"[{x:f}d, {y:f}d, {z:f}d]",
            r"{{x: {x:f}d, y: {y:f}d, z: {z:f}d}}"
        )
        
        for pattner in pattners:
            
            data = parse.parse(pattner, string)

            if data:
            
                x, y, z, = data["x"], data["y"], data["z"]
            
                return Vec3d(x, y, z)

        raise ValueError(f"Invalid string: {string}")
        
    
    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Vec3d):
            return False
        
        return self.as_tuple() == other.as_tuple()

    
    def __hash__(self) -> int:
        return hash(self.as_tuple())
    

    def __add__(self, other: "Vec3d") -> "Vec3d":

        return Vec3d(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )
    

    def __sub__(self, other: "Vec3d") -> "Vec3d":

        return Vec3d(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )
    

    def __mul__(self, value: Union["Vec3d", float]) -> "Vec3d":

        if isinstance(value, Vec3d):

            return Vec3d(
                self.x * value.x,
                self.y * value.y,
                self.z * value.z
            )
        
        return Vec3d(
            self.x * value,
            self.y * value,
            self.z * value
        )
    

    def __truediv__(self, value: Union["Vec3d", float]) -> "Vec3d":

        if isinstance(value, Vec3d):
            
            return Vec3d(
                self.x / value.x,
                self.y / value.y,
                self.z / value.z
            )
        
        return Vec3d(
            self.x / value,
            self.y / value,
            self.z / value
        )

    
    def to_int(self) -> "Vec3d":

        self.x = int(self.x)
        self.y = int(self.y)
        self.z = int(self.z)

        return self


    def round(self, ndigits: Optional[int] = None) -> "Vec3d":

        self.x = round(self.x, ndigits)
        self.y = round(self.y, ndigits)
        self.z = round(self.z, ndigits)

        return self
    

    def normalize(self) -> "Vec3d":

        len = self.__len__()

        return Vec3d(
            self.x / len,
            self.y / len,
            self.z / len 
        )


    def cross(self, other: "Vec3d") -> "Vec3d":

        return Vec3d(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    

    def up(self, value: float = 1) -> "Vec3d":
        return self + Vec3d(0, value, 0)
    
    
    def down(self, value: float = 1) -> "Vec3d":
        return self - Vec3d(0, value, 0)
    

    @property
    def len(self, no_sqrt: bool=True) -> float:
        """
        Same as `__len__` but doesn't take the square root by default
        """

        length_squared = self.x * self.x + self.y * self.y + self.z * self.z

        if no_sqrt is True:
            return length_squared
        
        return sqrt(length_squared)
    
    
    def __len__(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)


    def __str__(self) -> str:
        return f"{self.x} {self.y} {self.z}"
    
    
    def __repr__(self) -> str:
        return f"Vec3d x:{self.x}, y:{self.y}, z:{self.z}"

    
    def __copy__(self) -> "Vec3d":
        return Vec3d(self.x, self.y, self.z)
    

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    
    def copy(self) -> "Vec3d":
        return self.__copy__()