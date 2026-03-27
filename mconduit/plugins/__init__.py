"""
Conduit Plugins APIs
"""

from .plugin import Plugin
from .plugin_command import command, Command
from .perms import Permission, perms, check_perms
from .range import Range
from .event import event
from .config import Config
from .persistent import Persistent
from .flag import Flag
from . import checks as checks


__all__ = [
    "Plugin",
    "Command", "command",
    "Permission", "perms", "check_perms",
    "checks",
    "event",
    "Config",
    "Persistent",
    "Range", "Flag"
]