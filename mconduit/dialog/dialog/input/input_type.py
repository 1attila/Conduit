import enum


class InputType(str, enum.Enum):
    Text         = "text"
    Boolean      = "boolean"
    SingleOption = "single_option"
    NumberRange  = "number_range"