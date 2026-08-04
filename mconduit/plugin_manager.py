from __future__ import annotations
from typing import Optional, Callable, Dict, List, Any, TYPE_CHECKING
from pathlib import Path
import importlib.util
import importlib
import threading
import json
import sys
import gc
import os

from mconduit import text
from mconduit import perms
from mconduit.event import Event
from mconduit.enums import At
from mconduit.__version__ import __version__
from mconduit.utils.errors import ConduitError
from mconduit.utils.version import Version, VersionCheck
from mconduit.context import Context
from mconduit.lang.lang import Lang
from mconduit.plugins.plugin import Plugin, CommandCompletion
from mconduit.plugins.plugin_command import Command
from mconduit.plugins.arg_parser import Parser
from mconduit.plugins.command_cache import CommandCache
from mconduit.builtin_plugin import BuiltinPlugin # type: ignore
from mconduit.constants import *

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

class InvalidConduitVersion(Exception):
    ...

class RequiredPluginNotLoaded(Exception):
    ...

class InvalidRequiredPluginVersion(Exception):
    ...

class InvalidMinecraftVersion(Exception):
    ...


class PluginManager:
    """
    Conduit Plugin manager
    """

    _server: Server
    _plugins: List[Plugin]
    _parser: Parser
    _command_cache: CommandCache
    _lock: threading.RLock


    def __init__(
        self,
        server: Server
    ) -> None:
        
        self._lock = threading.RLock()
        self._server = server
        self._plugins = []
        self._parser = Parser()
        self._command_cache = CommandCache()
        self._plugins = [BuiltinPlugin(self, {"name": "builtin_plugin", "version": "0.0.0", "description": "Conduit utilities"}, None)]
        
        self._server._add_event_fallback(Event.PLAYER_COMMAND, self._on_command)
        self._server._add_event_fallback(Event.CONDUIT_STOP, self.about_to_stop_plugins)

        
    def _try_update_plugins(
        self,
        plugins_to_update: Dict[str, List[str]]
    ) -> None:
        """
        Notify the plugin update with the player and updates the plugin if the player agrees.

        This should be called only by PluginCatalogue._check_for_updates()
        """

        msg = text.Text("")

        builtin_plugin = self.get_plugin_named("builtin_plugin")
        update_plugin = builtin_plugin.get_command_named("plugin", "update").fallback # type: ignore
    
        for p_name, (c_version, n_version) in plugins_to_update.items():

            msg += text.dark_aqua(" • " + p_name + ": ")
            msg += text.gold(c_version) + text.dark_aqua( " --> ") + text.green(n_version)
                
            msg += text.button(
                f"{text.icon.plus} Update",
                show_text=text.aqua("Click to update it now!"),
                run_function=lambda c: update_plugin(c, p_name)
            ).dark_aqua()
            
            msg.endl()
            
        self.server.tellraw("@a", msg)

    
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

        for plugin in self._plugins:
            
            try:
                if not (plugin._running_check() is True):

                    plugin_name = plugin.name
                    self.reload_plugin(plugin_name)
                    self.server.tellraw(At.ALL_PLAYERS, text.gold(f"Plugin `{plugin_name}` has been reloaded after it crashed"))
            except:
                pass

        return None
    
    
    def _find_plugin_class(self, module) -> Optional[type[Plugin]]:
        """
        Returns the first subclass of `Plugin` that it finds in the module.

        Note: the other functions / classes (even other subclasses of `Plugin`) will be ignored
        """
        
        for item in module.__dict__.values():
            
            if isinstance(item, type) and issubclass(item, Plugin):

                if item.__name__ != "Plugin":
                    return item

        return None

    
    def _do_plugin_checks(self, plugin_metadata: Dict[str, Any]) -> None:
        """
        Runs all the plugin checks present in the metadata.

        This should be called ONLY by _load_plugin(), to assert the plugin can be loaded.

        Checks:

        1) Conduit version
        2) Plugin dependencies
        3) Minecraft version
        """

        if "conduit_version" in plugin_metadata:

            conduit_version = plugin_metadata["conduit_version"]
            version_check = VersionCheck.from_string(conduit_version)

            current_version = Version.from_string(__version__)

            if not version_check.check_for(current_version):
                raise InvalidConduitVersion(f"Required version: {conduit_version}, current version: {__version__}")

        if "plugin_dependencies" in plugin_metadata:

            plugin_dependencies = plugin_metadata["plugin_dependencies"]

            for dependency in plugin_dependencies:

                if (
                    "=" in dependency or
                    ">" in dependency or
                    "<" in dependency
                ):
                    check = VersionCheck.from_string(dependency)

                    assert check.dependency is not None

                    plg = self.get_plugin_named(check.dependency)
                    
                    if plg is None:
                        raise RequiredPluginNotLoaded(check.dependency)

                    if not check.check_for(plg.version):
                        raise InvalidRequiredPluginVersion(f"Required version: {dependency}, current version: {plg.version}")

                elif not self.are_plugins_loaded(dependency):
                    raise RequiredPluginNotLoaded(check.dependency)

        if "minecraft_version" in plugin_metadata:

            minecraft_version = plugin_metadata["minecraft_version"]
            version_check = VersionCheck.from_string(minecraft_version)
            
            if (
                self.server.version is not None and
                not version_check.check_for(self.server.version)
            ):
                raise InvalidMinecraftVersion(f"Required version: {version_check}, current version: {self.server.version}")


    def _load_plugin(self, plugin_name: str) -> Plugin:
        """
        Loads the given plugin and creates an instance of it
        """
        
        filename = Path(PLUGINS_DIR).joinpath(plugin_name)
        metadata = self._fetch_plugin_metadata(plugin_name)

        self._do_plugin_checks(metadata)

        if "entrypoint" not in metadata.keys():
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
            self.__purge_package(module_name)
            raise e

        if plugin := self._find_plugin_class(module):

            try:
                
                lang_path = Path(filename) / LANG_DIR
                plg_lang = None

                if lang_path.exists():
                    plg_lang = Lang(lang_path, self._server.lang.lang)
                
                plugin = plugin(self, metadata, plg_lang) # type: ignore

                return plugin # type: ignore
            
            except Exception as e:
                
                self.__purge_package(module_name)
                raise e
        else:

            self.__purge_package(module_name)
            raise MissingPluginClass()


    def _make_plugin_text(self, plugin_name: str) -> text.Text:
        """
        Creates the plugin name
        """

        plugin = self.get_plugin_named(plugin_name)

        plugin_text = text.green(f" `{plugin_name}` ").italic()

        if plugin is not None:
            plugin_desc = plugin.desc
            
        else:
            try:
                metadata = self._fetch_plugin_metadata(plugin_name)
                plugin_desc = metadata["description"]

            except (PluginDoesntExist, MissingMetadataFile):
                plugin_desc = "unknown plugin"

        plugin_text.hover(show_text=text.yellow(plugin_desc))
        
        return plugin_text
    

    def download_plugin(
        self,
        plugin_name: str,
        force: bool = False
    ) -> None:
        """
        Downloads the given plugin, if it's not in the `plugins` folder yet
        """
        
        error = self.server.handler.plugin_catalogue.download_plugin(plugin_name, force)

        self.to_all_plugins(lambda p: p.on_plugin_downloaded(plugin_name))
            
        confirm = text.green("Plugin") + self._make_plugin_text(plugin_name) + "has been downloaded sucesfully!"
        self.server.tellraw("@a", confirm)

        if error is not None:

            msg = text.red("Error while installing python dependencies: ")
            msg += ConduitError.from_exception(error).to_text()

            self.server.tellraw("@a", msg)


    def update_plugin(self, plugin_name: str) -> None:
        """
        Updates the given plugin, if its downloaded
        """

        error = self.server.handler.plugin_catalogue.update_plugin(plugin_name)

        confirm = text.green("Plugin") + self._make_plugin_text(plugin_name) + "has been updated sucesfully!"
        self.server.tellraw("@a", confirm)

        if error is not None:

            msg = text.red("Error while installing python dependencies: ")
            msg += ConduitError.from_exception(error).to_text()

            self.server.tellraw("@a", msg)
        

    def load_plugin(
        self,
        plugin_name: str,
        load_permanently: bool = True,
        notify: bool = True
    ) -> None:
        """
        Loads the specified plugin
        """

        if self.get_plugin_named(plugin_name):
            raise PluginAlreadyLoaded()

        try:

            with self._lock:

                plugin = self._load_plugin(plugin_name)
                self._plugins.append(plugin)
                
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

        with self._lock:
            
            plugin._about_to_stop()

            self._plugins.remove(plugin)
            plugin_name = str(plugin.name)
            del plugin

            module_name = f"{self.server.name}-{plugin_name}"
            self.__purge_package(module_name)
                
            importlib.invalidate_caches()
            gc.collect()

        
    def unload_plugin(
        self,
        plugin_name: str,
        unload_permanently: bool = True,
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
                self._plugins.append(self._load_plugin(plugin_name))
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

        for plugin in self._plugins:

            try:
                fn(plugin)
            except:
                pass

        
    def about_to_stop_plugins(self, handler: Handler) -> None:
        """
        Calls about_to_stop to every plugin
        """

        for plugin in self._plugins:
            plugin._about_to_stop()

    
    def set_lang(self, lang: str) -> None:
        """
        Changes the lang to all the loaded plugins
        """

        for plugin in self._plugins:

            if plugin.lang is not None:
                plugin.lang.set_lang(lang)
    

    @property
    def server(self) -> Server:
        """
        Server instance for this manager 
        """

        return self._server

    
    @property
    def plugins(self) -> List[Plugin]:
        """
        Servers loaded plugins
        """

        return list(self._plugins)

    
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

        command_prefix = self._server.handler.command_prefix

        return command_prefix


    def get_plugin_named(self, plugin_name: str) -> Optional[Plugin]:
        """
        Returns the plugin instance with the given name, if it exist
        """

        for plugin in self._plugins:
            if plugin.name == plugin_name:
                return plugin

        return None
    

    def _display_last_commands(self, ctx: Context) -> None:
        """
        Displays players last commands present in `command_cache.json`
        """

        # TODO: Consider remove commands from unloaded plugins?

        commands = self._command_cache.get_last_commands(ctx)

        if len(commands) == 0:
            commands = [["help"], ["version"], ["news"]]

            if ctx.player.has_permission(perms.Builtin.HELPER): # type: ignore
                commands.extend([
                    ["plugin"],
                    ["setlang"],
            ])

        for command in commands:
                
            cmd = self._server.handler.command_prefix

            for arg in command:
                cmd += " " + arg

            ctx.reply(
                text.gray(cmd).underlined().hover(
                show_text="Click to paste in chat").click(
                suggest_command=cmd
                )
            )
    

    def _on_command(self, ctx: Context) -> None:
        
        command = ctx.command.strip().replace(self._server.handler.command_prefix, "").strip() # type: ignore
        
        if len(command) == 0:
            
            self._display_last_commands(ctx)
            return None

        try:
            args, flags = self._parser.parse_args(command)
        except Exception as e:
            ctx.reply("Parsing error:", ConduitError.from_exception(e).to_text())
            return None
        
        for plugin in self._plugins:
            for command in plugin.commands:
                
                if  args[0] in command.names:
                    try:
                        command_args = args[1:] if len(args) > 1 else []
                        
                        if command._execute(ctx, command_args, flags):
                            self._command_cache.update(ctx, args, flags)
                            return None
                        
                    except Exception as e:
                        ctx.error(e)
                        return None
        
        command_completions = []

        for plugin in self._plugins:
            command_completions.extend(plugin._get_command_completion(args, ctx))
        
        if len(command_completions) > 0:

            for command in command_completions:

                cmd = self._server.handler.command_prefix + command

                ctx.reply(
                    text.gray(cmd).underlined().hover(
                        show_text="Click to paste in chat").click(
                        suggest_command=cmd
                    )
                )
        else:
            ctx.error("Command not found!")

        return None


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
            cmd, _flags = self._parser.parse_args(cmd.strip()) # type: ignore
        except Exception as e:
            raise e

        out = text.Text("")
        
        for plugin in self._plugins:

            for command in plugin.commands:
                
                if cmd[0] in command.names:
                    
                    if len(cmd) > 1:

                        out += self._get_help_recursively(command, cmd[1:]) # type: ignore
                    
                    else:
                        out += command._get_docstring(self.command_prefix)

        if len(out.plain_text) > 0:
            return out

        return None