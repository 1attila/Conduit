import enum


class HoverAction(enum.Enum):
    ShowText = "show_text"
    ShowItem = "show_item"
    ShowEntity = "show_entity"


class ClickAction(enum.Enum):
    SuggestCommand = "suggest_command"
    RunCommand = "run_command"
    OpenUrl = "open_url"
    OpenFile = "open_file" # No perms
    CopyToClipboard = "copy_to_clipboard" # 1.15+