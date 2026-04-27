from rule_builder.rules import Rule

from ...data.classes import Surface
from ...data.utils import craftable_recipes, machines_by, manual_crafting_categories
from ..rules import HasItem, HasRecipe

def get_crafting_events(surface: Surface) -> dict[str, tuple[Rule, list[str, bool]]]:
    events = {}

    for recipe in craftable_recipes:
        if recipe.category in manual_crafting_categories:
            events[f'Craft {recipe.name}'] = (
                HasRecipe(recipe)
                    & All([HasItem(item_name, surface) for item_name in recipe.ingredients]),
                [(product_name, False) for product_name in recipe.products],
            )

        machines = machines_by(crafting_category=recipe.category, can_be_placed_on=surface)
        if len(machines) > 0:
            events[f'Automate {recipe.name}'] = (
                HasRecipe(recipe)
                    & Any([HasItem(machine.name, surface) for machine in machines])
                    & All([HasItem(item_name, surface, True) for item_name in recipe.ingredients]),
                [(product_name, True) for product_name in recipe.products],
            )

    return events
