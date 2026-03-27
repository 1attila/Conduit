

from .._types import Message
from .component import BaseComponent


class Button(BaseComponent):
    

    def __init__(self, text: Message=""):
        ...

    def on_click(self):
        ...