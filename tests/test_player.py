from conduit import build_handler, Context


handler = build_handler()


@handler.on_player_join
def join(ctx: Context):
    test(ctx)


@handler.on_player_command
def command(ctx: Context):
    test(ctx)
    

def test(ctx: Context):

    ctx.wait_for_player()
    
    player = ctx.player

    try:
        # Entity
        print("Air", player.air)
        # print(player.custom_name)
        # print(player.is_custom_name_visible)
        print("FallDistance", player.fall_distance)
        print("Fire", player.fire)
        # print("Glowing", player.is_glowing) # Not for player
        # print("VisualFire", player.has_visual_fire) # Not for player
        # print(player.id) Player fix
        print("Invulnerable", player.invulnerable)
        print("Motion", player.motion)
        # print("NoGravity", player.no_gravity) # Not for players
        print("OnGround", player.is_on_ground)
        print("PortalCooldown", player.portal_cooldown)
        print("Pos", player.pos)
        print("Rotation", player.rotation)
        # print("Silent", player.is_silent) # Not for player
        print("Tags", player.tags)
        # print("TicksFrozen", player.ticks_frozen) # Not for player
        print("Uuid", player.uuid) # ToFix

        

        # Mob
        print("Healt", player.health)
        print("HurtTIme", player.hurt_time)
        print("HurtByTimestamp", player.hurt_by_timestamp)
        print("DeathTime", player.death_time)
        print("SleepingPos", player.sleeping_pos)

        # Player
        print("IsFlying", player.is_flying)
        print("CanInstabuild", player.can_instabuild)
        print("IsInvulnerable", player.is_invulnerable)
        print("MayBuild", player.may_build)
        print("MayFly", player.may_fly)
        print("Name", player.name)
        print("Dim", player.dimension)
        print("EchestInventory", player.echest_inventory)
        print("EnteredNetherPos", player.entered_nether_pos)
        print("ExaustionLevel", player.food_exhaustion_level)
        print("FoodLevel", player.food_level)
        print("SaturationLevel", player.food_saturation_level)
        print("FoodTickTimer", player.food_tick_timer)
        print("Inventory", player.inventory)
        print("LastDeathLocation", player.last_death_location)
        print("Gamemode", player.gamemode)
        print("Score", player.score)
        print("HasSeenCredits", player.has_seen_credits)
        print("SelectedItem", player.selected_item)
        print("SelectedSlot", player.selected_slot)
        print("SleepTimer", player.sleep_timer)
        print("SpawnDimension", player.spawn_dimension)
        print("SpawnPos", player.spawn_pos)
        print("XpLevel", player.xp_level)
        print("XpProgress", player.xp_progress_perc)
        print("XpSeed", player.xp_seed)
        print("XpTotal", player.xp_total)

    except Exception as e:
        print(e)