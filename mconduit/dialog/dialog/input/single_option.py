from typing import List

from ..json import Field
from ..text import Text

from .input_type import InputType
from .base_input import BaseInput
from .option import Option
from ..to_json import to_json


class SingleOption(BaseInput):
    """
    
    """


    label_visible: Field[bool, None, True]
    width: Field[int, None, 200]
    options: List[Option]


    def __init__(
        self,
        key: str,
        label: Text,
        *,
        label_visible: bool = True,
        width: int = 200,
        options: List[Option]
    ) -> None:
        
        super().__init__(
            type=InputType.SINGLE_OPTION,
            key=key,
            label=label
        )

        self.label_visible = label_visible
        self.width = width
        self.options = options


    def to_json(self):
        return super().to_json() + to_json({
            "label_visible": (True, self.label_visible),
            "width": (200, self.width)
        }) + {"options": self.options}