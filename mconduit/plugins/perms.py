from typing import Callable, Union, TYPE_CHECKING

from .plugin_command import Command

if TYPE_CHECKING:
    from ..context import Context


class Permission:
    """
    Permission levels
    """

    Guest  = 0
    User   = 1
    Helper = 2
    Admin  = 3
    Owner  = 4


    @classmethod
    def from_name_or_level(cls, name_or_level: Union[str, int]) -> int:
        
        try:
            return Permission.named(name_or_level)
            
        except:
            try:
                return Permission.of_level(name_or_level)
            except:
                raise KeyError("Permission doesnt exist")


    @classmethod
    def named(cls, name: str) -> int:

        p = name.lower().strip()

        return {
            "guest":  Permission.Guest,
            "user":   Permission.User,
            "helper": Permission.Helper,
            "admin":  Permission.Admin,
            "owner":  Permission.Owner
        }[p]

    
    @classmethod
    def of_level(cls, level: Union[str, int]) -> str:

        p = int(level.strip())

        return {
            0: "Guest",
            1: "User",
            2: "Helper",
            3: "Admin",
            4: "Owner"
        }[p]


def check_perms(permission: Permission) -> Callable:
    """
    This function is meant to be passed directly into the `command` decorator as `check`

    e.g
    ```
    @plugins.command(name="test", checks=[check_perms(plugins.Permission.Helper)])
    def test(self, ctx: Context): ...
    ```
    """

    def check_permission(ctx: "Context") -> bool:
        return ctx.player.permissions >= permission

    return check_permission


def perms(permission: Permission) -> Command:
    """
    A decorator that enables the command only for the specified role and the ones above
    """

    def check_permission(ctx: "Context") -> bool:
        return ctx.player.permissions >= permission

    def decorator(cmd: Command) -> Command:
        return cmd.add_check(check_permission)

    return decorator