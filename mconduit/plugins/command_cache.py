from typing import List, TYPE_CHECKING
from pathlib import Path
import json

if TYPE_CHECKING:
    from ..context import Context


MAX_COMMAND_SUGGESTION = 5
COMMAND_CACHE_FILE = "command_cache.json"


class CommandCache:
    """
    Player command cache.

    Holds the last 5 commands sent for each player to suggest them when needed
    """

    def __init__(self) -> None:

        if not Path(COMMAND_CACHE_FILE).exists():
            
            with open(COMMAND_CACHE_FILE, "x") as f:
                f.write("{\n}")
                

    def get_last_commands(self, ctx: "Context") -> List[List[str]]:
        """
        Returns the latest 5 commands sent by the player
        """
        
        with open(COMMAND_CACHE_FILE) as f:
            
            cache = json.load(f)
            return cache.get(ctx.player.name, []) # type: ignore
        
    
    def update(
        self,
        ctx: "Context",
        command_args: List[str],
        command_flags: List[str]
    ) -> None:
        """
        Updates the player command cache

        If the player command list len is 5 the list item will be removed
        """

        with open(COMMAND_CACHE_FILE) as f:
            try:
                cache = json.load(f)

            except Exception as e:
                print("Problem while reading command_cache.json", e)
                cache = {}
            player_commands = list(cache.get(ctx.player.name, [])) # type: ignore
            
        command_args.extend(command_flags)

        if command_args in player_commands:
            
            command_index = player_commands.index(command_args)
            player_commands.pop(command_index)
            
        elif len(player_commands) >= MAX_COMMAND_SUGGESTION:
            player_commands.pop(0)

        player_commands.append(command_args)
        
        cache[ctx.player.name] = player_commands # type: ignore

        try:
            new_cache = json.dumps(cache, indent=4)
        
        except Exception as e:
            print("Unable to de-serialize the command_cache", e)
            return
            
        with open(COMMAND_CACHE_FILE, "w") as f:
            f.write(new_cache)