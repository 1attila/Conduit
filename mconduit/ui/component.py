from abc import ABC
import random

from mconduit.ui.renderer import UiRenderer


class BaseComponent(ABC):
    
    _id: str
    _renderer: UiRenderer
    _enabled: bool