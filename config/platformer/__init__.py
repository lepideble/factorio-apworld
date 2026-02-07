game_name = "Factorio: Platformer"

def override_data(machines, recipes, recipes_unlocked_at_start, technologies):
    # Remove mining
    for recipe_name in list(recipes.keys()):
        if recipe_name.startswith("mining-"):
           del recipes[recipe_name]

    # Don't randomize starting technologies
    ignored_technologies = [
        "automation-science-pack",
        "electronics",
        "space-platform",
    ]
    for technology_name in ignored_technologies:
        technology = technologies[technology_name]

        recipes_unlocked_at_start.update(technology.unlocked_recipes)

        del technologies[technology_name]
