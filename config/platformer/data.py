# Technologies that we don't want to be randomized
ignored_technologies = ['automation', 'automation-science-pack', 'electronics', 'engine', 'space-platform', 'steel-processing']

# Stuff be is only hidden by platformer but should be considered removed
removed_technologies = [
    'discharge-defense-equipment',
    'energy-shield-equipment',
    'energy-shield-mk2-equipment',
    'fish-breeding',
    'personal-laser-defense-equipment',
    'tree-seeding',
]

def override_data(machines, recipes, recipes_unlocked_at_start, surfaces, surfaces_accessible_at_start, technologies, **args):
    # Remove mining
    for recipe in recipes:
        if recipe.name.startswith("mining-"):
           del recipes[recipe.name]

           recipes_unlocked_at_start.remove(recipe.name)

    # Keep only space platform surface
    for surface in surfaces:
        if not surface.name == 'space-platform':
            del surfaces[surface.name]

    surfaces_accessible_at_start.clear()
    surfaces_accessible_at_start.add('space-platform')

    # Removed machines
    del machines['burner-mining-drill']
    del machines['electric-mining-drill']
    del machines['big-mining-drill']
    del machines['stone-furnace']
    del machines['steel-furnace']

    # Ignored technologies
    for technology_name in ignored_technologies:
        technology = technologies[technology_name]

        recipes_unlocked_at_start.update(technology.unlocked_recipes)

        del technologies[technology_name]

    # Removed technologies
    for technology_name in removed_technologies:
        del technologies[technology_name]
