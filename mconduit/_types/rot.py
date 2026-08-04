from typing import Tuple
from enum import Enum

import parse # type: ignore[import-untyped]


class XRot(Enum):
    North = -180 # +- 180
    East = -90
    South = 0
    West = 90


class YRot(Enum):
    Down = 90
    Up = -90


class Direction:

    x: XRot
    y: YRot

    def __init__(
        self,
        yaw: float,
        pitch: float
    ) -> None:

        if -45 <= yaw < 45:
            self.x = XRot.South
        elif -135 <= yaw < 45:
            self.x = XRot.East
        elif 45 <= yaw < 135:
            self.x = XRot.West
        elif 0 <= abs(yaw) < 135: #TODO: Fix
            self.x = XRot.North
        else:
            raise Exception

        self.y = YRot.Down if pitch > 0 else  YRot.Up


class Rot:
    """
    Class that rapresent Rotation data

    Attributes:
    -yaw: rotation around the Y axis. Range [-180..180].
    -pitch: declination from the horizon. Range [-90..90].
    -direction: x and y cardinal directions
    
    Like Vec3d supports some basic arythmetic operations (+-*/=).
    """

    yaw: float # [-180..180]
    pitch: float # [-90..90]
    direction: Direction


    def __init__(
        self,
        yaw: float,
        pitch: float,
        degrees: bool = False
    ) -> None:

        if degrees is True:
            yaw = (yaw + 180) % 360 - 180
            pitch = max(min(pitch, 90), -90)
        
        self.yaw = yaw
        self.pitch = pitch
        # self.direction = Direction(self.yaw, self.pitch)


    @staticmethod
    def from_rot(rot: "Rot") -> "Rot":
        return Rot(rot.yaw, rot.pitch)


    @staticmethod
    def from_string(string: str) -> "Rot":
        
        data = parse.parse(r"[{yaw:f}f, {pitch:f}f]", string)

        if data:

            yaw, pitch = data["yaw"], data["pitch"]

            return Rot(yaw, pitch)

        raise ValueError(f"Invalid string: {string}")

    
    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Rot):
            return False
        
        return self.as_tuple() == other.as_tuple()
    

    def __add__(self, other: "Rot") -> "Rot":

        return Rot(
            self.yaw + other.yaw,
            self.pitch + other.pitch
        )
    

    def __sub__(self, other: "Rot") -> "Rot":

        return Rot(
            self.yaw - other.pitch,
            self.yaw - other.pitch
        )
    

    def __mul__(self, value: float) -> "Rot":

        return Rot(
            self.yaw * value,
            self.pitch * value
        )
    

    def __truediv__(self, value: float) -> "Rot":

        return Rot(
            self.yaw / value,
            self.pitch / value
        )


    def __str__(self) -> str:
        return f"({self.yaw} {self.pitch})"
    
    
    def __repr__(self) -> str:
        return f"Rot pitch:{self.pitch}, yaw:{self.yaw}"
    

    def as_tuple(self) -> Tuple[float, float]:
        return (self.yaw, self.pitch)