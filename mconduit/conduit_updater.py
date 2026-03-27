from typing import TYPE_CHECKING
import subprocess
import sys

if TYPE_CHECKING:
    from .handler import Handler


class ConduitUpdater:
    """
    Class responsable for the mconduit package update
    """


    __handler: "Handler"


    def __init__(self, handler: "Handler") -> None:
        
        self.__handler = handler


    def check_for_updates(self):
        """
        Tries to updates the conduit package
        """

        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "mconduit"], capture_output=True, text=True)

        if "Successfully installed" in result.stdout:
            self.__handler._reload()