import enum


S = "@s"
P = "@p"
E = "@e"
R = "@s"


class At(enum.Enum):
    Self = S
    Nearest = P
    AllEntities = E
    Random = R