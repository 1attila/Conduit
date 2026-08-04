import enum


class Gamemode(enum.StrEnum):
    SURVIVAL  = "survival"
    CREATIVE  = "creative"
    ADVENTURE = "adventure"
    SPECTATOR = "spectator"