from typing import List, Dict, Optional, Any, TYPE_CHECKING
import platform
import atexit
import uuid
import time

from .telemetry_storage import TelemetryStorage
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
        
        self.__handler = handler
        self.__is_conduit_loaded = False 
        self.__session_id = str(uuid.uuid4())
        self.__server_mapping: Dict[str, str] = {} # filled in self.conduit_load()
        self.__latest_event = ""
        self.__latest_error = ConduitError("place-holder", None, None, None)
        self.__storage = TelemetryStorage()
        self.__enabled = True

        atexit.register(self.at_exit)

    
    def enable(self) -> None:
        self.__enabled  = True

    
    def disable(self) -> None:
        self.__enabled = False

    
    def at_exit(self) -> None:
        
        if self.__latest_event == "conduit-unload":
            return
            
        last_error = get_last_error()
        
        if last_error is not None and last_error != self.__latest_error:
            self.exception_raised(last_error)
            
        self.conduit_unload(reload=False)


    def track_event(self, event_payload: Dict[str, Any]) -> None:
        
        if self.__enabled is False:
            return

        complete_payload = {
            "session-id": self.__session_id,
            "event": event_payload,
            "time": time.time()
        }

        self.__latest_event = event_payload["type"]
        self.__storage.store(complete_payload)

    
    def on_first_run(self) -> None:

        self.track_event(
            {
                "type": "first-run"
            }
        )
    
    
    def conduit_load(self, reload: bool = False) -> None:

        self.__server_mapping = {server.name: str(uuid.uuid4()) for server in self.__handler.servers}
        servers_data = {}

        for server in self.__handler.servers:

            servers_data[self.__server_mapping[server.name]] = {
                "loaded-plugins": [plugin.name for plugin in server.plugin_manager.plugins]
            }

        self.track_event(
            {
                "type": "conduit-load",
                "reload": reload,
                "conduit-version": self.__handler.version,
                "python-version": platform.python_version(),
                "system-type": platform.system(),
                "servers": servers_data
            }
        )

        self.__is_conduit_loaded = True


    def conduit_unload(self, reload: bool = False) -> None:

        self.track_event(
            {
                "type": "conduit-unload",
                "reload": reload
            }
        )


    def plugin_download(self, plugin_name: str) -> None:

        self.track_event(
            {
                "type": "plugin-download",
                "plugin": plugin_name
            }
        )

    
    def plugin_load(self, server: "Server", plugin_name: str) -> None:
        
        if self.__is_conduit_loaded is False:
            return
        
        self.track_event(
            {
                "type": "plugin-load",
                "server": self.__server_mapping[server.name],
                "plugin": plugin_name
            }
        )

    
    def plugin_unload(self, server: "Server", plugin_name: str) -> None:
        
        if self.__is_conduit_loaded is False:
            return
        
        self.track_event(
            {
                "type": "plugin-unload",
                "server": self.__server_mapping[server.name],
                "plugin": plugin_name
            }
        )

    
    def plugin_update(
        self,
        plugin_name: str,
        prev_version: str,
        new_version: str
    ) -> None:
        
        if self.__is_conduit_loaded is False:
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
        
        if self.__is_conduit_loaded is False:
            return

        self.track_event(
            {
                "type": "plugin-command-used",
                "server": self.__server_mapping[server.name],
                "plugin": plugin.name,
                "command": command_name
            }
        )

    
    def exception_raised(self, exception: Optional[ConduitError] = None) -> None:

        if exception is None:
            exception = get_last_error()

        if exception is None:
            return
        
        self.__latest_error = exception

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