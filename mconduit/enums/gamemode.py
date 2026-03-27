import enum


class Gamemode(str, enum.Enum):
    Survival = "survival"
    Creative = "creative"
    Adventure = "adventure"
    Spectator = "spectator"