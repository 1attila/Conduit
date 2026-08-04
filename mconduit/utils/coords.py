from typing import Union, Tuple, Generator, overload
from math import floor

from mconduit._types.vec3d import Vec3d


def approx_fix(v: Vec3d) -> Vec3d:
    """
    Needed to prevent bad entity pos approximation with negative values
    """

    def fix_component(component: float) -> float:

        if component >= 0:
            return component

        decimal_digits = int(str(component + 0.0).split(".")[1])
        decimal_component = decimal_digits / (10 ** len(str(decimal_digits)))

        if decimal_component >= 0.5:
            return component - 0.5
        
        return component

    v.x = fix_component(v.x)
    v.z = fix_component(v.z)

    return v


def ow_to_nether(v: Vec3d) -> Vec3d:
    """
    Overworld coords -> Nether coords
    """

    return Vec3d(
        floor(v.x / 8),
        floor(v.y / 8),
        floor(v.z / 8)
    )


def chunk_coords(v: Vec3d) -> Vec3d:
    """
    Returns the coords of the chunk where the given block is located
    """

    return Vec3d(
        floor(v.x / 16),
        floor(v.y / 16),
        floor(v.z / 16)
    )


def chunk_to_region(
    chunk_x: int,
    chunk_z: int
) -> Tuple[int, int]:
    """
    Return the region coordinate where the given chunk is located
    """

    return (
        floor(chunk_x / 32),
        floor(chunk_z / 32)
    )


@overload
def iter_coord(
    start: int,
    end: int
) -> Generator[int, None, None]:
    ...


@overload
def iter_coord(
    start: Vec3d,
    end: Vec3d
) -> Generator[Vec3d, None, None]:
    ...


def iter_coord(
    start: Union[Vec3d, int],
    end: Union[Vec3d, int]
) -> Generator[Union[Vec3d, int], None, None]:
    """
    Similar to `range(start, end)` or `range(end, start)` but with both extremes included.

    If `start` == `end` it yields `start` once
    """

    if start == end:
        yield start
        return

    if isinstance(start, int):

        assert isinstance(end, int)

        if start < end:
            yield from range(start, end + 1)
        else:
            yield from range(start, end - 1, -1)
    
    else:
        assert isinstance(end, Vec3d)

        for x in iter_coord(int(start.x), int(end.x)):
            for y in iter_coord(int(start.y), int(end.y)):
                for z in iter_coord(int(start.z), int(end.z)):
                    yield Vec3d(x, y, z)