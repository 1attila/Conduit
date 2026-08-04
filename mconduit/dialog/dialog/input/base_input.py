from typing import Dict, Any
from abc import ABC

from ..json import Serializable, Field
from ..text import Text

from .input_type import InputType


class BaseInput(ABC, Serializable):
    """
    Input base class.
    
    Do not use, go for Boolean, MultiLine, NumberRange, Option, SingleOption and Text instead!
    """

    _type: Field[InputType, "type"]
    key: Field[str]
    label: Field[Text]


    def __init__(
        self,
        type: InputType,
        key: str,
        label: Text
    ) -> None:
        
        self._type = type
        self.key = key
        self.label = label

            
    def to_json(self) -> Dict[str, Any]:

        return {
            "type": self._type,
            "key": self.key,
            "label": self.label
        }