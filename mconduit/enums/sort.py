import enum


class Sort(str, enum.Enum):
    Arbitrary = "arbitrary"
    Furthest  = "furthest"
    Nearest   = "nearest"
    Random    = "random"