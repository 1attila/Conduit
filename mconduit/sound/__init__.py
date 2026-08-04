"""
Sound utilities
"""

from mconduit.sound.sound import Sound
from mconduit.sound.ffmpeg import (
    ffmpeg,
    ffprobe,
    extract_sound_segment,
    get_duration,
    convert_to_ogg,
    InvalidSoundExtension
)
from mconduit.sound.sounds import (
    ambient,
    block,
    enchant,
    entity,
    event,
    item,
    music,
    music_disc,
    particle,
    ui,
    weather
)


__all__ = [
    "Sound",
    "ffmpeg",
    "ffprobe",
    "extract_sound_segment",
    "get_duration",
    "convert_to_ogg",
    "InvalidSoundExtension",
    "ambient",
    "block",
    "enchant",
    "entity",
    "event",
    "item",
    "music",
    "music_disc",
    "particle",
    "ui",
    "weather"
]