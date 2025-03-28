from typing import Optional, TYPE_CHECKING
import threading
import pygtail

from .conduit_config import ServerRunnerConfig
from .server import Server
from .stdout_parser import StdoutParser

if TYPE_CHECKING:
    from .handler import Handler


class ServerRunner:
    """
    Reads server logs
    """

    handler: Optional["Handler"]
    config: ServerRunnerConfig
    server: Server
    stdout_parser: StdoutParser
    stop_event: threading.Event
    input_loop_thread: threading.Thread
    restart_flag: bool
    init_flag: bool


    def __init__(self, config: ServerRunnerConfig, stop_event: threading.Event, restart_flag: bool=False, handler: Optional["Handler"]=None):
        
        self.handler = handler
        self.config = config
        self.stop_event = stop_event
        self.restart_flag = restart_flag
        self.init_flag = True
        self.server = Server(self)
        self.stdout_parser = StdoutParser(self)

        self.input_loop_thread = threading.Thread(target=self.input_loop)
        self.input_loop_thread.start()

    
    def input_loop(self):
        """
        Reads Minecraft logs in loop on a thread
        """
        
        while not self.stop_event.is_set():
            
            for line in pygtail.Pygtail(f"{self.config.path}/logs/latest.log"):
                
                if not self.restart_flag and self.init_flag:
                    continue

                if line and len(line) > 0:

                    print(line)
                    events = self.stdout_parser(line)
                    self.server.event_handler(events)

            self.init_flag = False