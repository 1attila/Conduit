from typing import Optional, Dict

from ..text import Text
from ..json import Serializable, Field

from ..to_json import to_json


class Option(Serializable):
    id: Field[str]
    display: Field[Optional[Text]]
    initial: Field[bool, None, False]


    def __init__(
        self,
        id: str,
        display: Option[Text],
        initial: bool = False
    ) -> None:
        
        self.id = id
        self.display = display
        self.initial = initial

    
    def to_json(self) -> Dict:

        return {"id": self.id} + to_json({
            "display": (None, self.display),
            "initial": (False, self.initial)
        })