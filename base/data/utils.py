import re

from .classes import MinableResource, PumpableResource, Recipe, Table
from .raw import machines, machines_for_manual_craft, recipes, recipes_unlocked_at_start, space_locations, surfaces, technologies


# Compute what is realy available
unlockable_recipes = Table()
for recipe_name in recipes_unlocked_at_start:
    if recipe_name in recipes:
        unlockable_recipes.add(recipes[recipe_name])
for technology in technologies:
    for recipe_name in technology.unlocked_recipes:
        if recipe_name in recipes:
            unlockable_recipes.add(recipes[recipe_name])

def _get_craftable(recipes: list[Recipe], resource: list[str]) -> tuple[set[str], Table]:
    craftable_items: set[str] = set()
    craftable_recipes: Table = Table()
    craftable_categories: set[str] = set()

    for machine_name in machines_for_manual_craft:
        craftable_categories.update(machines[machine_name].crafting_categories)

    loop = True
    while loop:
        loop = False

        for recipe in recipes:
            if recipe.name in craftable_recipes:
                continue

            if recipe.category not in craftable_categories:
                continue

            if all((ingredient in resource or ingredient in craftable_items for ingredient in recipe.ingredients)):
                craftable_recipes.add(recipe)

                for item_name in recipe.products.keys():
                    craftable_items.add(item_name)

                    if item_name in machines:
                        craftable_categories.update(machines[item_name].crafting_categories)

                loop = True

    return craftable_items, craftable_recipes

resources = set()
resources_at_start = set()
for space_location in space_locations:
    for asteroid_chunk in space_location.asteroid_chunks:
        resources.add(asteroid_chunk)
        if space_location.accessible_at_start:
            resources_at_start.add(asteroid_chunk)
for surface in surfaces:
    for resource in surface.resources:
        if isinstance(resource, PumpableResource):
            resources.update(resource.fluid)
        if isinstance(resource, MinableResource):
            resources.update(resource.results.keys())
            if resource.mining_fluid is None and resource.category in machines['character'].mining_categories:
                resources_at_start.update(resource.results.keys())

craftable_items, craftable_recipes = _get_craftable(unlockable_recipes, resources)
craftable_items_at_start, craftable_recipes_at_start = _get_craftable([recipes[recipe_name] for recipe_name in recipes_unlocked_at_start], resources_at_start)


# Compute upgrades
upgrades_levels = {}
upgrades_map = {}

for technology in technologies:
    if not technology.upgrade and technology.max_level is None:
        continue

    match = re.match(r'^(?P<name>.+)-(?P<level>\d+)$', technology.name)
    if match:
        name = match.group('name')
        level = int(match.group('level'))
    else:
        name = technology.name
        level = 1

    if name not in upgrades_levels:
        upgrades_levels[name] = []

    upgrades_levels[name].append(technology)

    upgrades_map[technology.name] = name
