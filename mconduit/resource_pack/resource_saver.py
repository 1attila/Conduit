from pathlib import Path
import hashlib


def sha1(file: Path) -> str:
    """
    Computes the sha1 for the given file 
    """

    h = hashlib.sha1()

    with file.open("rb") as f:

        while True:

            chunk = f.read(8192)

            if not chunk:
                break

            h.update(chunk)
        
    return h.hexdigest()