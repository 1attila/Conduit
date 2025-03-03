import enum


class Event(enum.Enum):
    
    PlayerJoin       = enum.auto()
    PlayerLeft       = enum.auto()
    PlayerDeath      = enum.auto()
    PlayerChat       = enum.auto()
    PlayerCommand    = enum.auto()
    PlayerShift      = enum.auto()
    PlayerRigthClick = enum.auto()
    PlayerLeftClick  = enum.auto()