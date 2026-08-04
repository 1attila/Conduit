from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING
import threading
import logging
import json
import os

from mconduit.perms.perm import P
from mconduit.perms.item import PermissionItem
from mconduit.constants import PERMS_FILE
from mconduit._types import Player

if TYPE_CHECKING:
    from mconduit.handler import Handler


logger = logging.getLogger(__name__)


class PermissionStorage:
    """
    Stores all the permissions for all the servers.

    This should be constructed ONLY by the manager
    """

    
    _handler: Handler
    _lock: threading.RLock
    _data: Dict[str, Dict[str, List[str]]] # {server-name -> {perm-item-name -> players}}


    def __init__(
        self,
        handler: Handler
    ) -> None:

        self._handler = handler
        self._lock = threading.RLock()
        self._data = {}


    def get_server_perms(self, server: str) -> Dict[str, List[str]]:

        try:
            return dict(self._data[server])
        
        except KeyError:
            return {}
        
    
    def get_players_with_perm(
        self,
        server: str,
        permission: PermissionItem | str
    ) -> List[Player]:

        if isinstance(permission, PermissionItem):
            permission = permission.name

        s = self._handler.get_server_named(server)

        if s is None:
            return []
        
        return [Player(p, s) for p in self.get_server_perms(server).get(permission, [])]


    def get_player_perms(
        self,
        server: str,
        player: Player | str
    ) -> List[str]:

        if isinstance(player, Player):
            player = player.name
        
        perms = []
        
        for p_name, players, in self.get_server_perms(server).items():

            if player in players:
                perms.append(p_name)
        
        return perms
    

    def add_perm(
        self,
        server: str,
        player: str,
        permission: PermissionItem | str
    ) -> None:

        if isinstance(permission, PermissionItem):
            permission = permission.name
        
        perm: list[str] = self._data.setdefault(server, {})\
            .setdefault(permission, [])

        if player not in perm:

            perm.append(player)
            self.save()
        

    def remove_perm(
        self,
        server: str,
        player: str,
        permission: PermissionItem | str
    ) -> None:

        if isinstance(permission, PermissionItem):
            permission = permission.name
        
        perm: list[str] = self._data.setdefault(server, {})\
            .setdefault(permission, [])

        if player in perm:

            perm.remove(player)
            self.save()


    def load(self) -> None:

        with self._lock:

            self._data = {}

            if not PERMS_FILE.exists():
                
                PERMS_FILE.parent.mkdir(parents=True, exist_ok=True)
                PERMS_FILE.write_text("{}")

            with PERMS_FILE.open("r", encoding="utf-8") as f:

                try:
                    self._data = json.load(f)

                except Exception as e:

                    self._data = {}
                    logger.error(f"Unable to load permission file: {e}")

    
    def save(self) -> None:
        
        with self._lock:
                
            if not PERMS_FILE.exists():
                PERMS_FILE.parent.mkdir(parents=True, exist_ok=True)

            temp_path = PERMS_FILE.with_suffix(".tmp")

            with open(temp_path, "w") as f:

                json.dump(self._data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, PERMS_FILE)