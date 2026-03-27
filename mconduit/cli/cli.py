from typing import Union, Optional, TYPE_CHECKING
from prompt_toolkit import PromptSession
import threading
import os

from .cli_suggester import ConduitCompleter
from ..utils.errors import get_last_error
from .logo import print_logo
from ..lang.lang import Lang
from ..constants import *

if TYPE_CHECKING:
    from ..handler import Handler
    from ..server import Server
    from ..plugin_manager import PluginManager


class Cli:
    """
    Command Line Interface for Conduit
    """

    __handler: "Handler"
    __lang: "Lang"
    __running: bool
    __gui: bool
    __reload_flag: bool
    __stop_event: threading.Event
    __prompt_session: Optional[PromptSession]


    def __init__(
        self,
        stop_event: threading.Event,
        handler: "Handler",
        lang: "Lang",
        gui: bool=False,
        reload: bool=False
    ) -> None:

        self.__handler = handler
        self.__lang = lang
        self.__running = True
        self.__gui = gui
        self.__reload_flag = reload
        self.__stop_event = stop_event

        if self.__gui:
            ...

        else:
            self.__prompt_session = PromptSession("> ", completer=ConduitCompleter.build(self.__handler))

        
    @property
    def has_gui(self) -> bool:
        return self.__gui
    

    def out(self, *values: object, sep: Optional[str]=" ", end: Optional[str]="\n") -> None:
        """
        Outputs something to the console
        """
        
        with threading.Lock(): # Using lock only here because this is the ONLY function that should be called from outside

            if not self.has_gui:
                print(*values, sep, end)

            else:
                raise NotImplementedError

    
    def _stop(self) -> None:
        """
        Stops the Cli, if any
        """

        self.__running = False

        if self.__prompt_session is not None:

            try:
                self.__prompt_session.app.exit()
            except:
                pass


    def _console_loop_thread(self) -> None:
        """
        Reads console input in loop on the main thread
        """

        if self.__reload_flag:
            self.out("Conduit has been reloaded sucesfully!")

        else:
            print_logo()
        
        try:
            while not self.__stop_event.is_set() and self.__running:
                try:
                    user_prompt = self.__prompt_session.prompt("> ", completer=ConduitCompleter.build(self.__handler)) # type: ignore

                    if user_prompt:
                        self(user_prompt)

                except EOFError:
                    break
                
        except KeyboardInterrupt:
            self.__running = False
        
        self.out("Closing Conduit CLI")


    def __print_help(self) -> str:
        """Help command"""

        return """
        Conduit CLI commands:

        - <server-name>.get-online-players
        - <server-name>.set-language <lang-path>

        You can read servers/handler attributes by doing:
        - <server-name/handler>.<attribute-name>
        Or modify it (if it's allowed) by doing:
        - <server-name/handler>.<attribute-name> = <new-value>
        For more infos go to https://github.com/1attila/Conduit
        """

    
    def __reload(self) -> None:
        """
        Reloads Conduit
        """

        self.out("Reloading Conduit...")
        self.__running = False
        self.__handler.reload()
    

    def __stop(self) -> None:
        """
        Stops Conduit
        """
        
        self.__handler._stop()

    
    def __download_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Downloads a plugin
        """

        try:
            manager.download_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} has been downloaded sucesfully!")

        except Exception as e:
            self.out(str(type(e).__name__))
        
    
    def __update_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Updates a plugin
        """

        try:
            manager.update_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} has been updated sucesfully!")

        except Exception as e:
            self.out(str(type(e).__name__)) 

    
    def __load_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Loads a plugin
        """

        try:
            manager.load_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} loaded sucesfully!")

        except Exception as e:
            self.out(str(type(e).__name__))
    

    def __unload_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Unloads a plugin
        """

        try:
            manager.unload_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} unloaded sucesfully!")

        except Exception as e:
            self.out(str(type(e).__name__))

    
    def __reload_plugin(self, plugin_name: str, manager: "PluginManager") -> None:
        """
        Reloads a plugin
        """

        try:
            manager.reload_plugin(plugin_name)
            self.out(f"Plugin {plugin_name} has been reloaded sucesfully!")

        except Exception as e:
            self.out(str(type(e).__name__))

    
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

            if type(obj).__name__ == "Server" and obj.config.high_permissions is False:
                self.out(f"{obj.name} config dont allow to modify attributes")
                return True
            
            if hasattr(obj, attr):
                
                setattr(obj, attr, value)
                Set = self.__lang["Set"]

                if hasattr(obj, "name"):
                    self.out(f"{Set} {obj.name}.{attr} = {value}")
                    return True
                else:
                    self.out(f"{Set} {obj.__str__()}.{attr} = {value}")
                    return True
                
        elif hasattr(obj, command) or "." in command:
            
            command = command.strip().split(".")
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
            
            if self.__handle_attributes(command, self.__handler) is True:
                return
            
            elif command.startswith("set-language"):

                lang = command[13:]
                self.__handler.set_lang(lang.strip())

                self.out(self.__lang["Language is now set to"] + " " + command.strip())
                return
            
            elif command.startswith("download-plugin"):
                
                plugin = command[16:].strip()
                self.__download_plugin(plugin, self.__handler.servers[0].plugin_manager)
                return

            elif command.startswith("update-plugin"):
                
                plugin = command[14:].strip()
                self.__update_plugin(plugin, self.__handler.servers[0].plugin_manager)
                return

            self.__handler.to_all_servers(lambda s: s.execute(command))

        else:
            for server in self.__handler.servers:
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
                                str([p._name for p in server.get_online_players()]) or "[]"
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
                                self.out(server.name, self.__lang["Language is now set to"] + " " + command.strip())
                            
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