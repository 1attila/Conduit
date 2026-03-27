import enum


class Dimension(str, enum.Enum):
    Overworld = "overworld"
    Nether = "the_nether"
    End = "the_end"