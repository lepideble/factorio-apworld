import re

from .data import machines, machines_available_at_start, recipes, recipes_unlocked_at_start, space_locations, technologies, unlockable_recipes
from .data_classes import Recipe


def _get_craftable(recipes: list[Recipe]) -> tuple[set[str], set[str]]:
    craftable_items: set[str] = set()
    craftable_recipes: set[str] = set()
    craftable_categories: set[str] = set()

    for machine_name in machines_available_at_start:
        craftable_categories.update(machines[machine_name].categories)

    loop = True
    while loop:
        loop = False

        for recipe in recipes:
            if recipe.name in craftable_recipes:
                continue

            if recipe.category not in craftable_categories:
                continue

            if craftable_items.issuperset(recipe.ingredients.keys()):
                craftable_recipes.add(recipe.name)

                for item_name in recipe.products.keys():
                    craftable_items.add(item_name)

                    if item_name in machines:
                        craftable_categories.update(machines[item_name].categories)

                loop = True

    return craftable_items, craftable_recipes


craftable_items, craftable_recipes = _get_craftable([recipes[recipe_name] for recipe_name in unlockable_recipes])


_starting_recipes = []
for recipe_name in recipes_unlocked_at_start:
    recipe = recipes[recipe_name]

    if recipe.category == 'asteroid-chunk' and not any(map(lambda space_location: space_location.accessible_at_start and recipe.name in space_location.asteroid_chunks, space_locations)):
        continue

    _starting_recipes.append(recipe)

craftable_items_at_start, craftable_recipes_at_start = _get_craftable(_starting_recipes)


# Compute upgrades
upgrades_levels = {}
upgrades_min_level = {}
upgrades_max_level = {}
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
        upgrades_min_level[name] = 0
        upgrades_max_level[name] = 0

    upgrades_levels[name].append(technology)

    if technology.has_unlock:
        upgrades_min_level[name] = max(upgrades_min_level[name], level)

    if upgrades_max_level[name] is not None:
        if technology.max_level is not None:
            upgrades_max_level[name] = None if technology.max_level == 'infinite' else technology.max_level
        else:
            upgrades_max_level[name] = max(upgrades_max_level[name], level)

    upgrades_map[technology.name] = name
