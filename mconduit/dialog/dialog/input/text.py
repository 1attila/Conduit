from typing import Optional

from ..json import Field
from .. import text

from .input_type import InputType
from .base_input import BaseInput
from .multi_line import MultiLine
from ..to_json import to_json


class Text(BaseInput):
    """
    
    """


    width: Field[int, None, 200]
    label_visible: Field[bool, None, True]
    initial: Field[Optional[str], None, None]
    max_length: Field[int, None, 32]
    multi_line: Field[Optional[MultiLine], None, None]


    def __init__(
        self,
        key: str,
        label: text.Text,
        *,
        width: int=200,
        label_visible: bool=True,
        initial: Optional[str]=None,
        max_length: int=32,
        multi_line: Optional[MultiLine]=None
    ) -> "Text":
        
        super().__init__(
            type=InputType.Text,
            key=key,
            label=label
        )

        self.width = width
        self.label_visible = label_visible
        self.initial = self.initial
        self.max_length = self.max_length
        self.multi_line = self.multi_line

    
    def to_json(self):

        return super().to_json() + to_json({
            "width": self.width,
            "label_visible": self.label_visible,
            "initial": self.initial,
            "max_length": self.max_length,
            "multi_line": self.multi_line.to_json()
        })