import enum


class SoundType(enum.StrEnum):
    AMBIENT = "ambient"
    BLOCK   = "block"
    HOSTILE = "hostile"
    MASTER  = "master"
    MISC    = "music"
    NEUTRAL = "neutral"
    PLAYER  = "player"
    RECORD  = "record"
    VOICE   = "voice"
    WEATHER = "weather"