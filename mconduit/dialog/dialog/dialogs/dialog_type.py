import enum


class DialogType(str, enum.Enum):
    Notice       = "notice"
    Confirmation = "confirmation"
    MultiAction  = "multi_action",
    ServerLinks  = "server_links"
    DialogList   = "dialog_list"