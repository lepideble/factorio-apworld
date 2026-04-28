from rule_builder.rules import Rule

from ...data.classes import Surface
from ...data.raw import recipes
from ...data.utils import craftable_recipes, machines_by_category
from ..rules.classes import UnlockedRecipe
from .level import ProductionLevel
from .rules import HasItem

def get_crafting_events(surface: Surface) -> dict[str, tuple[Rule, list[str, ProductionLevel]]]:
    data = {}

    for recipe_name in craftable_recipes:
        recipe = recipes[recipe_name]
        machines = [machine for machine in machines_by_category(recipe.category) if machine.can_be_placed_on(surface)]

        data[f'Craft {recipe_name}'] = (
            UnlockedRecipe(recipe.name)
                & Any([HasItem(machine.name, ProductionLevel.AVAILABLE, surface) for machine in machines])
                & All([HasItem(ingredient_name, ProductionLevel.CRAFTABLE, surface) for ingredient_name in recipe.ingredients]),
            [(product_name, ProductionLevel.CRAFTABLE) for product_name in recipe.products],
        )

        data[f'Automate {recipe_name}'] = (
            UnlockedRecipe(recipe.name)
                & Any([HasItem(machine.name, ProductionLevel.CRAFTABLE, surface) for machine in machines])
                & All([HasItem(ingredient_name, ProductionLevel.AUTOMATED, surface) for ingredient_name in recipe.ingredients]),
            [(product_name, ProductionLevel.AUTOMATED) for product_name in recipe.products],
        )

    return data
