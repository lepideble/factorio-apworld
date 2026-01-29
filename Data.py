import pkgutil
import orjson

class FactorioElement:
    name: str

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        return hash(self.name)


class Machine(FactorioElement):
    def __init__(self, name, categories):
        self.name: str = name
        self.categories: set = categories

class Recipe(FactorioElement):
    name: str
    category: str
    ingredients: dict[str, int]
    products: dict[str, int]
    time: float

    def __init__(self, name: str, category: str, ingredients: dict[str, int], products: dict[str, int], time: float):
        self.name = name
        self.category = category
        self.ingredients = ingredients
        self.products = products
        self.time = time


data = orjson.loads(pkgutil.get_data(__name__, "config/data.json"))


# Recipes
recipes: dict[str, Recipe] = {}
recipes_unlocked_at_start: dict[str] = set()
recipes_mining_with_fluid: dict[str] = set()

for asteroid_name, asteroid_data in data["asteroid"].items():
    if asteroid_data.get("parameter", False):
        continue

    recipe = Recipe(
        f"collecting-{asteroid_name}",
        "asteroid-collecting",
        {},
        {asteroid_name: 1},
        0,
    )
    recipes[recipe.name] = recipe

for recipe_name, recipe_data in data["recipe"].items():
    if recipe_data.get("parameter", False):
        continue

    recipe = Recipe(
        recipe_name, 
        recipe_data.get("category", "crafting"),
        {ingredient["name"]: ingredient["amount"] for ingredient in recipe_data.get("ingredients", [])},
        {result["name"]: result["amount"] if "amount" in result else (result["amount_min"] + result["amount_max"]) / 2 for result in recipe_data.get("results", [])},
        recipe_data.get("energy_required", 0.5)
    )
    recipes[recipe.name] = recipe

    if recipe_data.get("enabled", True):
        recipes_unlocked_at_start.add(recipe_name)

for resource_name, resource_data in data["resource"].items():
    if resource_data.get("parameter", False):
        continue

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

    if "required_fluid" in resource_data["minable"]:
        recipes_mining_with_fluid.add(recipe.name)


# Machines
machines: dict[str, Machine] = {}

for machine_name, machine_data in data["assembling-machine"].items():
    machine = Machine(machine_name, set(machine_data["crafting_categories"]))
    machines[machine.name] = machine

for machine_name, machine_data in data["asteroid-collector"].items():
    machine = Machine(machine_name, {"asteroid-collecting"})
    machines[machine.name] = machine

for machine_name, machine_data in data["character"].items():
    machine = Machine(machine_name, set(machine_data["crafting_categories"]))
    machines[machine.name] = machine

for machine_name, machine_data in data["mining-drill"].items():
    machine = Machine(machine_name, set(machine_data["resource_categories"]))
    machines[machine.name] = machine

for machine_name, machine_data in data["furnace"].items():
    machine = Machine(machine_name, set(machine_data["crafting_categories"]))
    machines[machine.name] = machine

for machine_name, machine_data in data["rocket-silo"].items():
    machine = Machine(machine_name, set(machine_data["crafting_categories"]))
    machines[machine.name] = machine