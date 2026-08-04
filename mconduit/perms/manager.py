from __future__ import annotations
from typing import Generic, Dict, List, Union, Type, Any, TYPE_CHECKING

from mconduit.perms.builtin import Builtin
from mconduit.perms.perm import Permission
from mconduit.perms.item import PermissionItem
from mconduit.perms.resolver import PermissionResolver, R
from mconduit._types.player import Player

if TYPE_CHECKING:

    from mconduit.perms.storage import PermissionStorage
    from mconduit.perms.perm import P

    from mconduit.server import Server


class NameConflictError(Exception):
    """
    Permission name(s) are already used
    """


class MissingResolverError(Exception):
    """
    The permission class doesnt have a resolver
    """


class PermissionNotFoundError(Exception):
    """
    The permission specified does not exist
    """


class PermissionManager:
    """
    Handles permission storage and assigning.

    This be constructed ONLY by the server
    """


    _server: Server
    _perms: Dict[Type[Permission], PermissionResolver[Any]]
    _item_to_resolver: Dict[str, PermissionResolver[Any]]
    _all_perm_items: List[str]


    def __init__(
        self,
        server: Server
    ) -> None:
        
        self._server = server
        self._perms = {}
        self._item_to_resolver = {}
        self._all_perm_items = []

        self.load_perm(Builtin)


    @property
    def storage(self) -> PermissionStorage:
        return self._server.handler.permission_storage
    

    def load_perm(
        self,
        perm: Type[P]
    ) -> None:

        if perm in self._perms.values():
            return
        
        self._assert_name_conflicts(perm)

        resolver_cls = self._find_and_load_resolver(perm)
        resolver_inst = resolver_cls(self, perm)

        self._perms[perm] = resolver_inst

        for item in perm:

            p: PermissionItem | PermissionResolver = item.value

            if isinstance(p, PermissionItem):

                self._all_perm_items.append(p.name)
                self._item_to_resolver[p.name] = resolver_inst

    
    @property
    def perms(self) -> Dict[str, List[str]]:

        return self.storage.get_server_perms(self._server.name)
        
    
    def get_players_with_perm(
        self,
        permission: PermissionItem | str
    ) -> List[Player]:

        return self.storage.get_players_with_perm(self._server.name, permission)


    def get_player_perms(
        self,
        player: str
    ) -> List[str]:
        
        return self.storage.get_player_perms(self._server.name, player)
    

    def add_perm(
        self,
        player: str,
        permission: PermissionItem | str
    ) -> None:
        
        self.storage.add_perm(self._server.name, player, permission)
        

    def remove_perm(
        self,
        player: str,
        permission: PermissionItem | str
    ) -> None:
        
        self.storage.remove_perm(self._server.name, player, permission)


    def has_permission(
        self,
        player: Union[str, Player],
        permission: Permission | PermissionItem | str
    ) -> bool:
        """
        Determines if the given player has the given permission
        """

        if isinstance(permission, Permission):
            permission = permission.value

        if isinstance(permission, PermissionItem):
            permission = permission.name
        
        resolver = self._item_to_resolver.get(permission)

        if resolver is None:
            raise PermissionNotFoundError
        
        return resolver.has_permission(player, permission)


    def _assert_name_conflicts(
        self,
        perm: Type[P]
    ) -> None:
        
        name_conflicts: List[bool] = []

        for item in perm:

            p: PermissionItem | PermissionResolver = item.value

            try:
                if issubclass(p, PermissionResolver): # type: ignore
                    continue
            except TypeError:
                pass

            name_conflicts.append(p.name in self._all_perm_items) # type: ignore

        if all(name_conflicts):

            # It's fine, the plugin that had this permission just got reloaded
            return

        if any(name_conflicts): # There are actual conflicts

            for item in perm:

                p = item.value

                if p.name in self._all_perm_items:
                    raise NameConflictError(f"Permission item: {p.name} of {perm}")


    def _find_and_load_resolver(
        self,
        perm: Type[P]
    ) -> Type[PermissionResolver[Any]]:

        for item in perm:

            p: PermissionItem | PermissionResolver = item.value

            try:
                if issubclass(p, PermissionResolver): # type: ignore
                    return p # type: ignore

            except TypeError:
                pass

        return PermissionResolver