"""
This file stores all the version changelogs to be accessed from BuiltinPlugin
"""


CHANGELOGS = {

    "0.1.22": {
        "release_date": "28/08/2025",
        "added": [
            "!!perms",
            "!!news",
            "!!uptime",
            "Event.OnLog",
            "default persistent values"
        ],
        "modified": [
            "table utils (still in progress)",
            "text warn is more clear",
            "reloads plugins when they crash",
            "renamed server.op -> server.ops",
            "files initialization"
        ],
        "fixed": ["command help for subcommands"],
        "removed": []
    },
    "0.1.23": {"release_date": "", "added": [], "modified": [], "fixed": [], "removed": []},
    "0.1.24": {"release_date": "", "added": [], "modified": [], "fixed": [], "removed": []},
    "0.1.25": {"release_date": "", "added": [], "modified": [], "fixed": [], "removed": []},
    "0.1.26": {"release_date": "", "added": [], "modified": [], "fixed": [], "removed": []},
    "0.1.27": {
        "release_date": "06/11/2025",
        "added": [
            "Persistent values are now thread-safe and dont require to call _save() anymore",
            "Full external machine support",
            "New Events",
            "Full support for Json Text 1.21.5+",
            "TextHandler for advanced click events binding",
            "Plugin threads (not finished yet, they will be replaced by processes)",
            "Plugin on_load() method replaced __init__()",
            "Vec3d.normalize()",
            "Vec3d.cross()",
            "Command.__call__()"
        ],
        "modified": [
            "player default perms cache",
            "Persistent class rewritten complitely",
            "server active plugins doesnt raise anymore if doesnt exist but adds its field",
            "removed lots of useless Rcon calls",
            "Click event can run functions (not natively)",
            "Commands now supports unpack operator",
            "PluginManager.load_all_plugins() doesnt raise anymore",
            "PluginCatalogue doesnt print all the traceback anymore if connection is lost",
            "Command docstring cleaned and more clear (will be improved further)",
            "BuiltinPlugin new command improved (BuiltinPlugin will be improved further)"
        ],
        "fixed": [
            "Update plugin notify doesnt crash anymore",
            "Lots of errors regarding Persistent values",
            "Entity.forward_vec is more precise"
        ],
        "removed": []
    },
    "0.1.28": {
        "release_date": "30/12/2025",
        "added": [
            "Plugin.path",
            "utils.scoreboards.get_score()",
            "Event.PlayerTrigger",
            "utils.errors (ConduitError & get_last_error())",
            "utils.gamerules.get_gamerule_value()",
            "text.button(), .link(), .suggester(), .quoted(), .endl(), .pixel_len()",
            "utils.coords.ow_to_nether() | chunk_coords",
            "Permission utility methods",
            "Vec3d.__hash__()",
            "Command.fallback",
            "PersistentList.insert()",
            "Package plugins entrypoint warn"
            ],
        "modified": [
            "Improved UI/UX",
            "BuiltinPlugin and PluginManager refactoring with newer API",
            "plugin download/load/unload/reload now prints confirm to everyone",
            "Every player can now trigger Event.TextClicked (and not just opped ones)",
            "Text now replaces bad quotes inside the text in order to avoid errors"
            "Renamed `utils.coords_fix` to `utils.coords`",
            "Renamed `coords_fix()` to `approx_fix()` in utils.coords",
            "Server.tellraw `at` parameter now accepts `Player` type too",
            "Plugin.get_command_named() now supports subcommands too"
            ],
        "fixed": [
            "!!news prints everything in batches to avoid Rcon failure",
            "Plugin unload doesnt cause AttributeError anymore (happened sometimes)",
            "Text.hover now supports Text type values for show_text action",
            "Text.to_json() now specifies color even if the color is White",
            "TextHandler.bind_text() doesnt raise if the first text bit doesnt have click but other do",
            "Text.to_json() separates styles, colors and events from other chunks added later",
            "Server.tellraw() now splits the text if the command its too long",
            "@a and @p were swapped",
            "Package plugins now reloads correctly",
            "PluginCatalogue doesnt raise anymore if handler.cli is not initialized yet"
            ],
        "removed": [
            "Command.__call__()"
        ]
    },
    "0.1.29": {
        "release_date": "31/12/2025",
        "added": [
            "PluginManager._fetch_plugin_metadata()",
            "Server.playsound(), .stopsound()",
            "Conduit plays conduit.activate sound to everyone when loads correctly"
        ],
        "modified": [
            "PluginManager._try_update_plugin() now uses server.tellraw()"
        ],
        "fixed": [
            "Context.say() now calls server.tellraw()",
            "@p and @p swaped again (i have no idea why this was done in the first place)",
            "PluginManager.download_plugin() doesnt raise anymore",
            "ConduitError.to_text() now dedents the exception documentation",
            "Text.to_json() bug converting Text in `show_text` hover-event",
            "Entity.pos/rot/mition/forward_vec dont raise anymore if Rcon fails",
            "!!help text now prints correctly"
        ],
        "removed": []
    },
    "0.3.0": {
        "release_date": "28/03/2026",
        "added": [
            "Text.click() change_page action type",
            "_Types.Coordinate & relative()",
            "enums.At.Selector",
            "sound subpackage",
            "sounds mappings",
            "resource_pack creation support",
            "ServerApi.resource_pack, .resource_pack_url, .require_resource_pack, .properties",
            "threading.RLock to PluginManager for safety",
            "utils.color.hex_to_rgb(), .rgb_to_hex()",
            "Handler.version",
            "Welcome screen",
            "Setup wizard",
            "Server download (vanilla)",
            "(Server) Properties",
            "Rcon config sync",
            "Telemetry",
            "ConduitError.__eq__()",
            "json subpackage (Serializable, Field)",
            "text.__deepcopy__",
            "Vec3d.__copy__(), .copy(), up(), .down()",
            "Plugin.on_plugin_ loaded(), unloaded(), reloaded(), downloaded()",
            "Plugin.logger",
            "world subpackage (world reading API)"
        ],
        "modified": [
            "Text.<any_color>() changes the color everywhere and not just at the first bit",
            "_types.Message is now a TypeAlias",
            "Conduit logo is now printed with a gradient",
            "Vec3d division and product now support a Vec3d too",
            "Vec3d.__init__() now has default values (0, 0, 0)",
            "Codebase cleaned/refactored",
            "Plugin about_to_stop() -> on_unload()"
        ],
        "fixed": [
            "EntityDataFetcher doesnt raise with invalid entity identifier",
            "Context.say() now sends messages to @a instead of @p",
            "ServerAPI.__change_data doesnt mess-up anymore when property is not set",
            "Corrupted .offset files are now recreated",
            "Event.SubScoreboardValue doesnt create a context with Event.SetScoreboardValue anymore",
            "Package plugins are not correctly loaded/unloaded/reloaded",
            "utils.scoreboards.get_latest_trigger_id now returns 0 instead of None",
            "Text.__radd__() now builds the next correctly",
            "Color.LigthPurple -> Color.LightPurple in all API",
            "Text doesnt raise anymore when deep-copied",
            "Rot.__repr__ doesnt raise AttributeError anymore",
            "*Some* mypy errors"
        ],
        "removed": [
            "ServerRunnerConfig.name (only.names now is supported)"
        ]
    },
    "0.4.0": {
        "release_date": "04/08/2026",
        "added": [
            "Plugin download can be forced",
            "!!version list",
            "Version, VersionCheck",
            "Server.version",
            "Server.online_players",
            "conduit_version field on plugin metadata",
            "--force flag in plugin download command",
            "perms package",
            "Context.notify() and notify_success()",
            "Server download (fabric)",
            "utils.debug() and Plugin.debug()",
            "Cli.out() now prints Text with colors & styles",
            "Server.save_all(), .save_all_flush()",
            "*Some* tests to ensure everything is safer and reliable",
            "WorldSnapshot",
            "Block.name property and other utility methods",
            "Vec3d.__rmul__()",
            "Every server has its own separate plugin config now",
            "Server.get_all_joined_players()",
            "Server.get_player_named()",
            "Server.online_players",
            "scoreboard subpackage",
            "Server.world, .overworld .nether .end properties",
            "Server.teams, scoreboards, objectives, display_slots",
            "Player.team, .display_name, __eq__()"
        ],
        "modified": [
            "plugin dependencies -> python_dependencies in metadata.json",
            "plugin finish its download even if its dependencies arent installed",
            "improved BuiltinPlugin",
            "plugin update notify complitely redone",
            "utils.version_checker -> version",
            "Server.get_online_players() -> fetch_online_players()",
            "Player.inventory and .echest_inventory works with complex items too",
            "Command.CastError now raises a useful message",
            "Better CLI help message",
            "CLI now runs on background",
            "Lang parameters must be passed via f-string now",
            "permission system has been redesigned completely",
            "plugin persistent & config binding",
            "Rcon errors are now not displayed by default",
            "CachedWorldReader.clean_cache() -> clear_cache() and it's also faster",
            "TextHandler now calls fetch_latest_trigger_id() only at initialization, making bind_text() a lot faster!",
            "Improved errors informations (a bit more concise now)",
            "Improved CLI colors and completions",
            "Player.is_sneaking() is now a method and not a property",
            "Renamed all the enums values from camel-case to sneak-case",
            "Removed most of the name-mangling variables",
            "Restructured Server classes",
            "EntityDataFetcher now caches everything and its a lot faster",
            "Player.spawn_pos -> respawn_pos, .spawn_dimension -> respawn_dimension"
        ],
        "fixed": [
            "help command failed with parameters",
            "*Some* mypy errors",
            "External prints doesnt mess up with user typing in CLI anymore",
            "Selector() is not modificated anymore",
            "utils.color.rgb_to_hsv() prevents divisions by 0 now",
            "Text.to_json() doesnt mutate text internal state anymore",
            "Chunk.get_height() was incorrect",
            "Context. info(), warn(), error(), success() now colors all the text and not just the first bit",
            "PluginManager now unloads the plugin-package if the plugin didnt load correctly",
            "Player.spawn_pos and .spawn_dimension fetched incorrect data",
            "text.icon.three was mispelled (tree)"
        ],
        "removed": [
            "PluginCatalogue.skipped_updates"
        ]
    }
}