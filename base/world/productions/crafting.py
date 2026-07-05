from rule_builder.rules import Rule, True_

from ...data.classes import Surface
from ...data.lookup import machines_by
from ...data.raw import machines_for_manual_craft
from ...data.utils import unlockable_recipes
from ..rules import All, Any, HasProduction, UnlockedRecipe

def get_crafting_productions(surface: Surface) -> dict[str, tuple[Rule, dict[str, bool]]]:
    events = {}

    for recipe in unlockable_recipes:
        machines = machines_by(can_be_placed_on=surface, crafting_category=recipe.category)

        if len(machines) == 0:
            continue

        can_manual_craft = len(machines_for_manual_craft.intersection((machine.name for machine in machines))) > 0

        unlocked_recipe_rule = UnlockedRecipe(recipe)
        has_machine_rule = Any([HasProduction(machine.name, surface) for machine in machines])

        events[f'Craft {recipe.name}'] = (
            unlocked_recipe_rule
                & (True_() if can_manual_craft else has_machine_rule)
                & All([HasProduction(item_name, surface) for item_name in recipe.ingredients]),
            {product_name: False for product_name in recipe.products},
        )

        events[f'Automate {recipe.name} crafting'] = (
            unlocked_recipe_rule
                & has_machine_rule
                & All([HasProduction(item_name, surface, True) for item_name in recipe.ingredients]),
            {product_name: True for product_name in recipe.products},
        )

    return events
