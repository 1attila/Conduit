import enum


class InputType(str, enum.Enum):
    TEXT          = "text"
    BOOLEAN       = "boolean"
    SINGLE_OPTION = "single_option"
    NUMBER_RANGE  = "number_range"