from typing import NoReturn, TYPE_CHECKING
import subprocess
import threading
import time
import sys

if TYPE_CHECKING:
    from .handler import Handler


class Updater:
    """
    Class responsable of checking and running updates
    """

    __handler: "Handler"
    __stop_event: threading.Event


    def __init__(self, handler: "Handler", stop_event: threading.Event) -> NoReturn:
        
        self.__handler = handler
        self.__stop_event = stop_event

        t = threading.Thread(target=self.check_for_updates, name="Updater", daemon=True)
        t.start()


    def check_for_updates(self, interval=60):
        """
        Tries to updates the package every given time
        """

        while True:

            time.sleep(interval)

            result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "conduit"], capture_output=True, text=True)

            if "Successfully installed" in result.stdout:
                self.reload()


    def reload(self) -> NoReturn:
        """
        Starts a new version of Conduit and closes the old one only when the 
        """

        subprocess.Popen([sys.executable, "-m", "conduit", "--restart"])

        self.__stop_event.set()

        self.__handler.to_all_servers(lambda s: s._join_input_thread())

        sys.exit()