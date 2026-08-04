from typing import TypeVar, Iterable, Any
import enum

from mconduit.perms.item import PermissionItem


class Permission(enum.Enum):
    """
    Permission schema, each value must be a `PermissionItem`

    You can override:

    • `DEFAULT`: defalt permission (`None` by default)

    • `RESOLVER`: responsable of handling permission check
    
    Example:
    ```
    class MyPerms(perms.Permission):
    
        TRADER   = perm_item("trader")
        VILLAGER = perm_item("trader")

        DEFAULT  = perm_item("trader")
        RESOLVRE = perm.PermissionResolver # Default value
    ```

    Or look at `Builtin` permissions for an example of hierarchical perms
    """

    #RESOLVER: Type[R] = PermissionResolver
    #DEFAULT: Optional[PermissionItem] = None

    value: PermissionItem
    

P = TypeVar("P", bound=Permission)