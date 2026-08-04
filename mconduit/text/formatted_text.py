"""
Translates Minecraft Json Text into prompt_toolkit's FormattedText
"""

from typing import List, Tuple, Union
from prompt_toolkit.formatted_text import FormattedText

from mconduit.text.text import Text
from mconduit.text.style import Style
from mconduit.enums.color import Color


ALLOWED_STYLES = {
    Style.BOLD,
    Style.ITALIC
}


COLOR_MAPPING = {
    Color.BLACK: "#000000",
    Color.DARK_BLUE: "#0000AA",
    Color.DARK_GREEN: "#00AA00",
    Color.DARK_AQUA: "#00AAAA",
    Color.DARK_RED: "#AA0000",
    Color.DARK_PURPLE: "#AA00AA",
    Color.GOLD: "#FFAA00",
    Color.GRAY: "#AAAAAA",
    Color.DARK_GRAY: "#555555",
    Color.BLUE: "#5555FF",
    Color.GREEN: "#55FF55",
    Color.AQUA: "#55FFFF",
    Color.RED: "#FF5555",
    Color.LIGHT_PURPLE: "#FF55FF",
    Color.YELLOW: "#FFFF55",
    Color.WHITE: "#FFFFFF"
}


def merge_styles(styles: List[Style]) -> str:

    translated_styles = ALLOWED_STYLES.intersection(styles)

    return " ".join([style.value for style in translated_styles])


def translate_color(color: Union[str, Color]) -> str:

    if isinstance(color, Color):
        return COLOR_MAPPING[color.value] # type: ignore
    
    return color


def translate_single_text(text: Text) -> Tuple[str, str]:
    """
    Creates the tuple that can be used inside FormattedText
    """

    color = translate_color(text.color)
    styles = merge_styles(text.styles)

    if styles != "":
        color += " " + styles

    return (
        color,
        text.text
    )


def to_formatted_text(text: Text) -> FormattedText:
    """
    Translates Minecraft Json Text into prompt_toolkit's FormattedText
    """

    text_bits = [translate_single_text(text)]

    for text_bit in text.text_bits:
        
        text_bits.append(
            translate_single_text(text_bit)
        )

    return FormattedText(text_bits)