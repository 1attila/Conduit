# Conduit 0.2.0:

## Release date:
*27/03/2026*

## Added

- Text.click() change_page action type
- _Types.Coordinate & relative()
- enums.At.Selector
- sound subpackage
- sounds mappings
- resource_pack creation support
- ServerApi.resource_pack, .resource_pack_url, .require_resource_pack, .properties
- threading.RLock to PluginManager for safety
- utils.color.hex_to_rgb(), .rgb_to_hex()
- Handler.version
- Welcome screen
- Setup wizard
- Server download (vanilla)
- (Server) Properties
- Rcon config sync
- Telemetry
- ConduitError.__eq__()
- json subpackage (Serializable, Field)
- text.__deepcopy__
- Vec3d.__copy__(), .copy(), up(), .down()
- Plugin.on_plugin_ loaded(), unloaded(), reloaded(), downloaded()
- Plugin.logger
- world subpackage (world reading API)

## Modified:
      
- Text.<any_color>() changes the color everywhere and not just at the first bit
- _types.Message is now a TypeAlias
- Conduit logo is now printed with a gradient
- Vec3d division and product now support a Vec3d too
- Vec3d.__init__() now has default values (0, 0, 0)
- Codebase cleaned/refactored
- Plugin about_to_stop() -> on_unload()

## Fixed:
        
- EntityDataFetcher doesnt raise with invalid entity identifier
- Context.say() now sends messages to @a instead of @p
- ServerAPI.__change_data doesnt mess-up anymore when property is not set
- Corrupted .offset files are now recreated
- Event.SubScoreboardValue doesnt create a context with Event.SetScoreboardValue anymore
- Package plugins are not correctly loaded/unloaded/reloaded
- utils.scoreboards.get_latest_trigger_id now returns 0 instead of None
- Text.__radd__() now builds the next correctly
- Color.LigthPurlple -> Color.Light in all API
- Text doesnt raise anymore when deep-copied

## Removed:

- ServerRunnerConfig.name (only.names is now supported)