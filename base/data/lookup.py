from .classes import get_name, Machine, Recipe, SpaceLocation, Surface, Technology
from .raw import machines, recipes, technologies


def machines_by(
    can_be_placed_on: Surface|None = None,
    crafting_category: str|None = None,
    mining_category: str|None = None,
    allowed_science_packs: set[str]|None = None,
    is_offshore_pump: bool = None,
    is_asteroid_collector: bool = None,
) -> list[Machine]:
    filtered_machines = machines
    if can_be_placed_on is not None:
        filtered_machines = filter(lambda machine: machine.can_be_placed_on(can_be_placed_on), filtered_machines)
    if crafting_category is not None:
        filtered_machines = filter(lambda machine: crafting_category in machine.crafting_categories, filtered_machines)
    if mining_category is not None:
        filtered_machines = filter(lambda machine: mining_category in machine.mining_categories, filtered_machines)
    if allowed_science_packs is not None:
        filtered_machines = filter(lambda machine: machine.allowed_science_packs.issuperset(allowed_science_packs), filtered_machines)
    if is_offshore_pump is not None:
        filtered_machines = filter(lambda machine: machine.is_offshore_pump, filtered_machines)
    if is_asteroid_collector is not None:
        filtered_machines = filter(lambda machine: machine.is_asteroid_collector, filtered_machines)
    return list(filtered_machines)


def recipes_by(
    product: str|None = None,
    surface: Surface|None = None,
) -> list[Recipe]:
    filtered_recipes = recipes
    if product is not None:
        filtered_recipes = filter(lambda recipe: product in recipe.products, filtered_recipes)
    if surface is not None:
        pass # TODO implement recipe surface conditions
    return list(filtered_recipes)


def technologies_by(
    unlock_recipe: Recipe|str|None = None,
    unlock_space_location: SpaceLocation|str|None = None,
    unlock_mining_with_fluid: bool|None = None,
) -> list[Technology]:
    filtered_technologies = technologies
    if unlock_recipe is not None:
        filtered_technologies = filter(lambda technology: get_name(unlock_recipe) in technology.unlocked_recipes, filtered_technologies)
    if unlock_space_location is not None:
        filtered_technologies = filter(lambda technology: get_name(unlock_space_location) in technology.unlocked_space_locations, filtered_technologies)
    if unlock_mining_with_fluid is not None:
        filtered_technologies = filter(lambda technology: 'mining-with-fluid' in technology.modifiers, filtered_technologies)
    return list(filtered_technologies)
