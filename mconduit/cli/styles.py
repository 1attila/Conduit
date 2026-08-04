from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style


NEON_CYAN = "#00FFFF"
DEEP_BLUE = "#005FFF"
MID_BLUE = "#0088FF"
DARK_BG = "#0a0a12"
ICE_BLUE = "#D0F0FF"
ERROR_RED = "#FF3333"

# Colors to Builtin permissions
GRAY = "#AAAAAA"
YELLOW = "#FFFF55"
AQUA = "#55FFFF"
DARK_AQUA = "#00AAAA"
BLUE = "#5555FF"


welcome_style = Style.from_dict({
    "frame.border":       f"{NEON_CYAN}",
    "dialog-body":        f"bg:{DARK_BG} {ICE_BLUE}",
    "title":              f"{NEON_CYAN} bold",
    "subtitle":           f"{MID_BLUE} italic",
    "button":             f"bg:#222222 {MID_BLUE}",
    "button.focused":     f"bg:{NEON_CYAN} #000000 bold",
    "checkbox":           f"{DEEP_BLUE}"
})

select_path_style = Style.from_dict({
    "frame.border": MID_BLUE
})


def deep_blue(text: str) -> FormattedText:
    return FormattedText([(DEEP_BLUE, text)])


def bold_deep_blue(text: str) -> FormattedText:
    return FormattedText([(f"{DEEP_BLUE} bold", text)]) 


def mid_blue(text: str) -> FormattedText:
    return FormattedText([(MID_BLUE, text)])


def error_red(text: str) -> FormattedText:
    return FormattedText([(ERROR_RED, text)])