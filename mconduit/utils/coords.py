from typing import Tuple, Iterator
from math import floor

from .._types.vec3d import Vec3d


def approx_fix(v: Vec3d) -> Vec3d:
    """
    Needed to prevent bad entity pos approximation with negative values
    """

    if v.x < 0 and abs(round(v.x) - v.x) >= 0.5:
        v.x -= 0.5

    if v.z < 0 and abs(round(v.z) - v.z) >= 0.5:
        v.z -= 0.5

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


def iter_coord(
    start: int,
    end: int
) -> Iterator[int]:
    """
    Similar to `range(start, end)` or `range(end, start)`.

    If `start` == `end` it returns `start` once
    """

    if start == end:
        return start # type: ignore

    step = 1 if start >= end else -1

    for c in range(start, end, step):
        yield c