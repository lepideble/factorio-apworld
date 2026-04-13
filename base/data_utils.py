import re

from .data import machines, machines_available_at_start, recipes, recipes_unlocked_at_start, space_locations, technologies
from .data_classes import Machine, Recipe, Technology


# Create lookup tables
_machines_by_category: dict[str, list[Machine]] = {}

for machine in machines:
    for category in machine.categories:
        if not category in _machines_by_category:
            _machines_by_category[category] = list()

        _machines_by_category[category].append(machine)

def machines_by_category(category: str) -> list[Machine]:
    return _machines_by_category.get(category, [])


_recipes_by_product: dict[str, list[Recipe]] = {}

for recipe in recipes:
    for product in recipe.products.keys():
        if not product in _recipes_by_product:
            _recipes_by_product[product] = list()

        _recipes_by_product[product].append(recipe)

def recipes_by_product(product: str) -> list[Recipe]:
    return _recipes_by_product.get(product, [])


_technologies_by_recipe_unlocked: dict[str, list[Technology]] = {}
_technologies_by_space_location_unlocked: dict[str, list[Technology]] = {}

for technology in technologies:
    for recipe_name in technology.unlocked_recipes:
        if not recipe_name in _technologies_by_recipe_unlocked:
            _technologies_by_recipe_unlocked[recipe_name] = list()

        _technologies_by_recipe_unlocked[recipe_name].append(technology)

    for space_location_name in technology.unlocked_space_locations:
        if not space_location_name in _technologies_by_space_location_unlocked:
            _technologies_by_space_location_unlocked[space_location_name] = list()

        _technologies_by_space_location_unlocked[space_location_name].append(technology)

def technologies_by_recipe_unlocked(recipe: str) -> list[Technology]:
    return _technologies_by_recipe_unlocked.get(recipe, [])

def technologies_by_space_location_unlocked(space_location: str) -> list[Technology]:
    return _technologies_by_space_location_unlocked.get(space_location, [])


# Compute what is realy available
unlockable_recipes = set()

for recipe in recipes:
    if recipe.name in recipes_unlocked_at_start or recipe.name in _technologies_by_recipe_unlocked:
        unlockable_recipes.add(recipe.name)


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
