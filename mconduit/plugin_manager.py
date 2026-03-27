from typing import Optional, Callable, Dict, List, Any, TYPE_CHECKING
from pathlib import Path
import importlib.util
import importlib
import threading
import json
import sys
import gc
import os

from .event import Event
from .enums import At
from . import text
from .utils import ConduitError
from .context import Context
from .lang.lang import Lang
from .plugins.plugin import Plugin, CommandCompletion
from .plugins.plugin_command import Command
from .plugins.arg_parser import Parser
from .plugins.command_cache import CommandCache
from .builtin_plugin import BuiltinPlugin
from .constants import *

if TYPE_CHECKING:
    from .server import Server
    from .handler import Handler


class PluginNotInArchive(Exception):
    ...

class PluginAlreadyUpdated(Exception):
    ...

class PluginNotLoaded(Exception):
    ...

class PluginAlreadyLoaded(Exception):
    ...

class PluginAlreadyDownloaded(Exception):
    ...

class PluginDoesntExist(Exception):
    ...

class UnableToDownloadPlugin(Exception):
    ...

class MissingMetadataFile(Exception):
    ...

class MissingPluginVersion(Exception):
    ...

class MissingPluginEntrypoint(Exception):
    ...

class MissingPluginClass(Exception):
    ...

class BuiltinPluginInvalidOperation(Exception):
    ...


