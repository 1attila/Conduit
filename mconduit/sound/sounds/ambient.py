# =============================
# Created by 1attla's generator
# =============================

cave = "ambient.cave"

class basalt_deltas:
    additions = "ambient.basalt_deltas.additions"
    loop = "ambient.basalt_deltas.loop"
    mood = "ambient.basalt_deltas.mood"

class crimson_forest:
    additions = "ambient.crimson_forest.additions"
    loop = "ambient.crimson_forest.loop"
    mood = "ambient.crimson_forest.mood"

class nether_wastes:
    additions = "ambient.nether_wastes.additions"
    loop = "ambient.nether_wastes.loop"
    mood = "ambient.nether_wastes.mood"

class soul_sand_valley:
    additions = "ambient.soul_sand_valley.additions"
    loop = "ambient.soul_sand_valley.loop"
    mood = "ambient.soul_sand_valley.mood"

class underwater:
    enter = "ambient.underwater.enter"
    exit = "ambient.underwater.exit"

    class _loop:
        """
        NOTE: you can use this directly as:
        sounds.ambient.underwater.loop
        """

        def __repr__(self) -> str:
            return "ambient.underwater.loop"


        class _additions:
            """
            NOTE: you can use this directly as:
            sounds.ambient.underwater.loop.additions
            """

            def __repr__(self) -> str:
                return "ambient.underwater.loop.additions"

            rare = "ambient.underwater.loop.additions.rare"
            ultra_rare = "ambient.underwater.loop.additions.ultra_rare"

        additions = _additions()


    loop = _loop()


class warped_forest:
    additions = "ambient.warped_forest.additions"
    loop = "ambient.warped_forest.loop"
    mood = "ambient.warped_forest.mood"
