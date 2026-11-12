for recipe_name, recipe in pairs(data.raw["recipe"]) do
    if string_starts_with(recipe_name, "empty-") and string_ends_with(recipe_name, "-barrel") then
        recipe.enabled = true
    end
end
