from typing import Optional, Dict, TYPE_CHECKING
import parse
import time

from ..utils.scoreboards import get_score
from ..enums.dimension import Dimension
from ..enums.gamemode import Gamemode
from .location import Location
from .vec3d import Vec3d
from .item import Item
from .mob import Mob

if TYPE_CHECKING:
    from ..plugins.perms import Permission
    from ..server import Server


class Player(Mob):
    """
    Player class containing almost every field
        returned from 'data get entity <player_name>'

    Unused fields:
    - shoulder_entity_left: Optional[Entity]
    - shoulder_entity_rigth: Optional[Entity]
    - spawn_forced: bool
    - warden_spawn_tracker: Dict
    
    Note that all the fields have been converted from camel-case to
    snake-case to follow Python's naming convention.
    Most boolean fields are a bit different to better follow
    Python's naming convention
    (E.g. 'flying' -> 'is_flying').

    Other fields name that are different to be more explicative:
    - instabuild -> can_instabuild
    - ender_items -> echest_inventory
    - player_game_type -> gamemode
    - previous_player_game_type -> prev_gamemode
    - seen_credits -> has_seen_credits
    - selected_item_slot -> selected_slot
    - [spawn_x, spawn_y, spawn_z] -> spawn_pos
    - xp_p -> xp_progress_perc
    """


    __permissions: Optional["Permission"] # Cached because fetch it every time requires time, it's used frequently and it's not modified a lot
    

    def __init__(self, name: str, server: "Server") -> None:

        self.__permissions = None
        super().__init__(name, server)


    @property
    def name(self) -> str:
        """
        Player name
        """

        return self._name
    

    @property
    def is_flying(self) -> bool:
        """
        Warning: Not following naming conventions.

        True if the entity is currently flying
        """

        return self._fetch("flying", bool)
    
    
    @property
    def can_instabuild(self) -> bool:
        """
        Warning: Not following naming conventions.

        True if the player can instantly destroy blocks.
        True only for creative mode
        """
        
        return self._fetch("instabuild", bool)
    

    @property
    def is_invulnerable(self) -> bool:
        """
        Warning: Not following naming conventions.

        True if the player is immune to all damage and harmful effects except for void damage.
        True only for creative and spectator.

        Differs from the invulnerable attribute
        """
        
        return self._fetch("invulnerable", bool)
    

    @property
    def may_build(self) -> bool:
        """
        True if the player can place and destroy blocks.
        
        True for creative and survival
        """
        
        return self._fetch("mayBuild", bool)
    

    @property
    def may_fly(self) -> bool:
        """
        True if the player can fly.

        True for creative and spectator
        """
        
        return self._fetch("mayFly", bool)
    

    @property
    def dimension(self) -> Dimension:
        """
        Player dimension
        """

        return self._fetch("Dimension", Dimension)
    
    
    @property
    def echest_inventory(self) -> Dict[int, str]:
        """
        Warning: Not following naming conventions.

        Ender chest inventory
        """

        return self._fetch("EnderItems", Dict)
    

    @property
    def entered_nether_pos(self) -> Optional[Vec3d]:
        """
        Overworld position when the player entered in the nether.

        It may not exist
        """
        
        if s:= self._fetch("enteredNetherPosition"):
            return Vec3d.from_string(s)
        
    
    @property
    def food_exhaustion_level(self) -> float:
        """
        Player food exaustion level
        """
        
        return self._fetch("foodExhaustionLevel", float)
    

    @property
    def food_level(self) -> int:
        """
        Value on the player hunger bar.

        0 - 20
        """
        
        return self._fetch("foodLevel", int)
    
    
    @property
    def food_saturation_level(self) -> float:
        """
        Player food saturation level
        """
        
        return self._fetch("foodSaturationLevel", float)
    
    
    @property
    def food_tick_timer(self) -> int:
        """
        Player food timer
        """

        return self._fetch("foodTickTimer", int)
    
    
    @property
    def inventory(self) -> Dict[int, Item]:
        """
        Players inventory
        """

        inv = self._fetch("Inventory", Dict) # `Dict` means load as json, so this returns a list in this case!
        inventory = {}

        for item in inv:
            inventory[item["Slot"]] = Item(item["id"], item["count"])

        return inventory
    

    @property
    def last_death_location(self) -> Optional[Location]:
        """
        Last death pos and dimension.

        It may not exist
        """

        return self._fetch("LastDeathLocation", Location)
    

    @property
    def gamemode(self) -> Gamemode:
        """
        Warning: Not following naming conventions.

        Player current gamemode
        """

        return self._fetch("playerGameType", Gamemode)


    @property
    def score(self) -> int:
        """
        Player score displayed upon death
        """

        return self._fetch("Score", int)
    
    
    @property
    def has_seen_credits(self) -> bool:
        """
        Warning: Not following naming conventions.

        True if player has entered the exit portal in the end
        """

        return self._fetch("seenCredits", bool)
    
    
    @property
    def selected_item(self) -> Optional[Item]:
        """
        Selected item, if there is one
        """

        si =  self._fetch("SelectedItem", Dict)

        if si is not None:
            return Item(si["id"], si["count"])
    
    
    @property
    def selected_slot(self) -> Optional[int]:
        """
        Warning: Not following naming conventions.

        Selected hotbar slot, if there is one
        """

        return self._fetch("SelectedItemSlot", int)


    @property
    def sleep_timer(self) -> int:
        """
        Player time had been in bed in ticks
        """

        return self._fetch("SleepTimer", int)
    
    
    @property
    def spawn_dimension(self) -> Optional[Dimension]:
        """
        Player respawn dimension.

        It may not exist
        """

        return self._fetch("SpawnDimension", Dimension)
    
    
    @property
    def spawn_pos(self) -> Optional[Vec3d]:
        """
        Warning: Not following naming conventions.

        Coordinate of the players bed of respawn anchor.

        It may not exist
        """

        x, y, z = [self._fetch(f"Spawn{item}", int) for item in "XYZ"]

        if x and y and z:
            return Vec3d(x, y, z)
    

    @property
    def xp_level(self) -> int:
        """
        Player xp level
        """

        return self._fetch("XpLevel", int)
    

    @property
    def xp_progress_perc(self) -> float:
        """
        Warning: Not following naming conventions.

        Progress across the bar to the next level
        """

        return self._fetch("XpP", float)
    

    @property
    def xp_seed(self) -> int:
        """
        Seed used for the next enchantment
        """

        return self._fetch("XpSeed", int)
    

    @property
    def xp_total(self) -> int:
        """
        Total xp the player has collected
        """

        return self._fetch("XpTotal", int)
    

    @property
    def is_sneaking(self) -> bool:
        """
        Returns True if the player is sneaking.

        Implemented using a double scoreboard check, it may take some time to process 
        """

        initial_sneak = get_score(self.__server, self.__name, "mconduit-sneak") or 0
        
        time.sleep(1 / 20) # 1 tick

        current_sneak = get_score(self.__server, self.__name, "mconduit-sneak") or 0

        if current_sneak > initial_sneak:
            return True
        
        return False


    @property
    def permissions(self) -> "Permission":
        """
        Player permissions, Guest as default
        """

        if self.__permissions is not None:
            return self.__permissions

        for perm, teams in self._server.permissions.items():

            for team in teams:
                data = self._server.execute(f"/team list {team}")
                
                data = parse.parse(r"Team [{team}] has {n} member(s): {members}", data)

                if data:

                    players = data["members"].split(", ")

                    if self.name in players:

                        self.__permissions = perm
                        
                        return perm

        self.__permissions = 0
        
        return 0 # Guest as default


    def __str__(self) -> str:
        return self._name