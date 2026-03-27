from typing import TYPE_CHECKING

from ..conduit_config import HandlerConfig
from .language_selector import LanguageSelector
from .prefix_setter import PrefixSetter
from .error_dialog import ErrorDialog
from .add_server import AddServer

if TYPE_CHECKING:
    from ..handler import Handler


class SetupWizard:
    """
    Conduit setup wizard.

    HandlerConfig:
    - Main language
    - Command prefix
    """

    def __init__(self, handler: "Handler") -> None:
        self.handler = handler

    
    def run(self) -> HandlerConfig:
        
        lang = LanguageSelector().run()
        p = PrefixSetter(lang).run()

        config = HandlerConfig()
        config.default_language = lang.lang
        config.command_prefix = p

        s = AddServer(lang).run()

        if s is None:
            
            ErrorDialog(
                "No server was added!",
                "Conduit cannot be started - you must add at least a server!"
            ).run()
            return # type: ignore

        if not isinstance(s, list):
            s = [s]

        config.servers_config = s

        return config