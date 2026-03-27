from typing import Optional, Dict

from ..json import Field
from ..to_json import to_json


class MultiLine:
    max_lines: Field[Optional[int]]
    height: Field[Optional[int]]


    def __init__(
        self,
        *,
        max_lines: Optional[int]=None,
        heigth: Optional[int]=None
    ) -> "MultiLine":
        
        self.max_lines = max_lines
        self.heigth = heigth


    def to_json(self) -> Dict:

        return to_json({
            "max_lines": self.max_lines,
            "heigth": self.height
        })