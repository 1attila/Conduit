from typing import TYPE_CHECKING

from mconduit.conduit_config import HandlerConfig
from mconduit.cli.language_selector import LanguageSelector
from mconduit.cli.prefix_setter import PrefixSetter
from mconduit.cli.error_dialog import ErrorDialog
from mconduit.cli.add_server import AddServer

if TYPE_CHECKING:
    from mconduit.handler import Handler


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