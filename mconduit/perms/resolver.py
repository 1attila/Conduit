from __future__ import annotations
from typing import Optional, Generic, Type, TypeVar, List, Union, TYPE_CHECKING

from mconduit.perms.item import PermissionItem

if TYPE_CHECKING:
    from mconduit.perms.manager import PermissionManager
    from mconduit.perms.perm import Permission
    from mconduit._types.player import Player


P = TypeVar("P", bound="Permission")


class PermissionResolver(Generic[P]):
    """
    Base class that implements logic to determine if a player has a certain permission or not
    """


    def __init__(
        self,
        manager: PermissionManager,
        perm: Type[P]
    ) -> None:
        
        self.manager = manager
        self.perm = perm

    
    def has_permission(
        self,
        player: Union[str, Player],
        permission: PermissionItem | str
    ) -> bool:
        
        if isinstance(permission, PermissionItem):
            permission = permission.name

        player_perms = self.manager.get_player_perms(str(player))

        if permission in player_perms:
            return True

        default: Optional[PermissionItem] = getattr(self.perm, "DEFAULT", None)

        if default is None:
            return False

        return permission == default.name


class HierarchicalPermissionResolver(PermissionResolver):
    """
    Determine if a player has a certain permission or not.

    Used for Hierarchical permissions: top has lowest permission while bottom has highest
    """


    values: List[str]


    def __init__(
        self,
        manager: PermissionManager,
        perm: Type[P]
    ) -> None:
        
        super().__init__(manager, perm)

        self.values = []

        for item in perm:
            
            p = item.value

            if isinstance(p, PermissionItem):
                self.values.append(p.name)

    
    def has_permission(
        self,
        player: Union[str, "Player"],
        permission: PermissionItem | str
    ) -> bool:

        if isinstance(permission, PermissionItem):
            permission = permission.name
        
        assert permission in self.values
        
        player_perms = [p for p in self.manager.get_player_perms(str(player)) if p in self.values]

        if len(player_perms) == 0:

            default: Optional[PermissionItem] = getattr(permission, "DEFAULT", None)

            if default is None:
                return False

            player_perms = [default.name]
        
        max_perm = max(player_perms, key = lambda p: self.values.index(p))

        return self.values.index(max_perm) >= self.values.index(permission)
        

R = TypeVar("R", bound=PermissionResolver)