class PluginManager:
    """
    Conduit Plugin manager
    """

    __server: "Server"
    __plugins: List[Plugin]
    __parser: Parser
    __command_cache: CommandCache
    __lock: threading.RLock
    _skipped_updates: List[str]


    def __init__(self, server: "Server") -> None:
        
        self.__lock = threading.RLock()
        self.__server = server
        self.__plugins = []
        self.__parser = Parser()
        self.__command_cache = CommandCache()
        self._skipped_updates = []
        self.__plugins = [BuiltinPlugin(self, {"name": "builtin_plugin", "version": "0.0.0", "description": "Conduit utilities"}, None)]
        
        self.__server._add_event_fallback(Event.PlayerCommand, self._on_command)
        self.__server._add_event_fallback(Event.ConduitStop, self.about_to_stop_plugins)

        
    def _try_update_plugin(
        self,
        plugin_name: str,
        new_version: str
    ) -> None:
        """
        Notify the plugin update with the player and updates the plugin if the player agrees.

        This should be called only by PluginCatalogue._check_for_updates()
        """
        
        if not self.are_plugins_loaded(plugin_name):
            return

        update_notify = text.gold(f"Plugin `{plugin_name}` can be updated from ")
        update_notify += text.dark_gray(self.get_plugin_named(plugin_name).version) # type: ignore
        update_notify += text.gold(" to ") + text.green(new_version)
        
        ask_to_update = text.gold("Update now? ")
        ask_to_update += text.green("[✔]").click(suggest_command=f"!!plugin update {plugin_name}") + " "
        ask_to_update += text.red("[X]").click(suggest_command=f"!!plugin skipupdate {plugin_name}")

        self.server.tellraw("@a", update_notify)
        self.server.tellraw("@a", ask_to_update)

    
    def _fetch_plugin_metadata(self, plugin_name: str) -> Dict[str, Any]:
        """
        Loads the metadata for the given plugin
        """

        filename = Path(PLUGINS_DIR).joinpath(plugin_name)

        if not filename.exists():
            raise PluginDoesntExist()

        meta_path = os.path.join(filename, METADATA_FILENAME)
        
        if not Path(meta_path).exists():
            raise MissingMetadataFile()

        return json.load(open(meta_path))


    def _handle_plugins_raises(self) -> None:
        """
        Checks if any of the loaded plugins has raised an exception and it's totally crashes.

        If so, restarts it
        """

        for plugin in self.__plugins:
            
            try:
                if not (plugin._running_check() is True):

                    plugin_name = plugin.name
                    self.reload_plugin(plugin_name)
                    self.server.tellraw(At.AllPlayers, text.gold(f"Plugin `{plugin_name}` has been reloaded after it crashed"))
            except:
                pass
    
    
    def _find_plugin_class(self, module) -> Optional[type[Plugin]]:
        """
        Returns the first subclass of `Plugin` that it finds in the module.

        Note: the other functions / classes (even other subclasses of `Plugin`) will be ignored
        """
        
        for item in module.__dict__.values():
            
            if isinstance(item, type) and issubclass(item, Plugin):

                if item.__name__ != "Plugin":
                    return item


    def _load_plugin(self, plugin_name: str) -> Plugin:
        """
        Loads the given plugin and creates an instance of it
        """
        
        filename = Path(PLUGINS_DIR).joinpath(plugin_name)
        metadata = self._fetch_plugin_metadata(plugin_name)

        if not "entrypoint" in metadata.keys():
            raise MissingPluginEntrypoint()
        
        module_name = f"{self.server.name}-{plugin_name}"
        entrypoint = metadata["entrypoint"]
        file_path = os.path.join(filename, entrypoint)
        is_package = entrypoint == "__init__.py"

        if is_package:
            
            spec = importlib.util.spec_from_file_location(
                module_name,
                file_path,
                submodule_search_locations=[str(filename)]
            )
        
        else:
            spec = importlib.util.spec_from_file_location(
                module_name,
                file_path
            )
        
        if spec is None:
            raise RuntimeError(f"Unable to fetch module spec from file_path: {file_path} and module_name: {module_name}")
        
        module = importlib.util.module_from_spec(spec)
        
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module) # type: ignore
        except Exception as e:
            raise e

        if plugin := self._find_plugin_class(module):

            try:
                
                lang_path = Path(filename) / LANG_DIR
                plg_lang = None

                if lang_path.exists():
                    plg_lang = Lang(lang_path, self.__server.lang.lang)
                
                plugin = plugin(self, metadata, plg_lang) # type: ignore

                return plugin # type: ignore
            
            except Exception as e:
                raise e
        else:
            raise MissingPluginClass()


    def _make_plugin_text(self, plugin_name: str) -> text.Text:
        """
        Creates the plugin name
        """

        plugin = self.get_plugin_named(plugin_name)

        plugin_text = text.green(f" `{plugin_name}` ").italic()

        if plugin is not None:
            plugin_text.hover(show_text=text.yellow(plugin.desc))

        elif metadata := self._fetch_plugin_metadata(plugin_name):
            plugin_text.hover(show_text=metadata["version"])
        
        return plugin_text
    

    def download_plugin(self, plugin_name: str) -> None:
        """
        Downloads the given plugin, if it's not in the `plugins` folder yet
        """
        
        try:
            self.server.handler.plugin_catalogue.download_plugin(plugin_name)

            self.to_all_plugins(lambda p: p.on_plugin_downloaded(plugin_name))
            
            confirm = text.green("Plugin") + self._make_plugin_text(plugin_name) + "has been downloaded sucesfully!"
            self.server.tellraw("@a", confirm)

        except Exception as e:
            raise e


    def update_plugin(self, plugin_name: str) -> None:
        """
        Updates the given plugin, if its downloaded
        """

        try:
            self.server.handler.plugin_catalogue.update_plugin(plugin_name)

            confirm = text.green("Plugin") + self._make_plugin_text(plugin_name) + "has been updated sucesfully!"
            self.server.tellraw("@a", confirm)

        except Exception as e:
            raise e
        

    def load_plugin(
        self,
        plugin_name: str,
        load_permanently: bool=True,
        notify: bool=True
    ) -> None:
        """
        Loads the specified plugin
        """

        if self.get_plugin_named(plugin_name):
            raise PluginAlreadyLoaded()

        try:

            with self.__lock:

                plugin = self._load_plugin(plugin_name)
                self.__plugins.append(plugin)
                
            self.to_all_plugins(lambda p: p.on_plugin_loaded(plugin))
            self.server.handler.plugin_catalogue.set_permanent(self.server, plugin_name, load_permanently)

            self.server.handler.telemetry.plugin_load(self.server, plugin_name)

            if notify is True:
                confirm = text.green("Plugin") + self._make_plugin_text(plugin_name) + "loaded sucesfully!"
                self.server.tellraw("@a", confirm)
        
        except Exception as e:
            raise e

    
    def __purge_package(self, plugin_name: str) -> None:

        to_delete = [
            name for name in sys.modules
            if name == plugin_name or name.startswith(plugin_name + ".")
        ]

        for module in to_delete:
            sys.modules.pop(module, None)
        
    
    def _unload_plugin(self, plugin: Plugin) -> None:
        """
        Unload the given plugin and unlinks all it's data 
        """

        with self.__lock:

            plugin._about_to_stop()

            self.__plugins.remove(plugin)
            plugin_name = str(plugin.name)
            del plugin

            module_name = f"{self.server.name}-{plugin_name}"
            self.__purge_package(module_name)
                
            importlib.invalidate_caches()
            gc.collect()

        
    def unload_plugin(
        self,
        plugin_name: str,
        unload_permanently: bool=True,
        notify: bool=True
    ) -> None:
        """
        Unloads the specified plugin, if it's loaded.

        It removes it from `active_plugins.json` if save_permanently it's set to True
        """

        if plugin_name in ["builtin_plugin", "builtin-plugin"]:
            raise BuiltinPluginInvalidOperation

        plugin_to_remove = self.get_plugin_named(plugin_name)

        self.to_all_plugins(lambda p: p.on_plugin_unloaded(plugin_to_remove)) # type: ignore

        if plugin_to_remove:

            p_name = self._make_plugin_text(plugin_name)

            self._unload_plugin(plugin_to_remove)
            
            self.server.handler.plugin_catalogue.set_permanent(self.server, plugin_name, not unload_permanently)
            self.server.handler.telemetry.plugin_unload(self.server, plugin_name)

            if notify is True:
                confirm = text.green("Plugin") + p_name + "unloaded sucesfully!"
                self.server.tellraw("@a", confirm)

        else:
            raise PluginNotLoaded()
        
    
    def reload_plugin(self, plugin_name: str) -> None:
        """
        Reloads the specified plugin
        """

        if plugin_name in ["builtin_plugin", "builtin-plugin"]:
            raise BuiltinPluginInvalidOperation
        
        try:
            self.to_all_plugins(lambda p: p.on_plugin_reloaded(self.get_plugin_named(plugin_name))) # type: ignore

            self.unload_plugin(plugin_name, notify=False)
            self.load_plugin(plugin_name, notify=False)

            confirm = text.green("Plugin") + self._make_plugin_text(plugin_name) + "has been reloaded sucesfully!"
            self.server.tellraw("@a", confirm)

        except Exception as e:
            raise e


    def load_all_plugins(self) -> None:
        """
        Loads and starts all the plugins present in `active_plugins.json`
        """

        errors = []
        
        for plugin_name in self.server.handler.plugin_catalogue.get_active_plugins_for(self.server):

            try:
                self.__plugins.append(self._load_plugin(plugin_name))
            except Exception as e:
                errors.append((plugin_name, e))

        if errors:

            self.server.tellraw("@p", text.red("Unable to load these plugins:"))

            for p_name, err in errors:
                
                disp = text.dark_aqua(f"  • {p_name}: ")
                disp += ConduitError.from_exception(err).to_text()

                self.server.tellraw("@p", disp)

    
    def are_plugins_loaded(self, *plugins_names) -> bool:
        """
        Checks if the given plugins are loaded
        """

        for plugin_name in plugins_names:
            
            if self.get_plugin_named(plugin_name) is None:
                return False

        return True
    

    def to_all_plugins(self, fn: Callable[[Plugin], Any]) -> None:

        for plugin in self.__plugins:

            try:
                fn(plugin)
            except:
                pass

        
    def about_to_stop_plugins(self, handler: "Handler") -> None:
        """
        Calls about_to_stop to every plugin
        """

        for plugin in self.__plugins:
            plugin._about_to_stop()

    
    def set_lang(self, lang: str) -> None:
        """
        Changes the lang to all the loaded plugins
        """

        for plugin in self.__plugins:

            if plugin.lang is not None:
                plugin.lang.set_lang(lang)
    

    @property
    def server(self) -> "Server":
        """
        Server instance for this manager 
        """

        return self.__server

    
    @property
    def plugins(self) -> List[Plugin]:
        """
        Servers loaded plugins
        """

        return list(self.__plugins)

    
    @property
    def command_prefix(self) -> str:
        """
        Conduit command prefix
        """

        return self.server.handler.command_prefix
    

    def _command_completion_text(self, completion: CommandCompletion) -> str:
        """
        Builds command completion Minecraft Text.

        Format:

        • <command-name>: description (optional)
        • underlined + run_action
        """

        command_prefix = self.__server.handler.command_prefix


    def get_plugin_named(self, plugin_name: str) -> Optional[Plugin]:
        """
        Returns the plugin instance with the given name, if it exist
        """

        for plugin in self.__plugins:
            if plugin.name == plugin_name:
                return plugin
    

    def _display_last_commands(self, ctx: Context) -> None:
        """
        Displays players last commands present in `command_cache.json`
        """

        # TODO: Consider remove commands from unloaded plugins?

        commands = self.__command_cache.get_last_commands(ctx)

        if len(commands) == 0:
            commands = [["help"], ["version"], ["news"]]

            if ctx.player.permissions >= 2: # type: ignore
                commands.extend([
                    ["plugin"],
                    ["setlang"],
                ])

        for command in commands:
                
                cmd = self.__server.handler.command_prefix

                for arg in command:
                    cmd += " " + arg

                ctx.reply(
                    text.gray(cmd).underlined().hover(
                    show_text="Click to paste in chat").click(
                    suggest_command=cmd
                    )
                )
    

    def _on_command(self, ctx: Context) -> None:
        
        command = ctx.command.strip().replace(self.__server.handler.command_prefix, "").strip() # type: ignore
        
        if len(command) == 0:
            
            self._display_last_commands(ctx)
            return

        try:
            args, flags = self.__parser.parse_args(command)
        except Exception as e:
            ctx.reply("Parsing error:", ConduitError.from_exception(e).to_text())
            return
        
        for plugin in self.__plugins:
            for command in plugin.commands:
                
                if  args[0] in command.names:
                    try:
                        command_args = args[1:] if len(args) > 1 else []
                        
                        if command._execute(ctx, command_args, flags):
                            self.__command_cache.update(ctx, args, flags)
                            return
                        
                    except Exception as e:
                        ctx.error(e)
                        return
        
        command_completions = []

        for plugin in self.__plugins:
            command_completions.extend(plugin._get_command_completion(args, ctx))
        
        if len(command_completions) > 0:

            for command in command_completions:

                cmd = self.__server.handler.command_prefix + command

                ctx.reply(
                    text.gray(cmd).underlined().hover(
                    show_text="Click to paste in chat").click(
                    suggest_command=cmd
                    )
                )
        else:
            ctx.error("Command not found!")


    def _get_help_recursively(self, command: Command, cmd: List[str]) -> text.Text:
        """
        Fetches help of the most nested command it can find
        """

        temp_docs = text.Text("")

        for subcommand in command.subcommands:

            if cmd[0] in subcommand.names:

                if len(cmd) > 1:
                    temp_docs += self._get_help_recursively(subcommand, cmd[1:])

                else:
                    temp_docs += subcommand._get_docstring(self.command_prefix)

        return temp_docs


    def get_command_help(self, cmd: str) -> Optional[text.Text]:
        """
        Returns docstring of the given command, if it exists
        """

        try:
            cmd, _flags = self.__parser.parse_args(cmd.strip()) # type: ignore
        except Exception as e:
            raise e

        out = text.Text("")
        
        for plugin in self.__plugins:

            for command in plugin.commands:
                
                if cmd[0] in command.names:
                    
                    if len(cmd) > 1:

                        out += self._get_help_recursively(command, cmd[1:]) # type: ignore
                    
                    else:
                        out += command._get_docstring(self.command_prefix)

        if len(out.plain_text) > 0:
            return out