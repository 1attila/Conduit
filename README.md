![ConduitLogo](https://raw.githubusercontent.com/1attila/Conduit/master/logo/Assets/Conduit1_long.png)
# Conduit
A Minecraft tool that runs above the server with APIs to fetch useful datas, edit properties and run commands

I just put all this together in less than a week, so it doesn't contain that much stuff and it's kinda uselsss rigth now, horewer it should be a solid base for the future.

Don't use this yet, horewer i will be glad if you could check the code and give suggestions about:
- Security: you shouldnt get data that is supposed to remain private (e.g. Rcon password)
- Features
- Api style
- Implementation
- Project structure


## Main Features
- ServerRunner: runs the server process and handles I/O. In the future it will handles events aswell
- FetchingAPI: is able to fetch intresting information (e.g online_players)
- Edit some server attributes: (e.g. whitelist, motd, view-distance, etc). This is done if a specific flag is set to true (false by default) 
- CommandsAPI: ability to run every command via Rcon
- Cli: Simple cli with the ability to execute commands from the servers, read and edit some server propetiers directly from the console
- Languages: supports multiple languages. Main language can be set in the server config.json file.
- Security: servers configs are designed to don't leak any private information (e.g. Rcon password). This will be really useful when plugins will be implemented.

## Future Features
- Event system: all the events are already present in Handler and Server class but they are not implemented yet
- Minecraft Json text: Like MCDReforged RText library
- Plugins: Like MCDReforged plugins
- More fetching
- More commands
- Supports multiple server types (e.g bukket, bungeecord, etc)

## How to run/use:
- Setup a classic minecraft server
- Clone/download the repo into a folder above the server folder
- Setup config.json
- Open a command prompt and run python main.py into the Conduit folder (This should start the servers processes and displaying all their output on the console)

## Credits
- MCDaemon: Run server process with Popen
- MCDReforged: General inspiration and features ideas
- MinecraftWiki: server properties and other knowledge
