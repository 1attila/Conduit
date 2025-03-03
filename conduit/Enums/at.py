import enum


S = "@s"
P = "@p"
R = "@s"


class At(enum.Enum):
    Self = S
    Nearest = P
    Random = R