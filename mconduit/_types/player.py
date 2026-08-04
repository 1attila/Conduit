from __future__ import annotations
from typing import Optional, Dict, List, TYPE_CHECKING
import time

from mconduit.utils.scoreboards import get_score
from mconduit.enums.dimension import Dimension
from mconduit.enums.gamemode import Gamemode
from mconduit.enums.color import Color
from mconduit.text.text import Text
from mconduit.perms.item import PermissionItem
from .entity_data_fetcher import AttributeNotFound, _parse_dimension
from .location import Location
from .vec3d import Vec3d
from .item import Item
from .mob import Mob

if TYPE_CHECKING:
    from mconduit.scoreboard.team import Team


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

        return bool(self._fetch("abilities", dict[str, bool])["flying"])
    
    
    @property
    def can_instabuild(self) -> bool:
        """
        Warning: Not following naming conventions.

        True if the player can instantly destroy blocks.
        True only for creative mode
        """
        
        return bool(self._fetch("abilities", dict[str, bool])["instabuild"])
    

    @property
    def is_invulnerable(self) -> bool:
        """
        Warning: Not following naming conventions.

        True if the player is immune to all damage and harmful effects except for void damage.
        True only for creative and spectator.

        Differs from the invulnerable attribute
        """
        
        return bool(self._fetch("abilities", dict[str, bool])["invulnerable"])
    

    @property
    def may_build(self) -> bool:
        """
        True if the player can place and destroy blocks.
        
        True for creative and survival
        """
        
        return bool(self._fetch("abilities", dict[str, bool])["mayBuild"])
    

    @property
    def may_fly(self) -> bool:
        """
        True if the player can fly.

        True for creative and spectator
        """
        
        return bool(self._fetch("abilities", dict[str, bool])["mayfly"])
    

    @property
    def dimension(self) -> Dimension:
        """
        Player dimension
        """

        return self._fetch("Dimension", Dimension)
    
    
    @property
    def echest_inventory(self) -> Dict[int, Item]:
        """
        Warning: Not following naming conventions.

        Ender chest inventory
        """

        inv = self._fetch("EnderItems", list)
        inventory = {}
        
        for item in inv:
            inventory[int(item["Slot"])] = Item(item["id"], item["count"], item.get("components", None))

        return inventory
    

    @property
    def entered_nether_pos(self) -> Optional[Vec3d]:
        """
        Overworld position when the player entered in the nether.

        It may not exist
        """
        
        try:
            s = self._fetch("enteredNetherPosition", dict)
            return Vec3d(s["x"], s["y"], s["z"])
        
        except AttributeNotFound:
            return None
        
    
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

        inv = self._fetch("Inventory", list)
        inventory = {}
        
        for item in inv:
            inventory[item["Slot"]] = Item(item["id"], item["count"], item.get("components", None))

        return inventory
    

    @property
    def last_death_location(self) -> Optional[Location]:
        """
        Last death pos and dimension.

        It may not exist
        """

        try:
            return self._fetch("LastDeathLocation", Location)

        except AttributeNotFound:
            return None
        

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

        try:
            si = self._fetch("SelectedItem", dict)

            return Item(si["id"], si["count"], si.get("components", None))

        except AttributeNotFound:
            return None
    
    
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
    def respawn_dimension(self) -> Optional[Dimension]:
        """
        Player respawn dimension.

        It may not exist
        """

        try:
            return _parse_dimension(self._fetch("respawn", dict)["dimension"])

        except AttributeNotFound:
            return None
    
    
    @property
    def respawn_pos(self) -> Optional[Vec3d]:
        """
        Warning: Not following naming conventions.

        Coordinate of the players bed of respawn anchor.

        It may not exist
        """

        try:
            s = self._fetch("respawn", dict)["pos"]

            return Vec3d(*s)

        except AttributeNotFound:
            return None
    

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
    def team(self) -> Optional[Team]:
        """
        Team the player is part of
        """

        for team in self._server.teams.values():

            for player in team.players:

                if player.name == self.name:
                    return team

        return None


    @property
    def display_name(self) -> Text:
        """
        Name of the player with the team color
        """

        team = self.team

        if team is not None and team.team_color is not None:
            color = team.team_color
        else:
            color = Color.WHITE
        
        return Text(self.name, color) # NOTE: avoiding team prefix and suffix is volontary
    

    def is_sneaking(self) -> bool:
        """
        Returns True if the player is sneaking.

        Implemented using a double scoreboard check, it may take some time to process 
        """

        initial_sneak = get_score(self._server, self._name, "mconduit-sneak") or 0
        
        time.sleep(1 / 20) # 1 tick

        current_sneak = get_score(self._server, self._name, "mconduit-sneak") or 0

        if current_sneak > initial_sneak:
            return True
        
        return False


    @property
    def permissions(self) -> List[str]:
        """
        Player permissions, Guest as default
        """

        return self._server.permission_manager.get_player_perms(self._name)


    def has_permissions(self, *permissions: PermissionItem | str) -> bool:
        """
        Returns True if this player has the given permissions
        """

        for permission in self.permissions:

            if not self._server.permission_manager.has_permission(self._name, permission):
                return False

        return True
    

    def has_permission(self, permission: PermissionItem | str) -> bool:
        """
        Returns True if this player has the given permission
        """

        return self.has_permissions(permission)


    def __str__(self) -> str:
        return self._name


    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Player):
            return False
        
        return self._name == other._name