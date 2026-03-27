from typing import Optional, Tuple

import parse


def parse_version(version: str) -> Optional[Tuple[int, int, int]]:
    """
    Splits a version string into a tuple.

    E.g: '1.2.3' -> (1, 2, 3)
    """

    parsed = parse.parse(r"{MAJOR}.{MINOR}.{PATCH}", version)

    if parsed:
        return parsed["MAJOR"], parsed["MINOR"], parsed["PATCH"]

    
def is_new_version(v1: str, v2: str) -> bool:
    """
    Returns True if v2 is newer than v1, False otherwise
    """

    v1 = parse_version(v1) # type: ignore
    v2 = parse_version(v2) # type: ignore

    if v1 is None or v2 is None:
        return False

    for i in range(3):

        if v2[i] > v1[i]:
            return True
        elif v2[i] != v1[i]:
            return False

    return False