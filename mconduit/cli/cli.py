from typing import Union, Optional, TYPE_CHECKING
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import PromptSession
import traceback
import threading
import os

from mconduit.cli.cli_suggester import ConduitCompleter
from mconduit.utils.errors import get_last_error
from mconduit.cli.logo import print_logo, apply_gradient_horizontal
from mconduit.lang.lang import Lang
from mconduit.text import Text
from mconduit.text.formatted_text import to_formatted_text
from mconduit.constants import *

if TYPE_CHECKING:
    from mconduit.handler import Handler
    from mconduit.server import Server
    from mconduit.plugin_manager import PluginManager


PREFIX = apply_gradient_horizontal("Conduit > ", "#8A2BE2", "#00FFFF")


class Cli:
    """
    Command Line Interface for Conduit
    """

    _handler: "Handler"
    _lang: "Lang"
    _running: bool
    _gui: bool
    _reload_flag: bool
    _stop_event: threading.Event
    _prompt_session: Optional[PromptSession]
    _lock: threading.Lock
    _cli_thread: Optional[threading.Thread]


    def __init__(
        self,
        stop_event: threading.Event,
        handler: "Handler",
        lang: "Lang",
        gui: bool = False,
        reload: bool = False
    ) -> None:

        self._handler = handler
        self._lang = lang
        self._running = True
        self._gui = gui
        self._reload_flag = reload
        self._stop_event = stop_event
        self._lock = threading.Lock()
        self._cli_thread = None
        self._prompt_session = None

        
    @property
    def has_gui(self) -> bool:
        return self._gui
    

    def out(
        self,
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n"
    ) -> None:
        """
        Outputs something to the console
        """
        
        with self._lock: # Using lock only here because this is the ONLY function that should be called from outside

            if len(values) == 1:

                value = values[0]

                if isinstance(value, Text):
                    print_formatted_text(to_formatted_text(value))
                    return

            if not self.has_gui:
                print(*values, sep=sep, end=end)

            else:
                raise NotImplementedError

    
    def start(self) -> None:
        """
        Starts the CLI in a background thread
        """

        if not self.has_gui:

            self._prompt_session = PromptSession(
                PREFIX,
                completer=ConduitCompleter.build(self._handler),
                complete_while_typing=True
            )

            self._cli_thread = threading.Thread(
                target=self._console_loop_thread,
                name="Conduit-CLI-Thread"
            )
            self._cli_thread.start()

    
    def _stop(self) -> None:
        """
        Stops the Cli, if any
        """

        self._running = False

        if self._prompt_session is not None:

            try:
                self._prompt_session.app.exit()
            except:
                pass


    def _console_loop_thread(self) -> None:
        """
        Reads console input in loop in background
        """

        if self._reload_flag:
            self.out("Conduit has been reloaded sucesfully!")

        else:
            print_logo()

        self.out() # Leave a blank line
        
        try:

            with patch_stdout():

                while not self._stop_event.is_set() and self._running:
                    try:
                        user_prompt = self._prompt_session.prompt() # type: ignore

                        if user_prompt:
                            self(user_prompt)

                    except EOFError:
                        break
                
        except KeyboardInterrupt:
            self._running = False
        
        self.out("Closing Conduit CLI")


    def __print_help(self) -> str:
        """Help command"""

        return """
        Conduit CLI commands:

        - <server-name> set-language <lang-path>
        - <server-name> list-plugins
        - <server-name> load-plugin <plugin-name>
        - <server-name> unload-plugin <plugin-name>
        - <server-name> download-plugin <plugin-name>
        - <server-name> update-plugin <plugin-name>

        You can read servers/handler attributes by doing:
        - <server-name/handler>.<attribute-name>

        E.g:
        - <server-name> online-players
        - <server-name> lang
        - <server-name> version
        - <server-name> motd
        - <server-name> view-distance

        Or modify them (if it's allowed) by doing:
        - <server-name/handler>.<attribute-name> = <new-value>

        E.g:
        - <server-name> motd = Conduit server

        For more infos go to https://github.com/1attila/Conduit
        """

    
    def __reload(self) -> None:
        """
        Reloads Conduit
        """

        self.out("Reloading Conduit...")
        self._running = False
        self._handler.reload()
    

    def __stop(self) -> None:
        """
        Stops Conduit
        """
        
        self._handler._stop()

    
    def __download_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Downloads a plugin
        """

        try:
            manager.download_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} has been downloaded sucesfully!")

        except Exception as e:
            traceback.print_exc()
        
    
    def __update_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Updates a plugin
        """

        try:
            manager.update_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} has been updated sucesfully!")

        except Exception as e:
            traceback.print_exc()

    
    def __load_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Loads a plugin
        """

        try:
            manager.load_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} loaded sucesfully!")

        except Exception as e:
            traceback.print_exc()
    

    def __unload_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Unloads a plugin
        """

        try:
            manager.unload_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} unloaded sucesfully!")

        except Exception as e:
            traceback.print_exc()

    
    def __reload_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Reloads a plugin
        """

        try:
            manager.reload_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} has been reloaded sucesfully!")

        except Exception as e:
            traceback.print_exc()

    
    def __list_downloaded_plugins(self) -> None:
        """
        Lists all downloaded plugins
        """
        
        plugins = ", ".join([file for file in os.listdir(PLUGINS_DIR)])

        self.out(f"[{plugins}]")
    

    def __list_plugins(self, manager: "PluginManager") -> None:
        """
        Lists all downloaded plugins
        """

        plugins = ", ".join([plugin.name for plugin in manager.plugins])

        self.out(f"[{plugins}]")

    
    def __last_error(self) -> None:
        """
        Prints the last error, if any
        """

        err = get_last_error()

        if err is not None:

            err_msg = err.name

            if err.info is not None:
                err_msg += f": {err.info}"

            elif err.docs is not None:
                err_msg += f": {err.docs}"

            if err.traceback is not None:

                err_msg += "\nTraceback:"
                err_msg += " * File: " + err.traceback["file"] + "\n"
                err_msg += " * Function: " + err.traceback["function"] + "\n"
                err_msg += " * Line: " + str(err.traceback["line"]) + "\n"
                err_msg += " * Code: " + err.traceback["code"] + "\n"

            self.out(err_msg)
        else:
            self.out("None")


    def __handle_attributes(self, command: str, obj: Union["Handler", "Server"]) -> bool:
        """
        Tries to read/edit an attribute
        """

        if "=" in command:
            attr, value = command.split("=")
            attr = attr[:-1].strip()
            value = value.strip()

            if isinstance(obj, Server) and obj.config.high_permissions is False:
                self.out(f"{obj.name} config dont allow to modify attributes")
                return True
            
            if hasattr(obj, attr):
                
                setattr(obj, attr, value)
                Set = self._lang["Set"]

                if hasattr(obj, "name"):
                    self.out(f"{Set} {obj.name}.{attr} = {value}")
                    return True
                else:
                    self.out(f"{Set} {obj.__str__()}.{attr} = {value}")
                    return True
                
        elif hasattr(obj, command) or "." in command:
            
            command = command.strip().split(".") # type: ignore
            temp_var = obj

            for cmd in command:
                if hasattr(temp_var, cmd.strip()):
                    temp_var = getattr(temp_var, cmd.strip())
                else:
                    self.out(f"Object `{temp_var}` has no attribute `{cmd.strip()}`")
                    return True
            
            self.out(str(temp_var))
            return True
        
        return False


    def __call__(self, prompt: str) -> None:
        """
        Cli commands

        syntaxt:
        <handler/server-name> <command/attribute>

        Example: smp.online_players
        """

        prompt = prompt.strip()

        if prompt == "":
            return
        
        if prompt in ("help", "?"):
            self.out(self.__print_help())
            return

        if prompt.startswith("handler"):
            command = prompt[8:].strip()
            
            handler_commands = {
                # "start-servers": self.__handler.start_servers,
                # "stop-servers": self.__handler.stop_servers,
                "last-error": self.__last_error,
                "list-plugins": self.__list_downloaded_plugins,
                "reload": self.__reload,
                "stop": self.__stop
            }
            
            if command in handler_commands:
                try:
                    handler_commands[command]()
                    return  
                
                except Exception as e:
                    self.out(e)
                    return
            
            if self.__handle_attributes(command, self._handler) is True:
                return
            
            elif command.startswith("set-language"):

                lang = command[13:]
                self._handler.set_lang(lang.strip())

                self.out(self._lang["Language is now set to"] + " " + command.strip())
                return
            
            elif command.startswith("download-plugin"):
                
                plugin = command[16:].strip()
                self.__download_plugin(plugin, self._handler.servers[0].plugin_manager)
                return

            elif command.startswith("update-plugin"):
                
                plugin = command[14:].strip()
                self.__update_plugin(plugin, self._handler.servers[0].plugin_manager)
                return

            self._handler.to_all_servers(lambda s: s.execute(command))

        else:
            for server in self._handler.servers:
                for name in server.names:

                    if prompt.startswith(name):
                        
                        command = prompt[len(name)+1:]

                        if self.__handle_attributes(command, server) is True:
                            return
                        
                        server_commands = {
                            # "start": server.start,
                            # "stop": server.stop,
                            "list-plugins": lambda: self.__list_plugins(server.plugin_manager),
                            "get-online-players": lambda: (
                                str([p for p in server.online_players]) or "[]"
                            )
                        }

                        if command in server_commands:
                            try:
                                server_commands[command]()
                                return
                            except Exception as e:
                                self.out(e)
                                return

                        elif command.startswith("execute"):
                            command = command[8:]

                            resp = server.execute(command)
                            self.out(resp)
                            return

                        elif command.startswith("set-language"):
                            command = command[13:]

                            if server.set_lang(command.strip()):
                                self.out(server.name, self._lang["Language is now set to"] + " " + command.strip())
                            
                            return
                        
                        elif command.startswith("download-plugin"):
                
                            plugin = command[16:].strip()
                            self.__download_plugin(plugin, server.plugin_manager)
                            return


                        elif command.startswith("update-plugin"):
                
                            plugin = command[14:].strip()
                            self.__update_plugin(plugin, server.plugin_manager)
                            return
                        
                        elif command.startswith("load-plugin"):
                
                            plugin = command[12:].strip()
                            self.__load_plugin(plugin, server.plugin_manager)
                            return
                        
                        elif command.startswith("unload-plugin"):
                
                            plugin = command[14:].strip()
                            self.__unload_plugin(plugin, server.plugin_manager)
                            return
                        
                        elif command.startswith("reload-plugin"):
                
                            plugin = command[14:].strip()
                            self.__reload_plugin(plugin, server.plugin_manager)
                            return

                        server.execute(command)

                        return