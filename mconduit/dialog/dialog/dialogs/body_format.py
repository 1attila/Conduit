

from ..json import Serializable, Field
from ..text import Text


class BodyFormat(Serializable):

    __type: Field[str, "type"]


    def __init__(
        self,
        type: str
    ) -> "BodyFormat":
        self.__type = type


class PlainMessage(BodyFormat):
    """

    """


    contents: Text
    width: Field[int, None, 200]
    

    def __init__(
        self,
        contents: Text,
        width: int = 200
    ) -> "PlainMessage":

        super().__init__("minecraft:plain_message")
        self.contents = contents
        self.width = width


class Item(BodyFormat):
    ...