from typing import Tuple, Optional

import parse


class Vec3d:
    """
    Tiny 3d vector class that can be used to store motion/position values.
    
    Supports some basic arythmetic operations (+-*/=).
    """

    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):

        self.x = x
        self.y = y
        self.z = z


    @staticmethod
    def from_vec(vec3d: "Vec3d") -> "Vec3d":
        return Vec3d(vec3d.x, vec3d.y, vec3d.z)

    
    @staticmethod
    def from_string(string: str) -> Optional["Vec3d"]:

        pattners = (
            r"[{x:f}d, {y:f}d, {z:f}d]",
            r"{{x: {x:f}d, y: {y:f}d, z: {z:f}d}}",
        )

        for pattner in pattners:
            
            data = parse.parse(pattner, string)

            if data:
            
                x, y, z, = data["x"], data["y"], data["z"]
            
                return Vec3d(x, y, z)
        
    
    def __eq__(self, other: "Vec3d") -> bool:
        return self.as_tuple() == other.as_tuple()
    

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
    

    def __mul__(self, value: float) -> "Vec3d":

        return Vec3d(
            self.x * value,
            self.y * value,
            self.z * value
        )
    

    def __div__(self, value: float) -> "Vec3d":

        return Vec3d(
            self.x / value,
            self.y / value,
            self.z / value
        )


    def __str__(self) -> str:
        return f"({self.x} {self.y} {self.z})"
    
    
    def __repr__(self) -> str:
        return f"Vec3d x:{self.x}, y:{self.y}, z:{self.z}"
    

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)