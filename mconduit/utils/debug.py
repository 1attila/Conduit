from __future__ import annotations
from typing import Callable, List, Tuple, Any, TYPE_CHECKING
from functools import partial
from types import FrameType
import inspect
import re

from mconduit import text

if TYPE_CHECKING:
    from mconduit.plugins.plugin import Plugin


def get_var_infos(
    frame: FrameType,
    *vars: object,
) -> zip[Tuple[str, object]]:

    c = inspect.getframeinfo(frame).code_context
    
    assert c is not None

    s = c[0]
    r = re.search(r"\((.*)\)", s)
    
    assert r is not None
    g = r.group(1)

    assert isinstance(g, str)
    var_names = g.split(", ")

    return zip(var_names, vars)


def debug(
    *vars: object,
    print: Callable = print,
) -> None:
    """
    Displays the name and the value of the given variables nicely
    """

    current_frame = inspect.currentframe()
    assert current_frame is not None

    f_back = current_frame.f_back
    assert f_back is not None
    
    for var, val in get_var_infos(f_back, *vars):

        msg =  text.dark_aqua(var).bold()
        msg += text.white(" = ")
        msg += text.aqua(str(val)).underlined()

        print(msg)
    
    return None


def debug_plg(
    plg: Plugin,
    *vars: object,
) -> None:
    """
    Displays the name and the value of the given variables nicely
    """

    current_frame = inspect.currentframe()
    assert current_frame is not None

    f_back = current_frame.f_back
    assert f_back is not None

    for var, val in get_var_infos(f_back, *vars):
        
        msg =  text.dark_blue(plg.server.name).bold() + text.bold(".")
        msg += text.blue(plg.name).bold() + text.bold(".")
        msg += text.dark_aqua(var).bold()
        msg += text.white(" = ")
        msg += text.aqua(str(val)).underlined()

        plg.server.handler.cli.out(msg)

    return None

def create_plg_debug(plg: Plugin) -> partial:
    return partial(debug_plg, plg)