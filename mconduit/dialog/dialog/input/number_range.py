from typing import Optional

from ..json import Field
from ..text import Text

from .input_type import InputType
from .base_input import BaseInput
from ..to_json import to_json


class NumberRange(BaseInput):
    """
    
    """


    label_format: Field[str]
    width: Field[int, None, 200]
    start: Field[int]
    end: Field[int]
    step: Field[Optional[int]]
    initial: Field[Optional[int]]


    def __init__(
        self,
        key: str,
        label: Text,
        *,
        width: int = 200,
        start: int,
        end: int,
        step: Optional[int] = None,
        initial: Optional[int] = None
    ) -> None:
        
        super().__init__(
            type=InputType.NUMBER_RANGE,
            key=key,
            label=label
        )

        self.width = width
        self.start = start
        self.end = end
        self.step = step
        self.initial = initial
    

    def to_json(self):

        return super().to_json() + to_json({
            "width": (200, self.width),
            "step": (None, self.step),
            "initial": (None, self.initial)
        }) + {
            "start": self.start,
            "end": self.end
        }