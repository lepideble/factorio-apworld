local config = require("config")

local function send_items(player)
    if not player or not player.valid then     -- Do nothing if we reference an invalid player somehow
        return
    end
    local character = player.character or player.cutscene_character
    if not character or not character.valid then
        return
    end
    local data = storage.items.players[player.index]
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
                if character.can_insert(stack) then
                    sent = character.insert(stack)
                else
                    sent = 0
                end
                if sent > 0 then
                    player.print({"archipelago.receive-sample-item", sent, "[item=" .. name .. ",quality=" .. quality .. "]"})
                    data.suppress_full_inventory_message = false
                end
                if sent ~= count then               -- Couldn't full send.
                    if not data.suppress_full_inventory_message then
                        player.print({"archipelago.sample-inventory-full"}, {r=1, g=1, b=0.25})
                    end
                    data.suppress_full_inventory_message = true -- Avoid spamming them with repeated full inventory messages.
                    data.pending[name][quality] = count - sent
                    break                           -- Stop trying to send other things
                else
                    data.pending[name][quality] = nil
                end
            else
                player.print({"archipelago.sample-error", count, name})
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

    for _, player in pairs(force.players) do
        add_to_item_table(storage.items.players[player.index].pending, name, count, quality)
        send_items(player)
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

-- Initialize player data, either from them joining the game or them already being part of the game when the mod was
-- added.`
local on_player_created = function(event)
    local player = game.players[event.player_index]
    -- FIXME: This (probably) fires before any other mod has a chance to change the player's force
    -- For now, they will (probably) always be on the 'player' force when this event fires.
    storage.items.players[player.index] = {
        pending = table.deepcopy(storage.items.forces[player.force.name].received),
    }

    send_items(player)
end

local on_player_removed = function(event)
    storage.items.players[player.index] = nil
end

local update_player_event = function(event)
    send_items(game.players[event.player_index])
end

local function on_init()
    storage.items = {
        forces = {},
        players = {},
    }

    -- Fire dummy events for all currently existing forces and players.
    for _, force in pairs(game.forces) do
        on_force_created({ force = force })
    end
    for index, _ in pairs(game.players) do
        on_player_created({ player_index = index })
    end
end

return {
    on_init = on_init,
    calls = {
        queue_item = queue_item,
    },
    events = {
        [defines.events.on_force_created] = on_force_created,
        [defines.events.on_player_created] = on_player_created,
        [defines.events.on_player_removed] = on_player_removed,
        [defines.events.on_player_joined_game] = update_player_event,
        [defines.events.on_player_main_inventory_changed] = update_player_event,
        [defines.events.on_cutscene_cancelled] = update_player_event,
        [defines.events.on_cutscene_finished] = update_player_event,
    },
}
