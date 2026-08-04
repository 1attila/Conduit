

from mconduit._types import Message
from mconduit.ui.component import BaseComponent


class Button(BaseComponent):
    

    def __init__(self, text: Message=""):
        ...

    def on_click(self):
        ...