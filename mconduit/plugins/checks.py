from typing import Optional, TYPE_CHECKING

from ..context import Context
from ..enums import Dimension, Gamemode

if TYPE_CHECKING:
    from .plugin_command import Command    


def in_dimension(dim: Dimension):
    """
    Checks if the player is in the given dimension
    """

    def check_dim(ctx: Context) -> bool:
        return ctx.player.dimension == dim # type: ignore
    
    def decorator(cmd: "Command") -> "Command":
        return cmd.add_check(check_dim)

    return decorator


def in_gamemode(gamemode: Gamemode):
    """
    Checks if the player is in the given gamemode
    """

    def check_gamemode(ctx: Context) -> bool:
        return ctx.player.gamemode == gamemode # type: ignore
    
    def decorator(cmd: "Command") -> "Command":
        return cmd.add_check(check_gamemode)

    return decorator


def is_near(x, y, z, *, radious: int=10):
    """
    Checks if the player is distant less than the radious from the given point.

    Note: to avoid confusion, radious must be passed as keyword argument!
    """

    def check_distance(ctx: Context) -> bool:

        px, py, pz = ctx.player.pos.as_tuple() # type: ignore
        dx = px - x
        dy = py - y
        dz = pz - z

        return dx*dx + dy*dy + dz*dz <= radious*radious
    
    def decorator(cmd: "Command") -> "Command":
        return cmd.add_check(check_distance)

    return decorator


def is_op():
    """
    Checks if the player is opped
    """

    def check_op(ctx: Context) -> bool:
        return ctx.player.name in ctx.server.ops # type: ignore
    
    def decorator(cmd: "Command") -> "Command":
        return cmd.add_check(check_op)

    return decorator


def holds_item(item: str, count: Optional[int]=None):
    """
    Checks if the player holds the given item in it's hand.

    If count is set to None, it will not compare the quantities.

    Note: the prefix `minecraft:` on items is optional!
    """

    if not item.startswith("minecraft:"):
        item = "minecraft:" + item

    def check_hold_item(ctx: Context) -> bool:
        
        selected_item = ctx.player.selected_item # type: ignore
        
        if selected_item is None:
            return False
        
        if count is not None and selected_item.count != count:
            return False
         
        return selected_item.name == item
    
    def decorator(cmd: "Command") -> "Command":
        return cmd.add_check(check_hold_item)

    return decorator


def has_item(item: str):
    """
    Checks if the player contains the given item in it's inventory.

    Note: the prefix `minecraft:` on items is optional!
    """

    if not item.startswith("minecraft:"):
        item = "minecraft:" + item

    def check_has_item(ctx: Context) -> bool:

        for it in ctx.player.inventory.values(): # type: ignore
            
            if it.name == item:
                return True

        return False
    
    def decorator(cmd: "Command") -> "Command":
        return cmd.add_check(check_has_item)

    return decorator