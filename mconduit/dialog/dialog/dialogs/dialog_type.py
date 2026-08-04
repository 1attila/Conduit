import enum


class DialogType(str, enum.Enum):
    NOTICE        = "notice"
    CONFIRMATION  = "confirmation"
    MULTI_ACTION  = "multi_action",
    SERVRER_LINKS = "server_links"
    DIALOG_LIST   = "dialog_list"