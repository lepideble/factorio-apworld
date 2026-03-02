game_name = 'Factorio: Platformer'


# Technologies that we don't want to be randomized
ignored_technologies = ['automation', 'automation-science-pack', 'electronics', 'engine', 'space-platform', 'steel-processing']

# Removed technologies and recipes
removed_technologies = ['energy-shield-equipment', 'personal-laser-defense-equipment']
removed_recipes = ['energy-shield-equipment', 'personal-laser-defense-equipment']

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

    for technology_name in ignored_technologies:
        technology = technologies[technology_name]

        recipes_unlocked_at_start.update(technology.unlocked_recipes)

        del technologies[technology_name]

    for technology_name in removed_technologies:
        del technologies[technology_name]

    for recipe_name in removed_recipes:
        del recipes[recipe_name]
