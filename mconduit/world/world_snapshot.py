from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
import shutil
import time

if TYPE_CHECKING:
    from mconduit.server_api import ServerAPI


class WorldSnapshot:
    """
    Manages a world copy in a separate folder to avoid concurrency errors with Minecraft.
    """

    _server: ServerAPI
    _original_world_path: Path
    _new_path: Path
    _latest_world_save_time: float
    _save_intervals_delay: int
    _counter: int


    def __init__(
        self,
        server: ServerAPI,
        save_intervals_delay: int = 30
    ) -> None:

        self._server = server

        world_name = server.properties.get("level-name", "world")
        self._original_world_path = server.path / world_name

        self._world_path = server.path / "world-copy" / world_name
        self._latest_world_save_time = -1

        self._save_intervals_delay = save_intervals_delay
        self._counter = 0

        self.sync_world_copy()


    @property
    def world_path(self) -> Path:
        return self._world_path


    @property
    def latest_world_save_time(self) -> float:
        return self._latest_world_save_time


    @property
    def data_version(self) -> int:
        return self._server.world.data_version # Crazy workaround, ik


    def sync_world_copy(self) -> None:
        """
        Copies everything inside server-path/<world-name> into server-path/world-copy/<world-name>
        """

        shutil.copytree(
            self._original_world_path,
            self._world_path, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("session.lock")
        )
        self._latest_world_save_time = time.time()

    
    def tick_save(self) -> None:
        """
        Saves the world every (_save_intervals_delay * 10) seconds (this is called every 10 seconds tho)
        """

        if self._counter % self._save_intervals_delay == 0:
            self._server.save_all()

        self._counter += 1