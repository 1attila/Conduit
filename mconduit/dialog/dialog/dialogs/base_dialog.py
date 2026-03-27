from typing import Dict, List, Optional, Union, Any
from abc import ABC

from mconduit import Message # pyright: ignore[reportMissingImports] # TODO
from ..json import Serializable, Field

from .dialog_type import DialogType
from .body_format import BodyFormat #TODO: PlainMessage | Item
from ..after_action import AfterAction
from ..input.base_input import BaseInput
from ..to_json import to_json


class BaseDialog(ABC, Serializable):
    """
    Dialog base class.

    Do not use, go for Confirmation, DialogList, MultiAction, Notice and ServerLinks instead!
    """


    __type: Field[DialogType, "type"]
    title: Field[Message]
    external_title: Field[Optional[str], None, None]
    body: Field[Optional[List[BodyFormat]], None, None]
    inputs: Field[Optional[List[BaseInput]], None, None]
    can_close_with_escape: Field[bool, None, True]
    pause: Field[bool, None, True]
    after_action: Field[AfterAction, None, AfterAction.Close]


    def __init__(
        self,
        type: DialogType,
        title: Message,
        external_title: str | None = None,
        body: List[BodyFormat] | None = None,
        inputs: List[BaseInput] | None = None,
        can_close_with_escape: bool = True,
        pause: bool = True,
        after_action: AfterAction = AfterAction.Close
    ) -> "BaseDialog":
        
        self.__type = type
        self.title = title
        self.external_title = external_title
        self.body = body
        self.inputs = inputs
        self.can_close_with_escape = can_close_with_escape
        self.pause = pause
        self.after_action = after_action

    
    def to_dict(self) -> Dict[str, Any]:
        
        return to_json({
            "external_title": (None, self.external_title),
            "body": (None, self.body),
            "inputs": (None, self.inputs),
            "can_close_with_escape": (True, self.can_close_with_escape),
            "pause": (True, self.pause),
            "after_action": (AfterAction.NONE, self.after_action)
        }) + {
            "type": self.__type,
            "title": self.title,
        }