# type: ignore

from typing import Optional, List
from datetime import datetime, timedelta
from math import floor

from . import plugins
from . import text
from .context import Context
from .__version__ import __version__ as conduit_version
from .changelog import CHANGELOGS


def plg(plugin_name: str) -> str:
    """
    Replaces `-` symbols with `_` so players can avoid to press shift when the type a plugin name
    """

    return plugin_name.replace("-", "_")


class BuiltinPlugin(plugins.Plugin[None, None]):
    """
    Conduit utilities
    """

    
    Plugin = plugins.Command.group(
        name="plugin",
        aliases=["plg"]
    )
    __start_datetime: datetime


    def on_load(self):
        self.__start_datetime = datetime.now()

    
    @plugins.command
    def help(self, ctx: Context, args: List[str] | None = None):
        """
        Gives info on the given command/plugin
        """

        self.server.handler.telemetry.help_invoked(args)

        if args is None:

            self._help0(ctx)
            return

            p = self.manager.command_prefix

            ctx.reply(text.Text("Builtin commands:"))
            ctx.reply(text.gray(f"{p}help <command/plugin>").hover("Click to paste in chat").click(suggest_command=f"{p}help"))
            ctx.reply(text.gray(f"{p}version").hover("Click to paste in chat").click(suggest_command=f"{p}version"))

            if ctx.player.permissions >= plugins.Permission.Helper:
                
                ctx.reply("Commands with permissions:")
                ctx.reply(text.gray(f"{p}plugin <load/unload/download/reload/update/list>").hover("Click to paste in chat").click(
                    suggest_command=f"{p}plugin"
                ))
                ctx.reply(text.gray(f"{p}setlang <lang>").hover("Click to paste in chat").click(suggest_command=f"{p}setlang"))
                ctx.reply(text.gray(f"{p}reload").hover("Click to paste in chat").click(suggest_command=f"{p}reload"))

            else:
                ctx.reply(text.gray(f"{p}plugin list").hover("Click to paste in chat").click(suggest_command=f"{p}plugin list"))

            return
        
        if len(args) == 1:

            p_name = plg(args[0])
            plg_inst = self.manager.get_plugin_named(p_name)

            if plg_inst is not None:
                
                self._help_plugin(ctx, p_name, plg_inst)

        try:

            if len(args) > 0:
                command = " ".join(args)
            
            c_doc = self.manager.get_command_help(command)

            if c_doc is not None:
                ctx.reply(c_doc)
            
            else:
                
                if plg_inst is None:
                    c_name = " ".join(args)
                    ctx.reply(text.red(f"Unable to find commands or plugins named `{c_name}`"))

        except Exception as e:
            ctx.reply(text.red(f"Parsing error: {type(e).__name__}"))


    def _useful_commands(self, ctx: Context):

        p = self.manager.command_prefix
        
        ctx.reply("")
        res = text.gold("[USEFUL COMMANDS]\n")
        res += text.suggester("plugin list", prefix=p).gray() + "\n"

        if ctx.player.permissions >= plugins.Permission.Helper: # type: ignore
            res += text.suggester("setlang", prefix=p).gray() + "\n"
            res += text.suggester("reload", prefix=p).gray() + "\n"

        res += text.suggester("perms", prefix=p).gray() + "\n"
        res += text.suggester("version", prefix=p).gray() + "\n"
        
        tutorial = self.manager.get_plugin_named("tutorial")

        if tutorial is not None:
            ...
        else:
            res += text.button(
                "INSTALL TUTORIAL"
            ).dark_aqua()

        ctx.reply(res)

        
    def _help0(self, ctx: Context):
        """
        [HELP]

        *!!help* is the main command to get documentation for plugin/commands.
        Usage:
        !!help <plugin> e.g: !!help builtin_plugin
        !!help <command> e.g: !!help plugin list

        [USEFUL COMANDS]
        {
        !!plg list
        +{all plugins if opped}
        !!perms
        !!version
        +{tutorial if allowed}
        +{suggest tutorial if not allowed}
        }
        """

        p = self.manager.command_prefix
        
        res = text.gold("[HELP]\n")
        res += text.bold(f"{p}help")
        res += text.italic(" is the main way to get documentation for plugin/commands\n")
        res += text.dark_aqua("Usage:\n").underlined()

        res += text.gray(f"{p}help <plugin> e.g: ")
        help_plg = text.gray(f"{p}help builtin-plugin\n").underlined()
        help_plg.hover("Click to paste in chat!")
        help_plg.click(suggest_command=f"{p}help builtin-pligin")
        res += help_plg

        res += text.gray(f"{p}help <command> e.g: ")
        help_cmd = text.gray(f"{p}help plugin list\n").underlined()
        help_cmd.hover("Click to paste in chat!")
        help_cmd.click(suggest_command=f"{p}help plugin list")
        res += help_cmd
        res += "\n"
        
        res += text.button(
            "USEFUL COMMANDS",
            show_text="Click to display useful commands",
            run_function=self._useful_commands
        ).dark_aqua()

        ctx.reply(res)


    def _help_plugin(
        self,
        ctx: Context,
        p_name: str,
        plg: plugins.Plugin
    ):

        res = text.gold("[PLUGIN]\n")
        res += text.dark_aqua(p_name).bold().hover(show_text=f"v{plg.version}")
        res += text.white(": ")
        res += text.aqua(plg.desc).italic()
        res += "\n\n"

        if len(plg.commands) > 0:
                    
            res += text.dark_aqua("• Commands ")
            res += text.aqua(f"({len(plg.commands)})")
            res += text.white(":\n")

            # This might be replaced by a table
            for command in plg.commands:
                
                res += text.dark_aqua(f"  • {command.names[0]}")
                res += " "
                res += text.button(
                    "DOCS",
                    show_text="Click to see full docs",
                    suggest_command=f"{self.manager.command_prefix}help {command.names[0]}"
                ).gold()
                res += "\n"

        ctx.reply(res)


    @plugins.command(name="version")
    def _version(self, ctx: Context):
        """
        Displays Conduit version
        """

        ctx.info(f"Conduit-v{conduit_version}")

    
    @_version.command
    def list(self, ctx: Context):
        """
        Lists all Conduit versions up to the current one
        """

        raise NotImplementedError

    
    @plugins.command
    def perms(self, ctx: Context, player_name: Optional[str]=None):
        """
        Displays the permissions for the given player.

        If player is not specified displays the permissions for the one who sent the command
        """

        if player_name is None:
            player_name = ctx.player.name
        
        p = self.server.get_permissions_for(player_name)

        ctx.info(f"Player {player_name} has {p} permissions")

    
    @perms.command(checks=[plugins.check_perms(plugins.Permission.Owner)])
    def set(self, ctx: Context, player_name: str, permission: str):
        """
        Sets the specified permission to the given player
        """

        current_perms = self.server.get_permissions_for(player_name)

        try:
            p = plugins.Permission.from_name_or_level(permission)
        except:
            ctx.error(f"Permission `{permission}` doesn not exist")
            return

        if current_perms == permission:
            ctx.error(f"{player_name} has already {player_name} permissions!")
            return

        action: str
        
        if permission >= current_perms:

            action = "upgraded"

        else:
            raise NotImplementedError() # Too fucking hard rn
            action = "downgraded"

            self.server.execute(f"/team leave {player_name}")

        teams = self.servers.permissions[permission]

        if len(teams) > 0:
            team = teams[0]
        else:
            ctx.error(f"There is no team assigned to {permission}s!")
            return
            
        self.server.execute(f"/team join {team} {player_name}")
        
        ctx.success(f"Permissions for {player_name} have been {action} to {permission}")
        

    @Plugin.command(checks=[plugins.check_perms(plugins.Permission.Helper)])    
    def download(self, ctx: Context, plugin_name: str):
        """
        Download a plugin from ConduitPlugin GitHub repo
        """

        plugin_name = plg(plugin_name)

        try:
            self.manager.download_plugin(plugin_name)

            ask_to_load = text.gray("Do you want to load it?")
            ask_to_load.hover(show_text="Click to load")
            ask_to_load.click(f"{self.manager.command_prefix}plugin load {plugin_name}")

            ctx.reply(ask_to_load)
            
        except Exception as e:
            ctx.error(e)

    
    @Plugin.command(checks=plugins.check_perms(plugins.Permission.Helper))
    def load(self, ctx: Context, plugin_name: str, not_perm: plugins.Flag):
        """
        Loads a plugin
        """

        plugin_name = plg(plugin_name)
        
        try:
            self.manager.load_plugin(plugin_name, not not_perm)

        except Exception as e:
            ctx.error(e)

    
    @Plugin.command(checks=[plugins.check_perms(plugins.Permission.Helper)])
    def unload(self, ctx: Context, plugin_name: str, not_perm: plugins.Flag):
        """
        Unloads a loaded plugin
        """

        plugin_name = plg(plugin_name)

        try:
            self.manager.unload_plugin(plugin_name, not not_perm)

        except Exception as e:
            ctx.error(e)

    
    @Plugin.command(checks=[plugins.check_perms(plugins.Permission.Helper)])
    def update(self, ctx: Context, plugin_name: str):
        """
        Updates a plugin, if possible
        """

        plugin_name = plg(plugin_name)

        try:
            self.manager.update_plugin(plugin_name)

            ask_to_reload = text.Text("Reload it now?").underlined()
            ask_to_reload.hover(show_text="Click here to reload")
            ask_to_reload.click(suggest_command=f"{self.manager.command_prefix}plugin reload {plugin_name}")

            ctx.info(ask_to_reload)

        except Exception as e:
            ctx.error(e)

    
    @Plugin.command(checks=[plugins.check_perms(plugins.Permission.Helper)])
    def skipupdate(self, ctx: Context, plugin_name: str):
        """
        Skips the updates for the given plugin
        """

        plugin_name = plg(plugin_name)

        try:
            self.server.handler.plugin_catalogue.skip_update(plugin_name)

            confirm = text.Text(f"Stopping updates of `{plugin_name}`")
            confirm.hover(show_text="Click here to update")
            confirm.click(suggest_command=f"{self.manager.command_prefix} plugin update {plugin_name}")

            ctx.success(confirm)

        except Exception as e:
            ctx.error(e)

    
    @Plugin.command(checks=[plugins.check_perms(plugins.Permission.Helper)])
    def reload(self, ctx: Context, plugin_name: str):
        """
        Reloads a plugin
        """

        plugin_name = plg(plugin_name)
        
        try:
            self.manager.reload_plugin(plugin_name)
        
        except Exception as e:
            ctx.error(e)

    
    @Plugin.command
    def list(self, ctx: Context, t: plugins.Flag):
        """
        Displays loaded plugins
        """

        if t is False:
            plugin_list = " • ".join([plugin.name for plugin in self.manager.plugins])
        
            message = text.dark_aqua(f"Loaded plugins ({len(self.manager.plugins)}): ")
            message += text.aqua(plugin_list)
        else:
            message = "<not implemented yet>"

        ctx.reply(message)

    
    @plugins.command
    def news(self, ctx: Context, version: Optional[str]=None):
        """
        Prints the cangelog of the given Conduit version.
        """

        CHANGELOG_COLORS = {
            "added": text.green,
            "modified": text.gold,
            "fixed": text.aqua,
            "removed": text.red
        }

        if version is None:
            version = conduit_version

        if version not in CHANGELOGS.keys():

            ctx.error(f"There is no version named `{version}`")
            return
        
        ctx.info(f"{version} CHANGELOG:\n")

        for field, changes in CHANGELOGS[version].items():
            
            if len(changes) > 0:
                
                message = CHANGELOG_COLORS[field](f"{field[0].upper()}{field[1:]}:\n")

                for change in changes:
                    message += (f"  • {change}\n")

                ctx.reply(message)

    
    @plugins.command
    def uptime(self, ctx: Context):
        """
        Shows the running time of conduit
        """

        start_date = self.__start_datetime.date()
        current_time = datetime.now()
        delta: timedelta = current_time - self.__start_datetime

        d = delta.days
        h, remainder = divmod(delta.seconds, 3600)
        m, s = divmod(remainder, 60)

        uptime_in_days = round(delta.total_seconds() / 86400, 2)
        uptime_in_hours = round(delta.total_seconds() / 3600, 2)
        uptime_in_minutes = floor(delta.total_seconds() / 60)

        start_str = self.__start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        answ = text.dark_aqua("Conduit has been running since ")
        answ += text.aqua(start_str).italic()
        answ += text.dark_aqua(" for a total of ")
        answ += text.dark_aqua(f"{d} days").hover(show_text=f"{uptime_in_days} days") + ", "
        answ += text.dark_aqua(f"{h} hours").hover(show_text=f"{uptime_in_hours} hours") + ", "
        answ += text.dark_aqua(f"{m} minutes").hover(show_text=f"{uptime_in_minutes} minutes")
        
        ctx.reply(answ)


    @plugins.perms(plugins.Permission.Helper)
    @plugins.command
    def setlang(self, ctx: Context, lang: str):
        
        try:
            if self.server.set_lang(lang):
                ctx.success(f"Lang has been changed sucesfully to {lang}!")
                
        except Exception as e:
            ctx.error(e)


    @plugins.perms(plugins.Permission.Helper)
    @plugins.command
    def reload(self, ctx: Context):
        """
        Reloads Conduit
        """

        try:
            self.server.handler.reload()
        except Exception as e:
            ctx.error(e)

    
    def on_unload(self):
        
        self.server.tellraw(
            "@a",
            text.red("[Conduit]: Stopped!")
        )