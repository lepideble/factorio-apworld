from collections.abc import Iterable

from rule_builder.rules import HasAny, Rule, True_

from ..config.rules import override_rules
from ..data import craftable_recipes, machines_by_category, recipes, space_locations, surfaces

from .locations import FactorioLocation, FactorioScienceLocation
from .rules_classes import Any, AllRule, AnyRule, CanAutomate, CanCraft, HasMachine, ReachedSpaceLocation, UnlockedRecipe, UnlockedSpaceLocation


def get_rules(locations: Iterable[FactorioLocation]) -> dict[str, Rule]:
    rules = {}

    for surface in surfaces:
        for recipe_name in craftable_recipes:
            recipe = recipes[recipe_name]

            unlocked_recipe = UnlockedRecipe(recipe.name)

            machines = [machine for machine in machines_by_category(recipe.category) if machine.can_be_placed_on(surface)]

            has_machine_for_craft = AnyRule([HasMachine(machine.name, surface.name) for machine in machines])
            has_machine_for_automation = AnyRule([CanCraft(machine.name, surface.name) for machine in machines])

            if recipe.category == 'asteroid-chunk':
                if surface.is_space_platform:
                    space_locations_with_chunk = [space_location for space_location in space_locations if recipe.name in space_location.asteroid_chunks]

                    reached_location = ReachedSpaceLocation(Any(space_locations_with_chunk), surface)

                    rules[f'Craft {recipe.name} on {surface.name}'] = unlocked_recipe & has_machine_for_craft & reached_location
                    rules[f'Automate {recipe.name} on {surface.name}'] = unlocked_recipe & has_machine_for_automation & reached_location
            else:
                can_craft_ingredients = AllRule([CanCraft(ingredient_name, surface.name) for ingredient_name in recipe.ingredients.keys()])
                can_automate_ingredients = AllRule([CanAutomate(ingredient_name, surface.name) for ingredient_name in recipe.ingredients.keys()])

                rules[f'Craft {recipe.name} on {surface.name}'] = unlocked_recipe & has_machine_for_craft & can_craft_ingredients
                rules[f'Automate {recipe.name} on {surface.name}'] = unlocked_recipe & has_machine_for_automation & can_automate_ingredients

        if surface.is_space_platform:
            for space_location in space_locations:
                if not space_location.accessible_at_start:
                    rules[f'Reach {space_location.name} with {surface.name}'] = (
                        UnlockedSpaceLocation(space_location.name)
                            & ReachedSpaceLocation(Any(space_location.connections), surface)
                    )

    for location in locations:
        if isinstance(location, FactorioScienceLocation):
            rules[location.name] = CanAutomate(All(location.ingredients.keys()), Any(surfaces))

    override_rules(locations, rules)

    return rules
