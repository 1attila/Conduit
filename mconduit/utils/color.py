from typing import Tuple
import ctypes


def rgb_to_argb(r: int, g: int, b: int, a: int = 255) -> int:
    """
    Transform a RGB/RGBA color into ARGB.

    Usef for text_displays background
    """
    
    if r == 0 and g == 0 and b == 0:
        return 0

    unsigned_mc_color = (a << 24) | (r << 16) | (g << 8) | b
    signed_mc_color = ctypes.c_int32(unsigned_mc_color).value

    return signed_mc_color


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """
    Transforms RGB colors into HSV
    """

    r /= 255 # type: ignore
    g /= 255 # type: ignore
    b /= 255 # type: ignore

    max_ = max(r, g, b)
    min_ = min(r, g, b)

    delta = max_ - min_

    h = 0

    if max_ == r:
        h = 60 * (((g - b) / delta) % 6)
    elif max_ == g:
        h = 60 * ((b - r) / delta + 2)
    elif max_ == b:
        h = 60 * ((r - g) / delta + 4)

    s = 0 if max_ == 0 else delta / max_
    v = max_

    return h, s, v


def hex_to_rgb(color: str) -> Tuple[int, int, int]:
    """
    Transforms the given color from hex to RGB format
    """

    color = color.lstrip("#")

    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)

    return r, g, b


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Transforms the given color from RGB to hex format 
    """

    return f"#{r:02x}{g:02x}{b:02x}"