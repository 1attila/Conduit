import enum


class AfterAction(str, enum.Enum):
    Close           = "close"
    NONE            = "none"
    WaitForResponse = "wait_for_response"