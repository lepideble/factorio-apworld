game_name = "Factorio: Platformer"

def override_data(recipes, recipes_unlocked_at_start, surfaces, surfaces_accessible_at_start, technologies, **args):
    # Remove mining
    for recipe in recipes:
        if recipe.name.startswith("mining-"):
           del recipes[recipe.name]

    # Keep only space platform surface
    for surface in surfaces:
        if not surface.name == 'space-platform':
            del surfaces[surface.name]

    surfaces_accessible_at_start.clear()
    surfaces_accessible_at_start.add('space-platform')

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
