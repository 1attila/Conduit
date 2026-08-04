from __future__ import annotations
from typing import Optional, Union, List, TYPE_CHECKING

from mconduit.base_server import BaseServer
from mconduit.enums import Selector, Difficulty, Gamemode, SoundType
from mconduit._types import Message, Player, Vec3d, Coordinate, relative
from mconduit.text import Text, Table

if TYPE_CHECKING:
    from mconduit.server_runner import ServerRunner

class ServerCommandsAPI(BaseServer):
    """
    Server commands container

    They are all grouped here for redability
    """


    def __init__(
        self,
        runner: ServerRunner
    ) -> None:
        super().__init__(runner)


    # Comunication

    def say(
        self,
        msg: Union[str, Text, Table]
    ) -> None:
        """
        Equivalent to `tellraw(@a, msg)`
        """

        self.tellraw("@a", msg)


    def tellraw(
        self,
        at: Union[Selector, Player, str],
        msg: Union[str, Text, Table]
    ) -> None:
        """
        Advanced tellraw method.

        Messages supported are:
        - strings
        - Text
        - Table

        This function is also responsable to bind the `run_function` click_event
        """
        
        if isinstance(at, Player):
            at = at.name
        
        if isinstance(msg, Table):
            
            for item in msg.draw():
                self.tellraw(at, item)
        
        elif isinstance(msg, str):
            self.execute(f"""/tellraw {at} {{"text": "{msg}"}}""")

        else:

            text: Text = self._text_handler.bind_text(msg) # type: ignore
            assert isinstance(text, Text) # cuz mypy complains
            
            temp_text = text.__str__(self.is_v1_21_5) # type: ignore
            
            if len(temp_text) > 1400:

                texts = text._split()
                
                with self.all_at_once():

                    for text in texts:
                        
                        text = text.__str__(self.is_v1_21_5) # type: ignore
                        self.execute(f"/tellraw {at} {text}")

                return
            
            self.execute(f"/tellraw {at} {temp_text}")

        return None

    def team(self):
        ...

    # def whitelist(self):
    #     ...

    def kick(self):
        ...

    def ban(self):
        ...

    def ban_ip(self):
        ...

    def pardon(self):
        ...

    def pardon_ip(self):
        ...

    def op(self, player: Union[str, Player]):
        ...

    def deop(self, player: Union[str, Player]):
        ...

    # Player action

    # def gamemode(self):
    #     ...

    # Entity interactions

    def summon(self):
        ...

    def kill(self):
        ...

    def tp(self):
        ...

    def rotate(self):
        ...

    def ride(self):
        ...

    def give(self):
        ...

    def enchant(self):
        ...

    def effect(self):
        ...

    def xp(self):
        ...

    def damage(self):
        ...

    def particle(self):
        ...
    
    def playsound(
        self,
        sound: str,
        *,
        type: SoundType = SoundType.AMBIENT,
        at: Selector | Player | str = "@a",
        coords: Optional[Coordinate] = None,
        volume: float = 1,
        pitch: float = 1,
        min_volume: float = 0
    ) -> None:

        if isinstance(at, Player):
            at = at.name
        
        coord_needed = volume != 1 or pitch != 1 or min_volume != 0

        if (
            (coords is None and coord_needed) or
            str(at).startswith(("@a", "@e"))
        ):
            
            if str(at).startswith(("@a", "@e")):
                
                for player in self.online_players.values():
                    
                    cmd = self._make_playsound_command(
                        sound=sound,
                        type=type,
                        at=player.name,
                        coords=player.pos,
                        volume=volume,
                        pitch=pitch,
                        min_volume=min_volume
                    )
                    self.execute(f"execute at {player} run {cmd}")
            else:

                cmd = self._make_playsound_command(
                    sound=sound,
                    type=type,
                    at=at,
                    coords=relative(),
                    volume=volume,
                    pitch=pitch,
                    min_volume=min_volume
                )

                self.execute(f"execute at {at} run {cmd}")
        
        else:

            assert coords is not None

            self.execute(
                self._make_playsound_command(
                    sound=sound,
                    type=type,
                    at=at,
                    coords=coords,
                    volume=volume,
                    pitch=pitch,
                    min_volume=min_volume
                )
            )

        
    def _make_playsound_command(
        self,
        sound: str,
        *,
        type: SoundType,
        at: Selector | str,
        coords: Coordinate = "~ ~ ~",
        volume: float = 1,
        pitch: float = 1,
        min_volume: float = 0
    ) -> str:
        """
        This is an utility function to fill all the default values when needed

        Example:
        playsound(ui.button.click, ambient, pitch=0.5)
        -> `playsound ui.button.click ambient at ~ ~ ~ 1 0.5`
        """
        
        command = f"playsound {sound}"

        params = [type, at, coords, volume, pitch, min_volume]
        required = [
            type       != "master",
            at         not in ["@a", "@e"],
            isinstance(coords, str) and coords     != "~ ~ ~",
            volume     != 1,
            pitch      != 1,
            min_volume != 0,
        ]
        
        params.reverse()
        required.reverse()
        params_to_pass: List[str] = []
        required_flag = False

        for p, r in zip(params, required):
            
            required_flag = required_flag or r

            if required_flag is True:
                params_to_pass.append(str(p))

        if len(params_to_pass) > 0:

            params_to_pass.reverse()
            command += " " + " ".join(params_to_pass)
        
        return command

    
    def stopsound(
        self,
        at: str | Selector,
        sound: str,
        type: SoundType = SoundType.AMBIENT
    ) -> None:
        self.execute(f"/stopsound {at} {type} {sound}")
    

    def scoreboard(self):
        ...

    # World interactions

    def time(self):
        ...

    def setblock(self):
        ...

    def fill(self):
        ...

    def loot(self):
        ...


    def save_all(
        self,
        flush: bool = False
    ) -> None:
        """
        Saves everything to the data storage.

        If flush is `True`, chunks are saved immediately, causing the server to freeze shortly.

        Things that are saved:

        - Chunks
        - Entities
        - Scoreboards / objectives / teams
        """

        if flush is True:

            self.save_all_flush()
            return
        
        self.execute("save-all")


    def save_all_flush(self) -> None:
        """
        Equivalent to `save_all(True)`
        
        NOTE: This causes the server to freeze shortly.
        
        If you want to save everything not immediately go for `save_all()`
        """

        self.execute("save-all flush")