# type: ignore

from typing import Optional, List
from datetime import datetime, timedelta
from math import floor

from mconduit import plugins
from mconduit import perms
from mconduit import text
from mconduit.context import Context
from mconduit.__version__ import __version__ as conduit_version
from mconduit.changelog import CHANGELOGS


def plg(plugin_name: str) -> str:
    """
    Replaces `-` symbols with `_` so players can avoid to press shift when the type a plugin name
    """

    return plugin_name.replace("-", "_")


DIVIDERS = [
    60 * 60 * 24 * 365,
    60 * 60 * 24 * 30,
    60 * 60 * 24 * 7,
    60 * 60 * 24,
    60 * 60,
    60,
    1
]


def get_timestamps(time: timedelta | float | int) -> List[int]:

    if isinstance(time, timedelta):
        secs = time.total_seconds()
    else:
        secs = time

    return [int(secs / div) for div in DIVIDERS]


def format_time(time: timedelta) -> str: #TODO: Abstract into a time-format utility

    timestamps = get_timestamps(time)

    prefixes = ["years", "months", "weeks", "days", "hrs", "mins", "secs"]

    formatted_time = ""

    for i, (timestamp, prefix, div) in enumerate(zip(timestamps, prefixes, DIVIDERS)):
        
        if timestamp >= 1:
            
            formatted_time = f"{timestamp}{prefix}"

            if i < len(DIVIDERS) - 1:
                second_bit = get_timestamps(time.total_seconds() - timestamp * div)[i + 1]

                if second_bit >= 1:
                    formatted_time += f", {second_bit}{prefixes[i + 1]}"

            break

    return formatted_time


def time_since_release(release_date: str) -> text.Text:

    now = datetime.now()

    d, m, y = [int(item) for item in release_date.split("/")]

    release_date = datetime(day=d, month=m, year=y)

    formatted_time = format_time(now - release_date)

    return text.dark_aqua(formatted_time + " ago")


