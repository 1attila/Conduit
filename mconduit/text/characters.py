from typing import TYPE_CHECKING
from .style import Style
from .text import Text

if TYPE_CHECKING:
    from .._types import Message

# Bold: 84 -> 98
"""
Bold: {
    126: 
    112: 126
    98: 112, # 1.14
    84: 98, # 1.66
    72: 84, # 1.66
    63: 72, # 1.14
    42: 56, # 1.33
    28: 42,  # 1.50
    21: 
    14: 
}
"""
MINECRAFT_FONT_WIDTHS = {
    " ":63, "A":84, "B":84, "C":84, "D":84, "E":84, "F":84,
    "G":84, "H":84, "I":56, "J":84, "K":84, "L":84, "M":84,
    "N":84, "O":84, "P":84, "Q":84, "R":84, "S":84, "T":84,
    "U":84, "V":84, "W":84, "X":84, "Y":84, "Z":84,
    "a":84, "b":84, "c":84, "d":84, "e":84, "f":70, "g":84,
    "h":84, "i":28, "j":84, "k": 72, "l":42, "m":84, "n":84,
    "o":84, "p":84, "q":84, "r":84, "s":84, "t":63, "u":84,
    "v":84, "w":84, "x":84, "y":84, "z":84,
    "0":84, "1":84, "2":84, "3":84, "4":84, "5":84,
    "6":84, "7":84, "8":84, "9":84,

    ".":28, ",":28, ":":28, ";":28, "!":28, "?":84, "'":28,
    '"':56, "/":84, "\\":24, "|":28, "-":84, "_":84, "+":84,
    "=":84, "*": 63, "&":84, "%":84, "#":84, "@":98, "^":84,
    "~": 98, "`":14, "(":56, ")":56, "[":56, "]":56, "{":56,
    "}":56, "<": 72, ">": 72, "\u2003": 70,
    "•": 42, "▶": 98, "✔": 98, "❌": 98, "…": 112,
    "⋮": 28, "ℹ": 140, "⚠": 140, "🔔": 112, "📨": 112,
    "☰": 84, "★": 112, "☆": 112, "📌": 84, "🔧": 98,
    "🗑": 84, "📁": 72, "♻": 126
}
# TODO: add "`"
WIDTHS = [14, 21, 28, 42, 56, 63, 72, 84, 98, 112, 126, 140]


def pixel_len(text: "Message") -> int:
    """
    Returns the lenght of the message in pixels
    """

    if isinstance(text, Text):

        l = 0

        for t in [Text(text.text, text.color, *text.styles), *text.text_bits]:
            
            if Style.Bold in t.styles:

                normal_lens = [MINECRAFT_FONT_WIDTHS.get(item, 84) for item in t]
                lens_ids = [WIDTHS.index(item) for item in normal_lens]
                l += sum([WIDTHS[item + 1] for item in lens_ids])
            else:
                l += pixel_len(t.plain_text)

        return l

    return sum([MINECRAFT_FONT_WIDTHS.get(item, 84) for item in text])