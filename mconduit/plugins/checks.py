from __future__ import annotations
from typing import TypeVar, Callable, Union, Optional, Any, TYPE_CHECKING

from mconduit.plugins.plugin_command import Command, CommandFunc
from mconduit.context import Context
from mconduit.enums import Dimension, Gamemode
from mconduit.perms.perm import Permission

if TYPE_CHECKING:
    from mconduit.context import Context    
    from mconduit.perms.item import PermissionItem


PermT = TypeVar("PermT", bound=Permission)
CheckDecorator = Union[Command, Any]
CheckPredicate = Callable[["Context"], bool]


def create_check(
    check_predicate: CheckPredicate
) -> Callable[[CheckDecorator], CheckDecorator]:
    """
    Creates the proper decorator
    """

    def decorator(cmd: CheckDecorator) -> CheckDecorator:

        if isinstance(cmd, Command):
            return cmd.add_check(check_predicate)
        
        else: # Callable

            if not hasattr(cmd, "_checks"):
                setattr(cmd, "_checks", [])
            
            getattr(cmd, "_checks", []).append(check_predicate)

            return cmd

    return decorator


def has_perms(*permissions: PermT | PermissionItem | str) -> Callable[[CheckDecorator], CheckDecorator]:
    """
    Checks if the player has the given permissions
    """

    def check_perms(ctx: Context) -> bool:

        for permission in permissions:

            assert ctx.player is not None

            if not ctx.server.permission_manager.has_permission(ctx.player, permission):
                return False

        return True
    
    return create_check(check_perms)


def has_perm(permission: PermT | PermissionItem | str) -> Callable[[CheckDecorator], CheckDecorator]:
    """
    Checks if the player has the given permission
    """

    return has_perms(permission)


def in_dimension(dim: Dimension) -> Callable[[CheckDecorator], CheckDecorator]:
    """
    Checks if the player is in the given dimension
    """

    def check_dim(ctx: Context) -> bool:
        return ctx.player.dimension == dim # type: ignore

    return create_check(check_dim)


def in_gamemode(gamemode: Gamemode) -> Callable[[CheckDecorator], CheckDecorator]:
    """
    Checks if the player is in the given gamemode
    """

    def check_gamemode(ctx: Context) -> bool:
        return ctx.player.gamemode == gamemode # type: ignore

    return create_check(check_gamemode)


def is_near(
    x, y, z,
    *, radious: int = 10
) -> Callable[[CheckDecorator], CheckDecorator]:
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

    return create_check(check_distance)


def is_op() -> Callable[[CheckDecorator], CheckDecorator]:
    """
    Checks if the player is opped
    """

    def check_op(ctx: Context) -> bool:
        return ctx.player.name in ctx.server.ops # type: ignore

    return create_check(check_op)


def holds_item(
    item: str,
    count: Optional[int] = None
) -> Callable[[CheckDecorator], CheckDecorator]:
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

    return create_check(check_hold_item)


def has_item(item: str) -> Callable[[CheckDecorator], CheckDecorator]:
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

    return create_check(check_has_item)