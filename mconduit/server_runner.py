from typing import Optional, Union, Iterator, Callable, TYPE_CHECKING
from pathlib import Path
import threading
import paramiko
import pygtail
import os

from .conduit_config import ServerRunnerConfig
from .server import Server
from .stdout_parser import StdoutParser

if TYPE_CHECKING:
    from .handler import Handler


class ServerRunner:
    """
    Reads server logs locally or over SSH
    """


    handler: "Handler"
    config: ServerRunnerConfig
    server: Server
    stdout_parser: StdoutParser
    stop_event: threading.Event
    main_loop_thread: threading.Thread
    restart_flag: bool
    init_flag: bool
    _chan: paramiko.Channel
    __client: Optional[paramiko.SSHClient]
    _get_new_lines: Callable[[], Iterator[str]]


    def __init__(
        self,
        config: ServerRunnerConfig,
        stop_event: threading.Event,
        restart_flag: bool,
        handler: "Handler"
    ) -> None:
        
        self.handler = handler
        self.config = config
        self.stop_event = stop_event
        self.restart_flag = restart_flag
        self.init_flag = True
        self._get_new_lines = self._get_new_lines_local
        self.__client = None

        if self.config.machine_config is not None:

            try:
                self._connect_ssh()
                self._get_new_lines = self._get_new_lines_remote

            except Exception as e:
                
                self.__client = None
                raise e

        self.server = Server(self)
        self.stdout_parser = StdoutParser(self)
        
        self.main_loop_thread = threading.Thread(target=self.main_loop)
        self.main_loop_thread.start()

    
    def _connect_ssh(self) -> None:
        """
        Setups and connects the Paramiko SSH client
        """
        
        self.__client = paramiko.SSHClient()
        self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:

            if self.config.machine_config is None:
                raise ValueError("Maching configs should not be None")

            self.__client.connect(
                hostname=self.config.machine_config.host,
                port=self.config.machine_config.port,
                username=self.config.machine_config.username,
                password=self.config.machine_config.password,
                key_filename=self.config.machine_config.key_filename,
                allow_agent=True,
                look_for_keys=True,
                timeout=10
            )

        except Exception as e:
                
            self.__client = None
            raise e


    def _reconnect_if_needed(self) -> None:
        """
        Checks if SSH transport has dropped and restores if it happened
        """

        if not self.__client:
            self._connect_ssh()

        elif (
            not self.__client.get_transport() or
            not self.__client.get_transport().is_active() # type: ignore
        ):
            try:
                self.__client.close()
            except Exception as e:
                pass

            self._connect_ssh()

    
    def _start_remote_tail(self) -> None:

        self._reconnect_if_needed()

        if not hasattr(self, "_chan") or self._chan.closed:
            
            if self.__client is None:
                return # type: ignore

            _sdin, sdout, _sderr = self.__client.exec_command(
                f"tail -n0 -F {self.config.path / 'logs' / 'latest.log'}",
                bufsize=1,
                get_pty=True
            )

            self._chan = sdout.channel
        

    def _get_new_lines_remote(self) -> Iterator[str]:
        
        if self.__client is None:
            return # type: ignore

        self._start_remote_tail()

        while not self.stop_event.is_set():
        
            if self._chan.recv_ready():
                
                data = self._chan.recv(4096).decode("utf-8", errors="ignore")

                for line in data.splitlines():
                    yield line.strip()
            else:
                threading.Event().wait(0.1)
                return
                

    def _is_valid_pygtail_offset(self, content: bytes) -> bool:

        if b"\x00" in content:
            return False

        lines = content.splitlines()

        if len(lines) != 2:
            return False

        return all(line.isdigit() for line in lines)


    def _safe_pygtail(self, log_path: Path) -> Iterator[str]:
        
        offset_path = log_path.with_name(log_path.name + ".offset")

        if offset_path.exists():

            try:
                with offset_path.open("rb") as f:
                    content = f.read().strip()
                
                if not self._is_valid_pygtail_offset(content):
                    raise ValueError

            except:
                offset_path.unlink(missing_ok=True)
                
        return pygtail.Pygtail(
            str(log_path),
            read_from_end=True
        )
    
    
    def _get_new_lines_local(self) -> Iterator[str]:
        
        try:
            for line in self._safe_pygtail(self.config.path / "logs" / "latest.log"):
                yield line
        except Exception as e:
            pass

    
    def main_loop(self) -> None:
        """
        Reads Minecraft logs in loop on a thread
        """
        
        while not self.stop_event.is_set():
            
            for line in self._get_new_lines():
                
                if not self.restart_flag and self.init_flag:
                    continue

                if line and len(line) > 0:
                    
                    self.server.plugin_manager._handle_plugins_raises()
                    events = self.stdout_parser(line)
                    self.server.event_handler(events)
                    self.server.event_handler.dispatch_log_events(line)

            self.server.event_handler.fetch_other_events()
            self.init_flag = False

        self.stop()


    def _read_file(self, relative_path: str) -> Optional[str]:
        """
        Fetches content from the given file on this server machine
        """

        path = str(self.config.path / relative_path)

        if self.__client:
            
            sftp = self.__client.open_sftp()
            
            try:
                with sftp.open(path, "r") as f:
                    return f.read().decode("utf-8")
                
            except Exception as e:
                return # type: ignore

            finally:
                sftp.close()

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    
    def _write_file(self, relative_path: str, content: Union[str, bytes]) -> None:
        """
        Writes the given file with the specified content on this server machine
        """

        path = str(self.config.path / relative_path)

        if self.__client:
            
            sftp = self.__client.open_sftp()

            try:
                with sftp.open(path, "w") as f:

                    if isinstance(content, bytes):
                        f.write(content.decode("utf-8"))
                    else:
                        f.write(content)
            
            finally:
                sftp.close()
        
        else:
            with open(path, "w") as f:
                f.write(content)


    def stop(self) -> None:
        """
        Stop the loop and clean up resources
        """

        self.stop_event.set()

        if (
            self.main_loop_thread.is_alive() and
            threading.current_thread() is not self.main_loop_thread
        ):
            self.main_loop_thread.join(timeout=5)

        if self.__client is not None:

            try:
                self.__client.close()

            except Exception as e:
                pass

            self.__client = None