import enum


S = "@s"
P = "@p"
R = "@s"


class At(enum):
    Self = S
    Nearest = P
    Random = R