class BuiltinPlugin(plugins.Plugin):
    """
    Conduit utilities
    """

    
    Plugin = plugins.Command.group(
        name="plugin",
        aliases=["plg"]
    )
    _start_datetime: datetime


    def on_load(self):
        self._start_datetime = datetime.now()

    
    @plugins.command
    def help(
        self,
        ctx: Context,
        *args: str
    ):
        """
        Gives info on the given command/plugin
        """

        self.server.handler.telemetry.help_invoked(args)

        if args is None:

            self._help0(ctx)
            return
        
        if len(args) == 1:

            p_name = plg(args[0])
            plg_inst = self.manager.get_plugin_named(p_name)

            if plg_inst is not None:
                
                self._help_plugin(ctx, p_name, plg_inst)

        if len(args) > 0:
            command = " ".join(args)
            
        c_doc = self.manager.get_command_help(command)

        if c_doc is not None:
            ctx.reply(c_doc)
            
        elif plg_inst is None:
            c_name = " ".join(args)
            ctx.error(f"Unable to find commands or plugins named `{c_name}`")


    def _useful_commands(self, ctx: Context):

        p = self.manager.command_prefix
        
        ctx.reply("")
        res = text.gold("[USEFUL COMMANDS]\n")
        res += text.suggester("plugin list", prefix=p).gray().endl()

        if ctx.player.has_permission(perms.Builtin.HELPER): # type: ignore
            res += text.suggester("setlang", prefix=p).gray().endl()
            res += text.suggester("reload", prefix=p).gray().endl()

        res += text.suggester("perms", prefix=p).gray().endl()
        res += text.suggester("version", prefix=p).gray().endl()
        
        tutorial = self.manager.get_plugin_named("tutorial")

        if tutorial is not None:
            
            res += text.dark_aqua(f"{text.icon.check_mark} is installed!").endl()
            res += "Type " + text.suggester("help", "tutorial", prefix=p).aqua()

        else:
            
            download_plugin = self.get_command_named("plugin", "download")

            res += text.button(
                f"{text.icon.plus} INSTALL TUTORIAL",
                show_text=text.aqua("Click to install the tutorial plugin to get better help!"),
                run_function=lambda c: download_plugin(c, "tutorial")
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
        res += help_cmd.endl()
        
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
                res.endl()

        ctx.reply(res)


    @plugins.command(name="version")
    def _version(self, ctx: Context):
        """
        Displays Conduit version
        """

        msg = f"Conduit-v{conduit_version}"

        release_date = CHANGELOGS.get(conduit_version, None)
        
        if release_date is not None:

            release_date = release_date.get("release_date", None)

            if release_date is not None:
                
                msg += " • released: " + text.italic(release_date).hover(time_since_release(release_date))

        ctx.info(msg)

    
    @_version.command
    def list(self, ctx: Context):
        """
        Lists all Conduit versions up to the current one
        """

        """
        Conduit versions

        <dot> <v-name (different colors?)> <dot> released italic(<release_date>) 
        """

        msg = text.gray("Version list:").bold().endl()

        for v_name, v_data in CHANGELOGS.items():

            if v_data["release_date"] == "":
                continue
            
            msg += text.dark_aqua(" • ")
            msg += text.aqua(v_name)
            msg += text.dark_aqua(" released: ")
            msg += text.aqua(v_data["release_date"]).italic().hover(time_since_release(v_data["release_date"]))
            msg.endl()

        ctx.reply(msg)

    
    @plugins.command(name="perms")
    def perms_command(
        self,
        ctx: Context,
        player_name: Optional[str] = None
    ):
        """
        Displays the permissions for the given player.

        If player is not specified displays the permissions for the one who sent the command
        """

        if player_name is None:
            player_name = ctx.player.name
        
        p = self.server.get_permissions_for(player_name)

        ctx.info(f"Player {player_name} has {p} permissions")

    
    @perms_command.command
    @plugins.checks.has_perm(perms.Builtin.ADMIN)
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
        
    
    @Plugin.command
    @plugins.checks.has_perm(perms.Builtin.HELPER)
    def download(self, ctx: Context, plugin_name: str, force: plugins.Flag):
        """
        Download a plugin from ConduitPlugin GitHub repo
        """

        plugin_name = plg(plugin_name)

        try:
            self.manager.download_plugin(plugin_name, force)

            ask_to_load = text.gray("Do you want to load it?")
            ask_to_load.hover(show_text="Click to load")
            ask_to_load.click(f"{self.manager.command_prefix}plugin load {plugin_name}")

            ctx.reply(ask_to_load)
            
        except Exception as e:
            ctx.error(e)


    @Plugin.command
    @plugins.checks.has_perm(perms.Builtin.HELPER)
    def load(self, ctx: Context, plugin_name: str, not_perm: plugins.Flag):
        """
        Loads a plugin
        """

        plugin_name = plg(plugin_name)
        
        try:
            self.manager.load_plugin(plugin_name, not not_perm)

        except Exception as e:
            ctx.error(e)


    @Plugin.command
    @plugins.checks.has_perm(perms.Builtin.HELPER)
    def unload(self, ctx: Context, plugin_name: str, not_perm: plugins.Flag):
        """
        Unloads a loaded plugin
        """

        plugin_name = plg(plugin_name)

        try:
            self.manager.unload_plugin(plugin_name, not not_perm)

        except Exception as e:
            ctx.error(e)

    
    @Plugin.command
    @plugins.checks.has_perm(perms.Builtin.HELPER)
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

    
    @Plugin.command(name="skipped-updates", aliases=["su"])
    def skipped_updates(self, ctx: Context):
        """
        Skips the updates for the given plugin
        """

        perms_to_update = ctx.player.has_permission(perms.Builtin.HELPER)

        skipped_updates = self.server.handler.plugin_catalogue.get_plugins_to_update()
        
        if len(skipped_updates) == 0:
            ctx.info("There is no skipped update!")
            return

        update_plugin = self.get_command_named("plugin", "update")

        ctx.info(text.bold("Skipped updates").underlined())

        msg = text.Text("")
    
        for p_name, (c_version, n_version) in skipped_updates.items():

            msg += text.dark_aqua(" • " + p_name + ": ")
            msg += text.gold(c_version) + text.dark_aqua( " --> ") + text.green(n_version)

            if perms_to_update is True:

                msg += text.button(
                    f"{text.icon.plus} Update",
                    show_text=text.aqua("Click to update it now!"),
                    run_function=lambda c: update_plugin(c, p_name)
                ).dark_aqua()

            msg.endl()
            
        ctx.reply(msg)

    
    @Plugin.command(name="reload")
    @plugins.checks.has_perm(perms.Builtin.HELPER)
    def plugin_reload(self, ctx: Context, plugin_name: str):
        """
        Reloads a plugin
        """

        plugin_name = plg(plugin_name)
        
        try:
            self.manager.reload_plugin(plugin_name)
        
        except Exception as e:
            ctx.error(e)

    
    @Plugin.command(name="list")
    def plugin_list(self, ctx: Context, t: plugins.Flag):
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
    def news(
        self,
        ctx: Context,
        version: Optional[str] = None
    ):
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
        
        release_date = CHANGELOGS[version]["release_date"]
        ctx.info(f"{version} CHANGELOG: " + text.underlined(release_date).hover(time_since_release(release_date)).endl())

        for field, changes in CHANGELOGS[version].items():
            
            if field != "release_date" and len(changes) > 0:
                
                field_name = field[0].upper() + field[1:]

                message = CHANGELOG_COLORS[field](f"{field_name} ({len(changes)}):\n")

                for change in changes:
                    message += (f"  • {change}\n")

                ctx.reply(message)

    
    @plugins.command
    def uptime(self, ctx: Context):
        """
        Shows the running time of conduit
        """

        current_time = datetime.now()
        delta: timedelta = current_time - self._start_datetime

        d = delta.days
        h, remainder = divmod(delta.seconds, 3600)
        m, _s = divmod(remainder, 60)

        uptime_in_days = round(delta.total_seconds() / 86400, 2)
        uptime_in_hours = round(delta.total_seconds() / 3600, 2)
        uptime_in_minutes = floor(delta.total_seconds() / 60)

        start_str = self._start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        answ = text.dark_aqua("Conduit has been running since ")
        answ += text.aqua(start_str).italic()
        answ += text.dark_aqua(" for a total of ")
        answ += text.dark_aqua(f"{d} days").hover(show_text=text.aqua(f"{uptime_in_days} days")) + ", "
        answ += text.dark_aqua(f"{h} hours").hover(show_text=text.aqua(f"{uptime_in_hours} hours")) + ", "
        answ += text.dark_aqua(f"{m} minutes").hover(show_text=text.aqua(f"{uptime_in_minutes} minutes"))
        
        ctx.reply(answ)


    @plugins.command
    @plugins.checks.has_perm(perms.Builtin.HELPER)
    def setlang(self, ctx: Context, lang: str):
        
        try:
            if self.server.set_lang(lang):
                ctx.success(f"Lang has been changed sucesfully to {lang}!")
                
        except Exception as e:
            ctx.error(e)

    
    @plugins.command(name="reload")
    @plugins.checks.has_perm(perms.Builtin.HELPER)
    def conduit_reload(self, ctx: Context):
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