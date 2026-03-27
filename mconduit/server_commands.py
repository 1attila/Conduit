# type: ignore

from typing import Optional, Union, TYPE_CHECKING

from .utils.rcon import Rcon
from .utils.scoreboards import generate_text_scoreboard, TextScoreboardTracker
from .enums import At, Difficulty, Gamemode
from ._types import Message, Player, Vec3d, Coordinate, relative
from .text import Text, Table

if TYPE_CHECKING:
    from .conduit_config import ServerRunnerConfig


class ServerCommandsAPI:
    """
    Server commands container

    They are all grouped here for redability
    """

    
    __rcon: Rcon # Initialized from Server
    

    def init(
        self,
        config: "ServerRunnerConfig",
        rcon: Rcon
    ) -> None:
        
        self.__rcon = rcon


    # Comunication

    def say(
        self,
        msg: Union[str, Text, Table]
    ):
        """
        Equivalent to `tellraw(@a, msg)`
        """

        self.tellraw("@a", msg)


    def tellraw(
        self,
        at: Union[At, Player, str],
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

            return
        
        if type(msg) is str:
            self.execute(f"""/tellraw {at} {{"text": "{msg}"}}""")

        else:

            text = self._text_handler.bind_text(msg)
            
            temp_text = text.__str__(self.is_v1_21_5)
            
            if len(temp_text) > 1400:

                texts = text._split()
                
                with self.all_at_once():

                    for text in texts:
                        
                        text = text.__str__(self.is_v1_21_5)
                        self.execute(f"/tellraw {at} {text}")

                return
            
            self.execute(f"/tellraw {at} {temp_text}")


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
        type: str = "ambient",
        at: At | str ="@a",
        coords: Optional[Coordinate] = None,
        volume: float = 1,
        pitch: float = 1,
        min_volume: float = 0
    ) -> None:
        
        coord_needed = volume != 1 or pitch != 1 or min_volume != 0

        if (
            (coords is None and coord_needed) is True or
            str(at).startswith(("@a", "@e"))
        ):
            
            if str(at).startswith(("@a", "@e")):

                players = self.get_online_players() or []
                
                for player in players:
                    
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
        type: str,
        at: At | str,
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
        params_to_pass = []
        required_flag = False

        for p, r in zip(params, required):
            
            required_flag = required_flag or r

            if required_flag is True:
                params_to_pass.append(p)

        if len(params_to_pass) > 0:

            params_to_pass.reverse()
            command += " " + " ".join(params_to_pass)
        
        return command

    
    def stopsound(
        self,
        at: str,
        sound: str,
        type="ambient"
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