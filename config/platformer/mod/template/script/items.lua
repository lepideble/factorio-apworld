local config = require("config")

local function get_first_platform(force)
    for _, platform in pairs(force.platforms) do
        -- Platforms that have been created with the "add platform" button exists in the platforms table but don't have
        -- a hub to send items to
        if platform.hub ~= nil then
            return platform
        end
    end

    return nil
end

local function deliver_pending(force)
    local platform = get_first_platform(force)
    if not platform then
        return
    end

    local data = storage.items.forces[force.name]

    for name, qualities in pairs(data.pending) do
        for quality, count in pairs(qualities) do
            local stack = { name = name, count = count }
            if script.active_mods["quality"] then
                stack.quality = quality
            end
            if prototypes.item[name] then
                local sent
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
                    return                           -- Stop trying to send other things
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

local function deliver(force, name, count, quality)
    if count <= 0 then
        return
    end

    add_to_item_table(storage.items.forces[force.name].pending, name, count, quality)
    deliver_pending(force)
end

local function on_force_created(event)
    storage.items.forces[event.force.name] = {
        pending = {},
        suppress_full_inventory_message = false,
    }

    for name, count in pairs(config.starting_items) do
        add_to_item_table(storage.items.forces[event.force.name].pending, name, count)
    end
end

-- Try to resend items after building in case the platform inventory was full
local function on_space_platform_built_entity(event)
    deliver_pending(event.platform.force)
end

local function on_space_platform_built_tile(event)
    deliver_pending(event.platform.force)
end

local function on_init()
    storage.items = {
        forces = {},
    }

    -- Fire dummy events for all currently existing forces.
    for _, force in pairs(game.forces) do
        on_force_created({ force = force })
    end
end

return {
    on_init = on_init,
    calls = {
        deliver = deliver,
    },
    events = {
        [defines.events.on_force_created] = on_force_created,
        [defines.events.on_space_platform_built_entity] = on_space_platform_built_entity,
        [defines.events.on_space_platform_built_tile] = on_space_platform_built_tile,
    },
}
