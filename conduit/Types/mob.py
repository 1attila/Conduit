from typing import Optional

from .entity import Entity
from .vec3d import Vec3d


class Mob(Entity):
    """
    Mob class containing some field returned
    from 'data entity <mob>'

    Unlike to other classes, a lot of fields are missing,
    this because all of them are costants that can be
    hardcoded into the program or pretty useless information.

    Note that all the fields have been converted from camel-case to
    snake-case to follow Python's naming convention.
    Most boolean fields are a bit different to better follow
    Python's naming convention
    (E.g. 'flying' -> 'is_flying').

    Other fields name that are different to be more explicative:
    - [SleepingX, SleepingY, SleepingZ] -> sleeping_pos
    """

    
    @property
    def health(self) -> float:
        """
        Mob health
        """

        return self._fetch("Health", float)
    

    @property
    def hurt_time(self) -> int:
        """
        Number of ticks the mob turns red after being hit
        """

        return self._fetch("HurtTime", int)


    @property
    def hurt_by_timestamp(self) -> int:
        """
        Last time the mob was damaged
        """

        return self._fetch("HurtByTimestamp", int)
    

    @property
    def death_time(self) -> int:
        """
        Number of ticks the mob has been dead for
        """

        return self._fetch("DeathTime", int)
    

    @property
    def sleeping_pos(self) -> Optional[Vec3d]:
        """
        Sleeping position, if the player is sleeping.

        It may not exist
        """

        x, y, z = [self._fetch(f"Sleeping{item}", int) for item in "XYZ"]

        if x and y and z:
            return Vec3d(x, y, z)