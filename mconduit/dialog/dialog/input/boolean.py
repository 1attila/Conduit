from ..json import Field
from ..text import Text

from .input_type import InputType
from .base_input import BaseInput
from ..to_json import to_json


class Boolean(BaseInput):
    """
    
    """


    initial: Field[bool, None, False]
    on_true: Field[str]
    on_false: Field[str]


    def __init__(
        self,
        key: str,
        label: Text,
        *,
        initial: bool = False,
        on_true: str = "true",
        on_false: str = "false"
    ) -> None:
        
        super().__init__(
            type=InputType.BOOLEAN,
            key=key,
            label=label
        )

        self.initial = initial
        self.on_true = on_true
        self.on_false = on_false

    
    def to_json(self):

        return super().to_json() + to_json({
            "initial": (False, self.initial),
            "on_true": ("true", self.on_true),
            "on_false": ("false", self.on_false)
        })