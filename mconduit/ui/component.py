from abc import ABC
import random

from .renderer import UiRenderer

class BaseComponent(ABC):
    
    __id: str
    __renderer: UiRenderer
    __enabled: bool