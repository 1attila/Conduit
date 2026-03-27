from typing import Iterable, Optional, NoReturn, List, Any, TYPE_CHECKING
from prompt_toolkit.completion import NestedCompleter, WordCompleter, Completion, CompleteEvent
from prompt_toolkit.document import Document

from ..constants import PLUGINS_DIR
from pathlib import Path
import os

if TYPE_CHECKING:
    from ..handler import Handler
    from ..server import Server


handler_commands = {
    "reload",
    "download-plugin",
    "update-plugin",
    "list-plugins",
    "set-language"
}

plugins_commands = {
    "download-plugin",
    "load-plugin",
    "unload-plugin",
    "reload-plugin",
    "list-plugins",
    "update-plugin"
}

handler_attributes = {
    "lang",
    "servers",
    "command_prefix",
    "cli",
    "async_tasks",
    "plugin_catalogue"
    "_updater"
}

server_commands = {
    "get-online-players",
    "set-language",
    "execute"
}

server_editable_attributes = { # from `server.properties`
    "motd",
    "view_distance",
    "simulation_distance",
    "gamemode",
    "difficulty"
}

server_attributes = {
    # fetched from `server.properties`
    "whitelist",
    "op",
    "banned_ips",
    "banned_players",

    # Server class fields
    "name",
    "names",
    "path",
    "handler",
    "config",
    "event_handler",
    "plugin_manager",
    "permissions",
    "lang",
    "is_running",
    "seed",
    "__slots",
    "__runner",
    "__rcon"
}


class ConduitCompleter(NestedCompleter):
    """
    Command completer for Conduit CLI.

    Some suggestions that may change are fetched when needed at runtime
    """


    handler: "Handler"


    @classmethod
    def build(cls, handler: "Handler") -> "ConduitCompleter":
        
        cls.handler = handler

        cli_commands = {
            "help": None,
            "?": None,
            "handler": handler_commands | handler_attributes
        }

        server_cli = plugins_commands | server_commands | server_attributes | server_editable_attributes | plugins_commands

        for server in handler.servers:
            for name in server.names:
                cli_commands[name] = server_cli

        super().from_nested_dict(cli_commands)

        return cls

    
    def get_servers_names(self) -> List[str]:
        """
        Return a list with all the possibles server names
        """

        names = []

        for server in self.handler.servers:
            names.extend(server.names)

        return names


    def get_server_named(self, name: str) -> Optional["Server"]:
        """
        Returns the server that has the given name/aliases
        """

        for server in self.handler.servers:
            if name in server.names:
                return server
            
    
    def set_to_server(self, server: "Server", *path, value: Any) -> NoReturn:
        """
        Sets to all the options with the server aliases the same values.

        set_to_server("smp", ["motd", "="], "A Minecraft server") means:

        self.options["smp"]["motd"]["="] = "A Minecraft server"

        for all the server names
        """

        new_completer = NestedCompleter.from_nested_dict(dict.fromkeys(value))
        
        for name in server.names:

            base = self.options[name]

            for idx in path[:-1]:
                base = base.options[idx]
            
            if type(base) is str:
                base[path[-1]] = new_completer
            else:
                base.options[path[-1]] = new_completer

    
    def _download_plugin(self, server: Optional["Server"]=None) -> NoReturn:
        
        downloaded_plugins = os.listdir(PLUGINS_DIR)
        plugins_to_download = []

        for plugin in self.handler.plugin_catalogue.latest_plugin_versions.keys():
            
            if plugin not in downloaded_plugins:
                plugins_to_download.append(plugin)

        c = NestedCompleter.from_nested_dict(dict.fromkeys(plugins_to_download))

        self.options["handler"].options["download-plugin"] = c

        if server is not None:
            self.set_to_server(server, "download-plugin", value=plugins_to_download)


    def _update_plugin(self, server: Optional["Server"]=None) -> NoReturn:
        
        c = NestedCompleter.from_nested_dict(dict.fromkeys(self.handler.plugin_catalogue.skipped_updates))

        self.options["handler"].options["download-plugin"] = c

        if server is not None:
            self.set_to_server(server, "download-plugin", value=self.handler.plugin_catalogue.skipped_updates)

    def _set_lang(self) -> NoReturn:
        
        langs = [item.replace(".yml", "") for item in os.listdir(Path(os.getcwd(), "resources")) if item.endswith(".yml")]
        c = NestedCompleter.from_nested_dict(dict.fromkeys(langs))

        self.options["handler"].options["set-language"] = c

    
    def _load_plugin(self, server: "Server") -> NoReturn:

        loaded_plugins = [plugin.name for plugin in server.plugin_manager.plugins]
        unloaded_plugins = []

        for plugin_name in os.listdir(PLUGINS_DIR):
            if plugin_name not in loaded_plugins:
                unloaded_plugins.append(plugin_name)

        self.set_to_server(server, "load-plugin", value=unloaded_plugins)

    
    def _edit_properties(self, server: "Server") -> NoReturn:

        if server.config.high_permissions is True:
            for property in server_editable_attributes:
                self.set_to_server(server, property, value="=")


    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        
        text = document.text_before_cursor.strip()
        stripped_len = len(document.text_before_cursor) - len(text)
        words = [w for part in text.split(" ") for w in part.split(".")]
        first_term = words[0]

        if not words:

            completer = WordCompleter(list(self.options.keys()), ignore_case=self.ignore_case)

            yield from completer.get_completions(document, complete_event)
            return

        if len(words) == 2:
            
            second_term = words[1]

            if first_term == "handler":

                match second_term:
                    case "download-plugin":
                        self._download_plugin()

                    case "update-plugin":
                        self._update_plugin()

                    case "set-language":
                        self._set_lang()

            elif first_term in self.get_servers_names():
                
                server = self.get_server_named(first_term)
                
                match second_term:

                    case "set-language":
                        self._set_lang()

                    case "download-plugin":
                        self._download_plugin(server)

                    case "update-plugin":
                        self._update_plugin(server)

                    case "load-plugin":
                        self._load_plugin(server)

                    case "unload-plugin":
                    
                        self.set_to_server(server, "unload-plugin",
                                        value={plugin.name for plugin in server.plugin_manager.plugins}
                        )
                    
                    case "reload-plugin":

                        self.set_to_server(server, "reload-plugin",
                                           value={plugin.name for plugin in server.plugin_manager.plugins}
                        )
                    
                if second_term in server_editable_attributes:
                    self._edit_properties(server)

        completer = self.options.get(first_term)

        if completer is not None:
            
            remaining_text = text[len(first_term):].lstrip()
            move_cursor = len(text) - len(remaining_text) + stripped_len

            new_document = Document(
                remaining_text,
                cursor_position=document.cursor_position - move_cursor,
            )

            yield from completer.get_completions(new_document, complete_event)

        else:
            completer = WordCompleter(list(self.options.keys()), ignore_case=self.ignore_case)

            yield from completer.get_completions(document, complete_event)