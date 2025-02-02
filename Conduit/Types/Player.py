from typing import Optional, Dict

from .Entity import Entity
from .Dimension import Dimension
from .Gamemode import Gamemode
from .Location import Location
from .Vec3d import Vec3d
from .Mob import Mob


class Player(Mob):
    """
    Player class containing almost every field
    returned from 'data entity <player_name>'

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
    - ender_items -> echest_inventory
    - player_game_type -> gamemode
    - previous_player_game_type -> prev_gamemode
    - seen_credits -> has_seen_credits
    - selected_item_slow -> selected_slot
    - [spawn_x, spawn_y, spawn_z] -> spawn_pos
    - xp_p -> xp_progress_perc
    """

    dimension: Dimension
    echest_inventory: Dict[int, str] # Not following naming convention
    entered_nether_pos: Vec3d
    food_exaustion_level: int
    food_level: int
    food_saturation_level: int
    food_tick_timer: int
    inventory: Dict[int, str]
    last_death_location: Location
    gamemode: Gamemode # Not following naming convention
    prev_gamemode: Gamemode # Not following naming convention
    root_vehicle: Optional[Entity]
    score: int
    has_seen_credits: bool # Not following naming convention
    selected_item: str
    selected_slot: int # Not following naming convention

    # [...]

    sleep_timer: int
    spawn_dimension: Dimension
    spawn_pos: Optional[Vec3d] # Not following naming convention

    # [...]

    xp_level: int
    xp_progress_perc: float # Not following naming convention
    xp_seed: int
    xp_total: int