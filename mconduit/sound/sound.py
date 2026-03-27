from dataclasses import dataclass
from pathlib import Path


@dataclass
class Sound:
    """
    Represents a resource pack sound
    """

    file_path: Path
    stream: bool