from pathlib import Path
import subprocess
import logging
import shutil


FFMPEG_ERROR = "ffmpeg not found.\n"
"Please install ffmpeg and ensure it is available on PATH.\n"
"See https://ffmpeg.org/download.html"

FFPROBE_ERROR = "ffprobe not found.\n"
"Please install ffmpeg and ensure it is available on PATH.\n"
"See https://ffmpeg.org/download.html"

logger = logging.getLogger("mconduit-sound")

ffmpeg = shutil.which("ffmpeg") or shutil.which("avconv")
ffprobe = shutil.which("ffprobe")

if ffmpeg is None:

    logger.warning(FFMPEG_ERROR)

if ffprobe is None:

    logger.warning(FFPROBE_ERROR)


class InvalidSoundExtension(Exception):
    ...


def ffmpeg_check() -> None:
    
    if ffmpeg is None:
        raise RuntimeError(FFMPEG_ERROR)
    

def ffprobe_check() -> None:
    
    if ffprobe is None:
        raise RuntimeError(FFPROBE_ERROR)


def extract_sound_segment(
    sound_path: Path,
    output_path: Path,
    start: float,
    stop: float
) -> Path:
    
    ffmpeg_check()

    if not sound_path.exists():
        raise FileNotFoundError(sound_path)

    if start < 0:
        raise ValueError("start must be >= 0")

    if stop <= start:
        raise ValueError("stop must be > start")

    if output_path.suffix != ".ogg":
        raise InvalidSoundExtension("output_path must end with .ogg")

    duration = get_duration(sound_path)

    if start >= duration:
        raise ValueError("start is beyond audio duration")

    stop = min(stop, duration)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-ss", str(start),
        "-i", str(sound_path),
        "-vn",
        "-t", str(stop - start),
        "-c", "copy",
        str(output_path)
    ]

    subprocess.check_call(cmd) # type: ignore

    return output_path


def get_duration(sound_path: Path) -> float:
    """
    Returns the duration of sound at the given path
    """

    ffprobe_check()

    if not sound_path.exists():
        raise FileNotFoundError(sound_path)

    probe_cmd = [
        ffprobe,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(sound_path),
    ]
    
    return float(subprocess.check_output(probe_cmd).decode().strip()) # type: ignore


def convert_to_ogg(input_path: Path, output_path: Path) -> None:
    """
    Converts a specific file at the given path to .ogg and copies it to the given path
    """

    ffmpeg_check()
    
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    
    if not output_path.name.endswith(".ogg"):
        raise InvalidSoundExtension("output_path must end with .ogg")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        ffmpeg,
        "-y",
        "-nostdin",
        "-hide_banner",
        "-loglevel", "info",
        "-i", str(input_path),
        "-vn",
        "-map_metadata", "-1",
        "-c:a", "libvorbis",
        "-q:a", "2",
        str(output_path),
    ]

    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL) # type: ignore