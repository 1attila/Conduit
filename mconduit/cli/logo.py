from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.formatted_text import HTML

from mconduit.utils import hex_to_rgb, rgb_to_hex


CONDUIT_LOGO = r"""
   _____                 _       _ _  
  / ____|               | |     (_) |  
 | |     ___  _ __    __| |_   _ _| |_ 
 | |    / _ \| '_ \  / _` | | | | | __|
 | |___| (_) | | | || (_| | |_| | | |_ 
  \_____\___/|_| |_| \__,_|\__,_|_|\__|
"""


def apply_gradient_horizontal(
    text: str,
    start_hex: str,
    end_hex: str
) -> HTML:
    """
    Applies an horizontal gradient (left -> rigth) to the text.
    """

    lines = text.strip('\n').split('\n')
    start_rgb = hex_to_rgb(start_hex)
    end_rgb = hex_to_rgb(end_hex)
    
    max_width = max(len(line) for line in lines)
    
    result_lines = []
    
    for line in lines:

        line_chars = []

        for x, char in enumerate(line):

            if char == " ":
                line_chars.append(char)
                continue
            
            ratio = x / max(max_width - 1, 1)
            
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            
            color_hex = rgb_to_hex(r, g, b)
            line_chars.append(f'<style fg="{color_hex}"><b>{char}</b></style>')
        
        result_lines.append("".join(line_chars))
    
    return HTML("\n".join(result_lines))


def get_logo() -> HTML:
    """
    Returns the HTML text containing the styled Conduit logo
    """

    return apply_gradient_horizontal(CONDUIT_LOGO, "#8A2BE2", "#00FFFF")


def print_logo() -> None:
    """
    Prints Conduit logo with a color gradient
    """

    print_formatted_text(get_logo())