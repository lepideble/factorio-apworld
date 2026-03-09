from collections.abc import Iterable

from rule_builder.rules import HasAny, Rule, True_

from ..config.rules import override_rules
from ..data import craftable_recipes, machines_by_category, recipes, space_locations, space_locations_accessible_at_start, surfaces

from .locations import FactorioLocation, FactorioScienceLocation
from .rules_classes import All, Any, CanAutomate, CanCraft, HasMachine, UnlockedRecipe, UnlockedSpaceLocation


def get_rules(locations: Iterable[FactorioLocation]) -> dict[str, Rule]:
    rules = {}

    for surface in surfaces:
        for recipe_name in craftable_recipes:
            recipe = recipes[recipe_name]

            rules[f'Craft {recipe.name} on {surface.name}'] = (
                UnlockedRecipe(recipe.name)
                    & Any([HasMachine(machine.name, surface.name) for machine in machines_by_category(recipe.category) if machine.can_be_placed_on(surface)])
                    & All([CanCraft(ingredient_name, surface.name) for ingredient_name in recipe.ingredients.keys()])
            )

            rules[f'Automate {recipe.name} on {surface.name}'] = (
                UnlockedRecipe(recipe.name)
                    & Any([HasMachine(machine.name, surface.name) for machine in machines_by_category(recipe.category) if machine.can_be_placed_on(surface) and machine.name != 'character'])
                    & All([CanAutomate(ingredient_name, surface.name) for ingredient_name in recipe.ingredients.keys()])
            )

        if surface.is_space_platform:
            for space_location in space_locations:
                if space_location.name in space_locations_accessible_at_start:
                    rules[f'Reach {space_location.name} with {surface.name}'] = True_()
                else:
                    rules[f'Reach {space_location.name} with {surface.name}'] = (
                        UnlockedSpaceLocation(space_location.name)
                            & HasAny(*[f'Reach {connection} with {surface.name}' for connection in space_location.connections])
                    )

    for location in locations:
        if isinstance(location, FactorioScienceLocation):
            rules[location.name] = All([Any([CanAutomate(science_pack, surface.name) for surface in surfaces]) for science_pack in location.ingredients.keys()])

    override_rules(locations, rules)

    return rules
