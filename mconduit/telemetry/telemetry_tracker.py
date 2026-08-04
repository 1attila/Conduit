from typing import List, Dict, Optional, Any, TYPE_CHECKING
import platform
import atexit
import uuid
import time

from .reporter import TelemetryReporter
from ..utils.errors import ConduitError, get_last_error

if TYPE_CHECKING:
    from ..handler import Handler
    from ..server import Server
    from ..plugins import Plugin


class TelemetryTracker:
    """
    Class responsable to register telemetry events
    """
    

    def __init__(
        self,
        handler: "Handler",
    ) -> None:
        
        self._handler = handler
        self._is_conduit_loaded = False 
        self._session_id = str(uuid.uuid4())
        self._server_mapping: Dict[str, str] = {} # filled in self.conduit_load()
        self._latest_event = ""
        self._latest_error = ConduitError("place-holder", None, None, None)
        self._reporter = TelemetryReporter("http://5.95.179.197/report")
        self._enabled = True

        atexit.register(self.at_exit)

    
    def enable(self) -> None:
        self._enabled  = True

    
    def disable(self) -> None:
        self._enabled = False

    
    def at_exit(self) -> None:
        
        if self._latest_event == "conduit-unload":

            self._reporter.stop()

            if self._reporter.is_alive():
                self._reporter.join(timeout=3)

            return
            
        last_error = get_last_error()
        
        if last_error is not None and last_error != self._latest_error:
            self.exception_raised(last_error)
            
        self.conduit_unload(reload=False)

        self._reporter.stop()

        if self._reporter.is_alive():
            self._reporter.join(timeout=3)


    def track_event(self, event_payload: Dict[str, Any]) -> None:
        
        if self._enabled is False:
            return

        complete_payload = {
            "session-id": self._session_id,
            "event": event_payload,
            "time": time.time()
        }

        self._latest_event = event_payload["type"]
        self._reporter.append_event(complete_payload)

    
    def on_first_run(self) -> None:

        self.track_event(
            {
                "type": "first-run",
                "conduit-version": self._handler.version,
                "python-version": platform.python_version(),
                "system-type": platform.system(),
                "arch": platform.architecture()
            }
        )
    
    
    def conduit_load(self, reload: bool = False) -> None:

        self._server_mapping = {server.name: str(uuid.uuid4()) for server in self._handler.servers}
        servers_data = {}

        for server in self._handler.servers:
            
            version = server.version

            if version is not None:
                version = str(version) # type: ignore

            servers_data[self._server_mapping[server.name]] = {
                "loaded-plugins": [plugin.name for plugin in server.plugin_manager.plugins],
                "version": version
            }

        self.track_event(
            {
                "type": "conduit-load",
                "reload": reload,
                "conduit-version": self._handler.version,
                "python-version": platform.python_version(),
                "system-type": platform.system(),
                "arch": platform.architecture(),
                "servers": servers_data
            }
        )

        self._is_conduit_loaded = True


    def conduit_unload(self, reload: bool = False) -> None:

        self.track_event(
            {
                "type": "conduit-unload",
                "reload": reload
            }
        )


    def plugin_download(self, plugin_name: str, forced: bool = False) -> None:

        self.track_event(
            {
                "type": "plugin-download",
                "plugin": plugin_name,
                "forced": forced
            }
        )

    
    def plugin_load(self, server: "Server", plugin_name: str) -> None:
        
        if self._is_conduit_loaded is False:
            return
        
        self.track_event(
            {
                "type": "plugin-load",
                "server": self._server_mapping[server.name],
                "plugin": plugin_name
            }
        )

    
    def plugin_unload(self, server: "Server", plugin_name: str) -> None:
        
        if self._is_conduit_loaded is False:
            return
        
        self.track_event(
            {
                "type": "plugin-unload",
                "server": self._server_mapping[server.name],
                "plugin": plugin_name
            }
        )

    
    def plugin_update(
        self,
        plugin_name: str,
        prev_version: str,
        new_version: str
    ) -> None:
        
        if self._is_conduit_loaded is False:
            return
        
        self.track_event(
            {   
                "type": "plugin-update",
                "plugin": plugin_name,
                "prev-version": prev_version,
                "new-version": new_version
            }
        )

    
    def command_invoked(
        self,
        server: "Server",
        plugin: "Plugin",
        command_name: str
    ) -> None:
        
        if self._is_conduit_loaded is False:
            return

        self.track_event(
            {
                "type": "plugin-command-used",
                "server": self._server_mapping[server.name],
                "plugin": plugin.name,
                "command": command_name
            }
        )

    
    def exception_raised(self, exception: Optional[ConduitError] = None) -> None:

        if exception is None:
            exception = get_last_error()

        if exception is None:
            return
        
        self._latest_error = exception

        self.track_event(
            {
                "type": "exception-raised",
                "name": exception.name,
                "info": exception.info,
                "doc": exception.docs,
                "traceback": exception.traceback
            }
        )

    
    def help_invoked(self, args: List[str] | None) -> None:

        if args is None:
            args = []

        self.track_event(
            {
                "type": "help-invoked",
                "args": args
            }
        )