from mconduit._types import Message
from mconduit.server import Server
from mconduit.text import Text

from mconduit.ui.component import BaseComponent


class Label(BaseComponent):
    """
    Displays a string
    """


    _text: Message


    def __init__(self, text: Message = "") -> None:
        """
        Creates a label
        """

        super().__init__()

        self._text = text
        self._renderer.edit_data("text", text)

    
    @property
    def text(self) -> Message:
        """
        Text displayed by this label
        """

        return self._text


    @text.setter
    def text(self, value: Message):
        
        self._text = value

        if isinstance(value, Text):
            value = Text.__str__(self._renderer._server.is_v1_21_5)
        
        self._renderer.edit_data("text", value)