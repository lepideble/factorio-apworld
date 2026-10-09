local config = require("config")

if config.free_samples == nil then
    return {}
end

local items = require("script/items")
local receive = require("script/receive")

local function get_stack_size(name)
    local item = prototypes.item[name]
    if item ~= nil then
        return item.stack_size
    end
    item = prototypes.equipment[name]
    if item ~= nil then
        return item.stack_size
    end
    -- failsafe
    return 1
end

local function send_for_recipe(force, recipe_name)
    local recipe = prototypes.recipe[recipe_name]

    for _, result in pairs(recipe.products) do
        if result.type == "item" and result.amount then
            local name = result.name
            if config.free_samples.blacklist[name] ~= 1 then
                local count
                if config.free_samples.quantity == "single_craft" then
                    count = result.amount
                else
                    count = get_stack_size(result.name)
                    if config.free_samples.quantity == "half_stack" then
                        count = math.ceil(count / 2)
                    end
                end
                items.calls.queue_item(force, name, count, config.free_samples.quality)
            end
        end
    end
end

local function send_for_technology(force, technology_name)
    local technology = prototypes.technology[technology_name]

    for _, effect in pairs(technology.effects) do
        if effect.type == "unlock-recipe" then
            send_for_recipe(force, effect.recipe)
        end
    end
end

receive.hooks.received_recipe(send_for_recipe)
receive.hooks.received_technology(send_for_technology)

return {}
