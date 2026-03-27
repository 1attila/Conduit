from .._types import Message
from ..server import Server

from .component import BaseComponent


class Label(BaseComponent):
    """
    Displays a string
    """


    __text: Message


    def __init__(self, text: Message="") -> "Label":
        """
        Creates a label
        """

        super().__init__()

        self.__text = text
        self.__renderer.edit_data("text", text)

    
    @property
    def text(self) -> Message:
        """
        Text displayed by this label
        """

        return self.__text


    @text.setter
    def text(self, value: Message):
        
        self.__text = value
        self.__renderer.edit_data("text", value)