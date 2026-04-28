from rule_builder.rules import Rule

from ...data.classes import Surface
from ...data.utils import craftable_recipes, machines_by, manual_crafting_categories
from ..rules import HasItem, HasRecipe

def get_crafting_events(surface: Surface) -> dict[str, tuple[Rule, list[str, bool]]]:
    data = {}

    for recipe in craftable_recipes:
        if recipe.category in manual_crafting_categories:
            data[f'Craft {recipe.name}'] = (
                HasRecipe(recipe)
                    & All([HasItem(item_name, ProductionLevel.CRAFTABLE, surface) for item_name in recipe.ingredients]),
                [(product_name, ProductionLevel.CRAFTABLE) for product_name in recipe.products],
            )

        machines = machines_by(crafting_category=recipe.category, can_be_placed_on=surface)
        if len(machines) > 0:
            data[f'Automate {recipe.name}'] = (
                HasRecipe(recipe)
                    & Any([HasItem(machine.name, ProductionLevel.CRAFTABLE, surface) for machine in machines])
                    & All([HasItem(item_name, ProductionLevel.AUTOMATED, surface) for item_name in recipe.ingredients]),
                [(product_name, ProductionLevel.AUTOMATED) for product_name in recipe.products],
            )

    return data
