from typing import TYPE_CHECKING
import subprocess
import sys

if TYPE_CHECKING:
    from mconduit.handler import Handler


class ConduitUpdater:
    """
    Class responsable for the mconduit package update
    """


    _handler: "Handler"


    def __init__(self, handler: "Handler") -> None:
        
        self._handler = handler


    def check_for_updates(self):
        """
        Tries to updates the conduit package
        """

        result = subprocess.run(
            [sys.executable,
             "-m", "pip", "install", "--upgrade", "mconduit"
            ],
            capture_output=True, text=True
        )

        if "Successfully installed" in result.stdout:
            self._handler._reload()