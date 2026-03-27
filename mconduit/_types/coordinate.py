from typing import TypeAlias

from .vec3d import Vec3d


Coordinate: TypeAlias = str | Vec3d


def relative(offset_x: float=0, offset_y: float=0, offset_z: float=0) -> str:
    """
    Return a string that can be used in commands to indicate the coordinates of where the command is executed plus the given offset.

    E.g:
    relative(1, 2, 3) --> `"^1 ^2 ^3"`
    """

    if offset_x == offset_y == offset_z == 0:
        return "~ ~ ~"

    return f"^{offset_x} ^{offset_y} ^{offset_z}"