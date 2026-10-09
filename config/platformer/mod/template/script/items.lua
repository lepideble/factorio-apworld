local config = require("config")

local function send_items(platform)
    local data = storage.items.platforms[platform.index]
    local sent
    local stack = {}

    for name, qualities in pairs(data.pending) do
        for quality, count in pairs(qualities) do
            stack.name = name
            stack.count = count
            if script.active_mods["quality"] then
                stack.quality = quality
            end
            if prototypes.item[name] then
                if platform.hub.can_insert(stack) then
                    sent = platform.hub.insert(stack)
                else
                    sent = 0
                end
                if sent > 0 then
                    platform.force.print({"archipelago.receive-sample-item", sent, "[item=" .. name .. ",quality=" .. quality .. "]"})
                    data.suppress_full_inventory_message = false
                end
                if sent ~= count then               -- Couldn't full send.
                    if not data.suppress_full_inventory_message then
                        platform.force.print({"archipelago.sample-inventory-full"}, {r=1, g=1, b=0.25})
                    end
                    data.suppress_full_inventory_message = true -- Avoid spamming them with repeated full inventory messages.
                    data.pending[name][quality] = count - sent
                    break                           -- Stop trying to send other things
                else
                    data.pending[name][quality] = nil
                end
            else
                platform.force.print({"archipelago.sample-error", count, name})
                data.pending[name][quality] = nil
            end
        end
    end
end

local function add_to_item_table(table, name, count, quality)
    quality = quality or "normal"

    table[name] = table[name] or {}
    table[name][quality] = (table[name][quality] or 0) + count
end

local function queue_item(force, name, count, quality)
    if count <= 0 then
        return
    end

    add_to_item_table(storage.items.forces[force.name].received, name, count, quality)

    for _, platform in pairs(force.platforms) do
        -- Platforms that have been created with the "add platform" button exists in the platform table but should not
        -- be considered for free samples yet.
        if platform.hub ~= nil then
            add_to_item_table(storage.items.platforms[platform.index].pending, name, count, quality)
            send_items(platform)
        end
    end
end

local function on_force_created(event)
    storage.items.forces[event.force.name] = {
        received = {},
    }

    for name, count in pairs(config.starting_items) do
        add_to_item_table(storage.items.forces[event.force.name].received, name, count)
    end
end

local function on_surface_created(event)
    local surface = game.surfaces[event.surface_index]
    local platform = surface.platform

    if platform == nil then
        return
    end

    storage.items.platforms[platform.index] = {
        pending = table.deepcopy(storage.items.forces[platform.force.name].received),
    }

    send_items(platform)
end

local on_surface_deleted = function(event)
    local surface = game.surfaces[event.surface_index]
    local platform = surface.platform

    if platform == nil then
        return
    end

    storage.items.platforms[platform.index] = nil
end

-- Try to resend items after building in case the platform inventory was full
local on_space_platform_built_entity = function(event)
    send_items(event.platform)
end

local on_space_platform_built_tile = function(event)
    send_items(event.platform)
end

local function on_init()
    storage.items = {
        forces = {},
        platforms = {},
    }

    -- Fire dummy events for all currently existing surfaces.
    for _, force in pairs(game.forces) do
        on_force_created({ force = force })
    end
    for _, surface in pairs(game.surfaces) do
        on_surface_created({ surface_index = surface.index })
    end
end

return {
    on_init = on_init,
    calls = {
        queue_item = queue_item,
    },
    events = {
        [defines.events.on_force_created] = on_force_created,
        [defines.events.on_surface_created] = on_surface_created,
        [defines.events.on_surface_deleted] = on_surface_deleted,
        [defines.events.on_space_platform_built_entity] = on_space_platform_built_entity,
        [defines.events.on_space_platform_built_tile] = on_space_platform_built_tile,
    },
}
