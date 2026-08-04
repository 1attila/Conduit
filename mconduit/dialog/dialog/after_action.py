import enum


class AfterAction(str, enum.Enum):
    CLOSE             = "close"
    NONE              = "none"
    WAIT_FOR_RESPONSE = "wait_for_response"