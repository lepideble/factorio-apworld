require("lib")

local register_received_recipe_hook, call_received_recipe_hooks = create_hook()
local register_received_technology_hook, call_received_technology_hooks = create_hook()

local TRAP_TABLE = {
["Attack Trap"] = function ()
    game.surfaces["nauvis"].build_enemy_base(game.forces["player"].get_spawn_position(game.get_surface(1)), 25)
end,
["Evolution Trap"] = function ()
    local new_factor = game.forces["enemy"].get_evolution_factor("nauvis") +
        (TRAP_EVO_FACTOR * (1 - game.forces["enemy"].get_evolution_factor("nauvis")))
    game.forces["enemy"].set_evolution_factor(new_factor, "nauvis")
    game.print({"traps.new-evolution-factor", new_factor})
end,
["Teleport Trap"] = function()
    for _, player in ipairs(game.forces["player"].players) do
        if player.character then
            attempt_teleport_player(player, 1)
        end
    end
end,
["Grenade Trap"] = function ()
    fire_entity_at_players("grenade", 0.1)
end,
["Cluster Grenade Trap"] = function ()
    fire_entity_at_players("cluster-grenade", 0.1)
end,
["Artillery Trap"] = function ()
    fire_entity_at_players("artillery-projectile", 1)
end,
["Atomic Rocket Trap"] = function ()
    fire_entity_at_players("atomic-rocket", 0.1)
end,
["Atomic Cliff Remover Trap"] = function ()
    local cliffs = game.surfaces["nauvis"].find_entities_filtered{type = "cliff"}

    if #cliffs > 0 then
        fire_entity_at_entities("atomic-rocket", {cliffs[math.random(#cliffs)]}, 0.1)
    end
end,
["Inventory Spill Trap"] = function ()
    for _, player in ipairs(game.forces["player"].players) do
        spill_character_inventory(player.character)
    end
end,
}

local receive_item = function(item_name, source)
    local force = game.forces["player"]

    local technology = force.technologies[item_name]
    if technology ~= nil then
        if technology.researched then
            return false
        end

        game.print({"archipelago.receive-ap-item", "[technology=" .. technology.name .. "]", source})
        game.play_sound({path="utility/research_completed"})

        technology.researched = true

        call_received_technology_hooks(foce, technology.name)

        return true
    end

    local quality_name = string_strip_prefix(item_name, "quality: ")
    if quality_name then
        local quality = prototypes.quality[quality_name]
        if quality ~= nil then
            if force.is_quality_unlocked(quality) then
                return false
            end

            game.print({"archipelago.receive-ap-item", "[quality=" .. quality.name .. "]", source})
            game.play_sound({path="utility/research_completed"})

            force.unlock_quality(quality)

            return true
        end
    end

    local recipe_name = string_strip_prefix(item_name, "recipe: ")
    if recipe_name then
        local recipe = force.recipes[recipe_name]
        if recipe ~= nil then
            if recipe.enabled then
                return false
            end

            game.print({"archipelago.receive-ap-item", "[recipe=" .. recipe.name .. "]", source})
            game.play_sound({path="utility/research_completed"})

            recipe.enabled = true

            call_received_recipe_hooks(force, recipe.name)

            return true
        end
    end

    local space_location_name = string_strip_prefix(item_name, "space location: ")
    if space_location_name then
        local space_location = prototypes.space_location[space_location_name]
        if space_location ~= nil then
            if force.is_space_location_unlocked(space_location) then
                return false
            end

            game.print({"archipelago.receive-ap-item", "[space-location=" .. space_location.name .. "]", source})
            game.play_sound({path="utility/research_completed"})

            force.unlock_space_location(space_location)

            return true
        end
    end

    if TRAP_TABLE[item_name] ~= nil then
        game.print({"archipelago.receive-ap-item", item_name, source})
        TRAP_TABLE[item_name]()

        return true
    end

    game.print("Unknown Item " .. item_name)
end

local on_init = function()
    storage.receive_index = {}
    storage.receive_items = {}
end

local on_technology_effects_reset = function()
    local force = game.forces["player"]

    for _, item_name in pairs(storage.receive_items) do
        local quality_name = string_strip_prefix(item_name, "quality: ")
        if quality_name then
            local quality = prototypes.quality[quality_name]
            if quality then
                force.unlock_quality(quality)
            end
        end

        local recipe_name = string_strip_prefix(item_name, "recipe: ")
        if recipe_name then
            local recipe = force.recipes[recipe_name]
            if recipe then
                recipe.enabled = true
            end
        end

        local space_location_name = string_strip_prefix(item_name, "space location: ")
        if space_location_name then
            local space_location = prototypes.space_location[space_location_name]
            if space_location then
                force.unlock_space_location(space_location)
            end
        end
    end
end

local get_technology_command = function(call)
    local force = game.forces["player"]
    if call.parameter == nil then
        game.print("ap-get-technology is only to be used by the Archipelago Factorio Client")
        return
    end
    chunks = split(call.parameter, "\t")
    local item_name = chunks[1]
    local index = chunks[2]
    local source = chunks[3] or "Archipelago"

    if index == nil then
        game.print("ap-get-technology is only to be used by the Archipelago Factorio Client")
        return
    end

    if index == "-1" then -- for coop sync and restoring from an older savegame
        local tech = force.technologies[item_name]
        if tech.researched ~= true then
            game.print({"archipelago.receive-ap-catchup", "[technology=" .. tech.name .. "]"})
            game.play_sound({path="utility/research_completed"})
            tech.researched = true
        end
        return
    end

    if storage.receive_index[index] == item_name then
        return
    end

    local received, received_item
    if PROGRESSIVE_ITEMS[item_name] ~= nil then
        for _, progressive_item_name in ipairs(PROGRESSIVE_ITEMS[item_name]) do
            received = receive_item(progressive_item_name, source)
            received_item = progressive_item_name

            if received ~= false then
                break
            end
        end
    else
        received = receive_item(item_name, source)
        received_item = item_name
    end

    if received then
        storage.receive_index[index] = item_name
        storage.receive_items[index] = received_item
    end
end

return {
    on_init = on_init,
    events = {
        [defines.events.on_technology_effects_reset] = on_technology_effects_reset,
    },
    add_commands = function()
        commands.add_command("ap-get-technology", "Grant a technology, used by the Archipelago Client.", get_technology_command)
    end,
    hooks = {
        received_recipe = register_received_recipe_hook,
        received_technology = register_received_technology_hook,
    },
}
