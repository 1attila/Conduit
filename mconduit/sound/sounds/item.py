# =============================
# Created by 1attla's generator
# =============================

nautilus_saddle_equip = "item.nautilus_saddle_equip"
nautilus_saddle_underwater_equip = "item.nautilus_saddle_underwater_equip"

class armor:
    equip_chain = "item.armor.equip_chain"
    equip_copper = "item.armor.equip_copper"
    equip_diamond = "item.armor.equip_diamond"
    equip_elytra = "item.armor.equip_elytra"
    equip_generic = "item.armor.equip_generic"
    equip_gold = "item.armor.equip_gold"
    equip_iron = "item.armor.equip_iron"
    equip_leather = "item.armor.equip_leather"
    equip_nautilus = "item.armor.equip_nautilus"
    equip_netherite = "item.armor.equip_netherite"
    equip_turtle = "item.armor.equip_turtle"
    equip_wolf = "item.armor.equip_wolf"
    unequip_nautilus = "item.armor.unequip_nautilus"
    unequip_wolf = "item.armor.unequip_wolf"

class axe:
    scrape = "item.axe.scrape"
    strip = "item.axe.strip"
    wax_off = "item.axe.wax_off"

class bone_meal:
    use = "item.bone_meal.use"

class book:
    page_turn = "item.book.page_turn"
    put = "item.book.put"

class bottle:
    empty = "item.bottle.empty"
    fill = "item.bottle.fill"
    fill_dragonbreath = "item.bottle.fill_dragonbreath"

class brush:
    class brushing:
        generic = "item.brush.brushing.generic"

        class _gravel:
            """
            NOTE: you can use this directly as:
            sounds.item.brush.brushing.gravel
            """

            def __repr__(self) -> str:
                return "item.brush.brushing.gravel"

            complete = "item.brush.brushing.gravel.complete"

        gravel = _gravel()

        class _sand:
            """
            NOTE: you can use this directly as:
            sounds.item.brush.brushing.sand
            """

            def __repr__(self) -> str:
                return "item.brush.brushing.sand"

            complete = "item.brush.brushing.sand.complete"

        sand = _sand()



class bucket:
    empty = "item.bucket.empty"
    empty_axolotl = "item.bucket.empty_axolotl"
    empty_fish = "item.bucket.empty_fish"
    empty_lava = "item.bucket.empty_lava"
    empty_powder_snow = "item.bucket.empty_powder_snow"
    empty_tadpole = "item.bucket.empty_tadpole"
    fill = "item.bucket.fill"
    fill_axolotl = "item.bucket.fill_axolotl"
    fill_fish = "item.bucket.fill_fish"
    fill_lava = "item.bucket.fill_lava"
    fill_powder_snow = "item.bucket.fill_powder_snow"
    fill_tadpole = "item.bucket.fill_tadpole"

class bundle:
    drop_contents = "item.bundle.drop_contents"
    insert = "item.bundle.insert"
    insert_fail = "item.bundle.insert_fail"
    remove_one = "item.bundle.remove_one"

class chorus_fruit:
    teleport = "item.chorus_fruit.teleport"

class crop:
    plant = "item.crop.plant"

class crossbow:
    hit = "item.crossbow.hit"
    loading_end = "item.crossbow.loading_end"
    loading_middle = "item.crossbow.loading_middle"
    loading_start = "item.crossbow.loading_start"
    quick_charge_1 = "item.crossbow.quick_charge_1"
    quick_charge_2 = "item.crossbow.quick_charge_2"
    quick_charge_3 = "item.crossbow.quick_charge_3"
    shoot = "item.crossbow.shoot"

class dye:
    use = "item.dye.use"

class elytra:
    flying = "item.elytra.flying"

class firecharge:
    use = "item.firecharge.use"

class flintandsteel:
    use = "item.flintandsteel.use"

class glow_ink_sac:
    use = "item.glow_ink_sac.use"

class goat_horn:
    class sound:
        _0 = "item.goat_horn.sound.0"
        _1 = "item.goat_horn.sound.1"
        _2 = "item.goat_horn.sound.2"
        _3 = "item.goat_horn.sound.3"
        _4 = "item.goat_horn.sound.4"
        _5 = "item.goat_horn.sound.5"
        _6 = "item.goat_horn.sound.6"
        _7 = "item.goat_horn.sound.7"


class hoe:
    till = "item.hoe.till"

class honey_bottle:
    drink = "item.honey_bottle.drink"

class honeycomb:
    wax_on = "item.honeycomb.wax_on"

class horse_armor:
    unequip = "item.horse_armor.unequip"

class ink_sac:
    use = "item.ink_sac.use"

class lead:
    break_ = "item.lead.break"
    tied = "item.lead.tied"
    untied = "item.lead.untied"

class llama_carpet:
    unequip = "item.llama_carpet.unequip"

class lodestone_compass:
    lock = "item.lodestone_compass.lock"

class mace:
    smash_air = "item.mace.smash_air"
    smash_ground = "item.mace.smash_ground"
    smash_ground_heavy = "item.mace.smash_ground_heavy"

class nether_wart:
    plant = "item.nether_wart.plant"

class ominous_bottle:
    dispose = "item.ominous_bottle.dispose"

class saddle:
    unequip = "item.saddle.unequip"

class shears:
    snip = "item.shears.snip"

class shield:
    block = "item.shield.block"
    break_ = "item.shield.break"

class shovel:
    flatten = "item.shovel.flatten"

class spear:
    attack = "item.spear.attack"
    hit = "item.spear.hit"
    lunge_1 = "item.spear.lunge_1"
    lunge_2 = "item.spear.lunge_2"
    lunge_3 = "item.spear.lunge_3"
    use = "item.spear.use"

class spear_wood:
    attack = "item.spear_wood.attack"
    hit = "item.spear_wood.hit"
    use = "item.spear_wood.use"

class spyglass:
    stop_using = "item.spyglass.stop_using"
    use = "item.spyglass.use"

class totem:
    use = "item.totem.use"

class trident:
    hit = "item.trident.hit"
    hit_ground = "item.trident.hit_ground"
    return_ = "item.trident.return"
    riptide_1 = "item.trident.riptide_1"
    riptide_2 = "item.trident.riptide_2"
    riptide_3 = "item.trident.riptide_3"
    throw = "item.trident.throw"
    thunder = "item.trident.thunder"

class wolf_armor:
    break_ = "item.wolf_armor.break"
    crack = "item.wolf_armor.crack"
    damage = "item.wolf_armor.damage"
    repair = "item.wolf_armor.repair"
