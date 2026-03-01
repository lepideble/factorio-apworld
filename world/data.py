import pkgutil

import orjson

from .config import override_data
from .data_classes import Lab, Machine, Recipe, Surface, SurfaceCondition, Table, Technology


data = orjson.loads(pkgutil.get_data(__name__, 'config/data.json'))

def get_data(type: str):
    return ((k, v) for k, v in data[type].items() if not v.get('parameter', False))


# Surfaces
surfaces = Table()
surfaces_accessible_at_start = {'nauvis'}

for surface_name, surface_data in get_data('surface'):
    surfaces.add(Surface(surface_name, surface_data['surface_properties']))

for planet_name, planet_data in get_data('planet'):
    surfaces.add(Surface(planet_name, planet_data['surface_properties']))


# Machines
machines = Table()

for machine_name, machine_data in get_data("assembling-machine"):
    machines.add(Machine(machine_name, set(machine_data["crafting_categories"])))

for machine_name, machine_data in get_data("asteroid-collector"):
    machines.add(Machine(machine_name, {"asteroid-collecting"}))

for machine_name, machine_data in get_data("character"):
    machines.add(Machine(machine_name, set(machine_data["crafting_categories"])))

for machine_name, machine_data in get_data("mining-drill"):
    machines.add(Machine(machine_name, set(machine_data["resource_categories"])))

for machine_name, machine_data in get_data("furnace"):
    machines.add(Machine(machine_name, set(machine_data["crafting_categories"])))

for machine_name, machine_data in get_data("rocket-silo"):
    machines.add(Machine(machine_name, set(machine_data["crafting_categories"])))


# Science lab
labs = Table()

for lab_name, lab_data in get_data('lab'):
    labs.add(Lab(
        lab_name,
        set(lab_data['inputs']),
        [SurfaceCondition(surface_condition['property'], surface_condition.get('min'), surface_condition.get('max')) for surface_condition in lab_data.get('surface_conditions', [])],
    ))


# Recipes
recipes = Table()
recipes_unlocked_at_start: dict[str] = set()
recipes_mining_with_fluid: dict[str] = set()

for asteroid_name, asteroid_data in get_data("asteroid"):
    recipe = Recipe(
        f"asteroid-collecting-{asteroid_name}",
        "asteroid-collecting",
        {},
        {asteroid_name: 1},
        0,
    )

    recipes.add(recipe)
    recipes_unlocked_at_start.add(recipe.name)

for recipe_name, recipe_data in get_data('recipe'):
    recipe = Recipe(
        recipe_name, 
        recipe_data.get("category", "crafting"),
        {ingredient["name"]: ingredient["amount"] for ingredient in recipe_data.get("ingredients", [])},
        {result["name"]: (result["amount"] if "amount" in result else (result["amount_min"] + result["amount_max"]) / 2) * result.get('probability', 1) + result.get('extra_count_fraction', 0) for result in recipe_data.get("results", [])},
        recipe_data.get("energy_required", 0.5)
    )

    recipes.add(recipe)
    if recipe_data.get("enabled", True):
        recipes_unlocked_at_start.add(recipe.name)

for resource_name, resource_data in get_data("resource"):
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

    recipes.add(recipe)
    recipes_unlocked_at_start.add(recipe.name)

    if "required_fluid" in resource_data["minable"]:
        recipes_mining_with_fluid.add(recipe.name)


# Science packs
# this is a list because keeping the order in which they are defined is important
science_packs = list()

for tool_name, tool_data in get_data('tool'):
    if tool_data['subgroup'] == 'science-pack':
        science_packs.append(tool_name)


# Technologies
technologies = Table()

for technology_name, technology_data in get_data('technology'):
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

    technologies.add(technology)


# Cleanup
del recipes_mining_with_fluid


# Override
override_data(
    machines=machines,
    recipes=recipes,
    recipes_unlocked_at_start=recipes_unlocked_at_start,
    science_packs=science_packs,
    surfaces=surfaces,
    surfaces_accessible_at_start=surfaces_accessible_at_start,
    technologies=technologies,
)
