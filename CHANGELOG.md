# Conduit 0.4.0:

## Release date:
*04/08/2026*

## Added:

- Plugin download can be forced
- !!version list
- Version, VersionCheck
- Server.version
- Server.online_players
- conduit_version field on plugin metadata
- --force flag in plugin download command
- perms package
- Context.notify() and notify_success()
- Server download (fabric)
- utils.debug() and Plugin.debug()
- Cli.out() now prints Text with colors & styles
- Server.save_all(), .save_all_flush()
- *Some* tests to ensure everything is safer and reliable
- WorldSnapshot
- Block.name property and other utility methods
- Vec3d.__rmul__()
- Every server has its own separate plugin config now
- Server.get_all_joined_players()
- Server.get_player_named()
- Server.online_players
- scoreboard subpackage
- Server.world, .overworld .nether .end properties
- Server.teams, scoreboards, objectives, display_slots
- Player.team, .display_name, __eq__()

## Modified:
- plugin dependencies -> python_dependencies in metadata.json
- plugin finish its download even if its dependencies arent installed
- improved BuiltinPlugin
- plugin update notify complitely redone
- utils.version_checker -> version
- Server.get_online_players() -> fetch_online_players()
- Player.inventory and .echest_inventory works with complex items too
- Command.CastError now raises a useful message
- Better CLI help message
- CLI now runs on background
- Lang parameters must be passed via f-string now
- permission system has been redesigned completely
- plugin persistent & config binding
- Rcon errors are now not displayed by default
- CachedWorldReader.clean_cache() -> clear_cache() and it's also faster
- TextHandler now calls fetch_latest_trigger_id() only at initialization, making bind_text() a lot faster!
- Improved errors informations (a bit more concise now)
- Improved CLI colors and completions
- Player.is_sneaking() is now a method and not a property
- Renamed all the enums values from camel-case to sneak-case
- Removed most of the name-mangling variables
- Restructured Server classes
- EntityDataFetcher now caches everything and its a lot faster
- Player.spawn_pos -> respawn_pos, .spawn_dimension -> respawn_dimension

## Fixed:
- help command failed with parameters
- All mypy errors
- External prints doesnt mess up with user typing in CLI anymore
- Selector() is not modificated anymore
- utils.color.rgb_to_hsv() prevents divisions by 0 now
- Text.to_json() doesnt mutate text internal state anymore
- Chunk.get_height() was incorrect
- Context. info(), warn(), error(), success() now colors all the text and not just the first bit
- PluginManager now unloads the plugin-package if the plugin didnt load correctly
- Player.spawn_pos and .spawn_dimension fetched incorrect data
- text.icon.three was mispelled (tree)

## Removed:
- PluginCatalogue.skipped_updates