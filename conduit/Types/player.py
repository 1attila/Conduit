from typing import Optional, Dict

from ..Enums.dimension import Dimension
from ..Enums.gamemode import Gamemode
from .location import Location
from .vec3d import Vec3d
from .mob import Mob


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
    def inventory(self) -> Dict[int, str]:
        """
        Players inventory
        """

        return self._fetch("Inventory", Dict)
    

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
    def selected_item(self) -> str:
        """
        Selected item
        """

        return self._fetch("SelectedItem")
    
    
    @property
    def selected_slot(self) -> int:
        """
        Warning: Not following naming conventions.

        Selected hotbar slot
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

    is_sneaking: bool # Added


    def __str__(self) -> str:
        return self._name