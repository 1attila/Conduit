"""
UI components
"""

from .keyboard import Keyboard
from .component import BaseComponent
from .ui import UI
from .button import Button
from .label import Label


__all__ = [
    "Keyboard"
    "BaseComponent",
    "Dialog",
    "Button",
    "Label"
]
# I have no idea on how to implement this API lol

from mconduit import ui, Server


class MyUI(ui.UI):

    label_1: ui.Label
    button_1: ui.Button

    def __init__(self):
        
        self.label_1 = ui.Label("0")
        self.button_1 = ui.Button("Click me!")

        self.button_1.on_click(self.inc)

    
    def inc(self):
        n = int(self.label_1.text) + 1
        self.label_1.text = str(n)


def render_ui():
    Server.display_ui("XxattilaxX_00", MyUI())


del MyUI
del render_ui
del ui, Server