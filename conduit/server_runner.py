from subprocess import Popen, PIPE
import os
from typing import Optional, TYPE_CHECKING
import signal
import threading

from .conduit_config import ServerRunnerConfig
from .server import Server
from .stdout_parser import StdoutParser

if TYPE_CHECKING:
    from .handler import Handler


def _set_nonblocking(pipe):
    """
    Set pipe to non-blocking move

    Works differently for:
    - Linux/macOS: fcntl
    - Windows: msvcrt
    """

    if os.name == "posix": #Linux/macOS

        import fcntl

        flags = fcntl.fcntl(pipe, fcntl.F_GETFL)
        fcntl.fcntl(pipe, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
    elif os.name == "nt": # Windows
            
        import msvcrt
        from ctypes import windll, byref, c_ulong

        p_handle = msvcrt.get_osfhandle(pipe.fileno())
        mode = c_ulong(0)
        windll.kernel32.GetConsoleMode(p_handle, byref(mode))
        mode.value |= 0x0004  # Enable non-blocking mode
        windll.kernel32.SetConsoleMode(p_handle, mode)


class ServerRunner:
    """
    Server process abstraction
    
    Runs the minecraft server and handles I/O using Popen
    """

    process: Popen
    handler: Optional["Handler"]
    config: ServerRunnerConfig
    server: Server
    stdout_parser: StdoutParser
    is_running: bool = False


    def __init__(self, config: ServerRunnerConfig, handler: Optional["Handler"]=None):
        
        self.handler = handler
        self.config = config
        self.start()
        self.server = Server(self)
        self.is_running = True
        self.stdout_parser = StdoutParser(self)

        input_loop_thread = threading.Thread(target=self.input_loop)
        input_loop_thread.start()


    def start(self):
        """
        Sets the and starts the process
        """

        self.process = Popen(self.config.start_command,
                             stdin=PIPE,
                             stdout=PIPE,
                             stderr=PIPE,
                             shell=True,
                             cwd=self.config.path)

        _set_nonblocking(self.process.stdin)
        _set_nonblocking(self.process.stderr)

    
    def input_loop(self):
        """
        Reads stdout in loop on a thread
        """
        
        while True:
            line = self.process.stdout.readline().decode("utf-8", errors="replace") # It can throw errors if the server is already running
            
            if line:
                print(line)
                events = self.stdout_parser(line)
                self.server.event_handler(events)


    def _process_terminate(self):
        """
        Tries to terminate a process gracefully
        
        Works differently for:
        - Windows: CTRL_BREAK_EVENT
        - Everything else: process.terminate()
        """
        
        if os.name == "nt": # Windows
            try:
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            except:
                ...
        else:
            try:
                self.process.terminate()
            except:
                ...


    def send(self, packet: str, end: str="\n"):
        """
        Sends a packet to the server and flushes the stream.

        "end" is set to new-line by default since is needed on Windows to execute commands
        """

        self.process.stdin.write(bytes(packet + end, "utf-8"))
        self.process.stdin.flush()

    
    def stop(self):
        """
        Stops the server process
        """

        self.is_running = False
        self.send("/stop")

        self._process_terminate()

        try:
            self.process.kill()
        except:
            ...