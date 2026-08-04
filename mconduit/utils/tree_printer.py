from typing import Dict, List

from mconduit._types import Message


def _draw_recursive(tree: Dict, messages: List[Message]) -> Message:
    
    to_return = ""

    for key, item in tree.items():
        
        if to_return == "":
            to_return = key

    return to_return


def _draw_vertical_lines(lines_pos: List[int]) -> Message:

    out = ""

    for i in range(max(lines_pos) + 1):

        if i in lines_pos:
            out += "|"
        else:
            out += " "

    return out



def draw_tree(tree: Dict) -> List[Message]:
    """
    Returns a list of messages that can be printed to draw the given tree


    Ok so this is intresting.

    Let's make some examples

    tree = {

        "hello": {
            "test": "ok,
            "nop": {"cde", "fgh"}
            "not_ok": "abc"
        },
        "world": {}
    }

    +-hello+-test+-ok
    |      |
    |      +-nop+-cde
    |      |    |
    |      |    +-fgh
    |      |
    |      +-not_ok+-abc
    |
    +-world

    start with
    """

    out_messages = []
    vertical_lines = [0]

    for key, value in tree.items():
        
        msg = "+" + key

        if type(value) is dict:
            vertical_lines.append(1 + len(key))
            msg += "+" + _draw_recursive(value, out_messages)

        out_messages.append(msg)
        out_messages.append(_draw_vertical_lines(vertical_lines))
    
    out_messages.pop()

    return out_messages