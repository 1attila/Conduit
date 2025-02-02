from .Entity import Entity


class Mob(Entity):
    """
    Mob class containing almost every field returned
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
    - instabuild -> can_instabuild
    """
    
    is_flying: bool # Not following naming convention
    fly_speed = float
    can_instabuild: bool # Not following naming convention
    is_invulnerable: bool # Not following naming convention
    may_build: bool
    may_fly: bool
    walk_speed: float