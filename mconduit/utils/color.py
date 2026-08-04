from typing import Tuple
import ctypes


def rgb_to_argb(r: int, g: int, b: int, a: int = 255) -> int:
    """
    Transform a RGB/RGBA color into ARGB.

    Useful for text_displays background
    """

    unsigned_mc_color = (a << 24) | (r << 16) | (g << 8) | b
    signed_mc_color = ctypes.c_int32(unsigned_mc_color).value

    return signed_mc_color


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[int, float, float]:
    """
    Transforms RGB colors into HSV
    """

    rf = r / 255.0
    gf = g / 255.0
    bf = b / 255.0

    max_ = max(rf, gf, bf)
    min_ = min(rf, gf, bf)

    delta = max_ - min_

    h = 0.0

    if delta == 0:
        h = 0.0
    elif max_ == rf:
        h = 60.0 * (((gf - bf) / delta) % 6)
    elif max_ == gf:
        h = 60.0 * ((bf - rf) / delta + 2)
    elif max_ == bf:
        h = 60.0 * ((rf - gf) / delta + 4)

    s = 0 if max_ == 0 else delta / max_
    v = max_

    return round(h), round(s * 100, 1), round(v * 100, 1)


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