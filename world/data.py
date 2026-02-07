import pkgutil

import orjson

from .config import override_data
from .data_classes import Machine, Recipe, Surface, Technology


data = orjson.loads(pkgutil.get_data(__name__, "config/data.json"))

def get_data(type: str):
    return {k: v for k, v in data[type].items() if not v.get("parameter", False)}


# Machines
machines: dict[str, Machine] = {}

for machine_name, machine_data in get_data("assembling-machine").items():
    machine = Machine(machine_name, set(machine_data["crafting_categories"]))
    machines[machine.name] = machine

for machine_name, machine_data in get_data("asteroid-collector").items():
    machine = Machine(machine_name, {"asteroid-collecting"})
    machines[machine.name] = machine

for machine_name, machine_data in get_data("character").items():
    machine = Machine(machine_name, set(machine_data["crafting_categories"]))
    machines[machine.name] = machine

for machine_name, machine_data in get_data("mining-drill").items():
    machine = Machine(machine_name, set(machine_data["resource_categories"]))
    machines[machine.name] = machine

for machine_name, machine_data in get_data("furnace").items():
    machine = Machine(machine_name, set(machine_data["crafting_categories"]))
    machines[machine.name] = machine

for machine_name, machine_data in get_data("rocket-silo").items():
    machine = Machine(machine_name, set(machine_data["crafting_categories"]))
    machines[machine.name] = machine


# Recipes
recipes: dict[str, Recipe] = {}
recipes_unlocked_at_start: dict[str] = set()
recipes_mining_with_fluid: dict[str] = set()

for asteroid_name, asteroid_data in get_data("asteroid").items():
    recipe = Recipe(
        f"asteroid-collecting-{asteroid_name}",
        "asteroid-collecting",
        {},
        {asteroid_name: 1},
        0,
    )

    recipes[recipe.name] = recipe
    recipes_unlocked_at_start.add(recipe.name)

for recipe_name, recipe_data in get_data("recipe").items():
    recipe = Recipe(
        recipe_name, 
        recipe_data.get("category", "crafting"),
        {ingredient["name"]: ingredient["amount"] for ingredient in recipe_data.get("ingredients", [])},
        {result["name"]: (result["amount"] if "amount" in result else (result["amount_min"] + result["amount_max"]) / 2) * result.get('probability', 1) + result.get('extra_count_fraction', 0) for result in recipe_data.get("results", [])},
        recipe_data.get("energy_required", 0.5)
    )

    recipes[recipe.name] = recipe
    if recipe_data.get("enabled", True):
        recipes_unlocked_at_start.add(recipe.name)

for resource_name, resource_data in get_data("resource").items():
    if "result" in resource_data["minable"]:
        products = {resource_data["minable"]["result"]: 1}
    elif "results" in resource_data["minable"]:
        products = {result_data["name"]: 1 for result_data in resource_data["minable"]["results"]}
    else:
        continue

    recipe = Recipe(
        f"mining-{resource_name}",
        resource_data.get("category", "basic-solid"),
        {resource_data["minable"]["required_fluid"]: resource_data["minable"]["fluid_amount"]} if "required_fluid" in resource_data["minable"] else {},
        products,
        resource_data["minable"]["mining_time"]
    )

    recipes[recipe.name] = recipe
    recipes_unlocked_at_start.add(recipe.name)

    if "required_fluid" in resource_data["minable"]:
        recipes_mining_with_fluid.add(recipe.name)


# Technologies
technologies: dict[str, Technology] = {}

for technology_name, technology_data in get_data("technology").items():
    technology = Technology(technology_name)

    for effect in technology_data.get("effects", []):
        match effect["type"]:
            case "unlock-recipe":
                technology.unlocked_recipes.add(effect["recipe"])
            case "mining-with-fluid":
                technology.unlocked_recipes.update(recipes_mining_with_fluid)
            case "unlock-space-location":
                technology.unlocked_space_locations.add(effect["space_location"])
            case _:
                technology.modifiers.append(effect["type"])

    technologies[technology.name] = technology


# Cleanup
del recipes_mining_with_fluid


# Override
override_data(machines, recipes, recipes_unlocked_at_start, technologies)


# Debug
if __name__ == '__main__':
    for machine in machines.values():
        print(f'Machine: {machine.name}')
        print(f'  categories: {', '.join(machine.categories)}')

    for recipe in recipes.values():
        print(f'Recipe: {recipe.name}')
        print(f'  category: {recipe.category}')
        print(f'  ingredients: {recipe.ingredients}')
        print(f'  products: {recipe.products}')

    for technology in technologies.values():
        print(f'Technologies: {technology.name}')
        if len(technology.unlocked_recipes) > 0:
            print(f'  unlocked_recipes: {', '.join(technology.unlocked_recipes)}')
        if len(technology.unlocked_space_locations) > 0:
            print(f'  unlocked_space_locations: {', '.join(technology.unlocked_space_locations)}')
        if len(technology.modifiers) > 0:
            print(f'  modifiers: {technology.modifiers}')
