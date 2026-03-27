"""
Dialog interface for Conduit plugins
"""

from .dialogs.notice import Notice
from .dialogs.confirmation import Confirmation
from .dialogs.multi_action import MultiAction
from .dialogs.server_links import ServerLinks
from .dialogs.dialog_list import DialogList

from .input.text import Text
from .input.boolean import Boolean
from .input.single_option import SingleOption
from .input.number_range import NumberRange

from .after_action import AfterAction


__all__ = [
    "Notice",
    "Confirmation",
    "MultiAction",
    "ServerLinks",
    "DialogList",

    "Text",
    "Boolean",
    "SingleOption",
    "NumberRange",

    "AfterAction"
]