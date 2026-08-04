from typing import Optional, TYPE_CHECKING
import parse

if TYPE_CHECKING:
    from mconduit.server import Server


def get_gamerule_value(server: "Server", gamerule: str) -> Optional[bool]:
    """
    Returns if a given gamerule is set to True or False
    """

    out = server.execute(f"/gamerule {gamerule}")

    if parsed := parse.parse(r"Gamerule {gamerule} is currently set to: {value}", out):

        value = parsed["value"]

        return True if value == "true" else False

    return None