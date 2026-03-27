# Idk if this should stay in /sound or /enums

# from mconduit import SoundType
# playsound("test", SoundType.Ambient)


# from mconduit import sound
# playsound("test", sound.Type.Ambient)
# playsound("test", sound.SoundType.Ambient)

import enum


class SoundType(enum.Enum):
    Ambient = "ambient"
    Block = "block"
    Hostile = "hostile"
    Master = "master"
    Music = "music"
    Neutral = "neutral"
    Player = "player"
    Record = "record"
    Voice = "voice"
    Weather = "weather"