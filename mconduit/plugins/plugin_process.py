from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
import multiprocessing

if TYPE_CHECKING:
    from mconduit.handler import Handler


@dataclass
class PluginProcess:
    """
    Plugin thread wrapper
    """

    process: multiprocessing.Process
    start_time: datetime
    stop_time: Optional[datetime]


class ProcessHandler:
    """
    Manages all the plugin processes
    """

    __handler: "Handler"


    def __init__(self, handler: "Handler") -> "None":

        self.__handler = handler

    
    def check_processes(self) -> None:
        """
        Checks every plugin thread and stops it if needed 
        """

        now = datetime.now()

        for server in self.__handler.servers:

            for plugin in server.plugin_manager.plugins:

                for process in plugin.running_processes:

                    if (
                        process.stop_time is not None and
                        process.stop_time >= now and process.process.is_alive()
                    ):
                        process.process.terminate()

                    if not process.process.is_alive():
                        plugin.running_processes.remove(process)