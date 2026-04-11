from collections.abc import Iterable

from rule_builder.rules import HasAny, Rule, True_

from ..config.rules import override_rules
from ..data import machines_by_category, recipes, space_locations, surfaces
from ..data_utils import craftable_recipes
from .locations import FactorioLocation, FactorioCraftLocation, FactorioScienceLocation
from .rules_classes import All, Any, CanAutomate, CanCraft, HasMachine, ReachedSpaceLocation, UnlockedRecipe, UnlockedSpaceLocation


def get_rules(locations: Iterable[FactorioLocation]) -> dict[str, Rule]:
    rules = {}

    for surface in surfaces:
        for recipe_name in craftable_recipes:
            recipe = recipes[recipe_name]

            unlocked_recipe = UnlockedRecipe(recipe.name)

            machines = [machine for machine in machines_by_category(recipe.category) if machine.can_be_placed_on(surface)]

            has_machine_for_craft = Any([HasMachine(machine.name, surface.name) for machine in machines])
            has_machine_for_automation = Any([CanCraft(machine.name, surface.name) for machine in machines])

            if recipe.category == 'asteroid-chunk':
                if surface.is_space_platform:
                    space_locations_with_chunk = [space_location for space_location in space_locations if recipe.name in space_location.asteroid_chunks]

                    reached_location = Any([ReachedSpaceLocation(space_location, surface) for space_location in space_locations_with_chunk])

                    rules[f'Craft {recipe.name} on {surface.name}'] = unlocked_recipe & has_machine_for_craft & reached_location
                    rules[f'Automate {recipe.name} on {surface.name}'] = unlocked_recipe & has_machine_for_automation & reached_location
            else:
                can_craft_ingredients = All([CanCraft(ingredient_name, surface.name) for ingredient_name in recipe.ingredients.keys()])
                can_automate_ingredients = All([CanAutomate(ingredient_name, surface.name) for ingredient_name in recipe.ingredients.keys()])

                rules[f'Craft {recipe.name} on {surface.name}'] = unlocked_recipe & has_machine_for_craft & can_craft_ingredients
                rules[f'Automate {recipe.name} on {surface.name}'] = unlocked_recipe & has_machine_for_automation & can_automate_ingredients

        if surface.is_space_platform:
            for space_location in space_locations:
                if not space_location.accessible_at_start:
                    rules[f'Reach {space_location.name} with {surface.name}'] = (
                        UnlockedSpaceLocation(space_location.name)
                            & Any([ReachedSpaceLocation(connection, surface) for connection in space_location.connections])
                    )

    for location in locations:
        if isinstance(location, FactorioCraftLocation):
            rules[location.name] = Any([CanCraft(location.item_name, surface.name) for surface in surfaces])

        if isinstance(location, FactorioScienceLocation):
            # Early science locations can be recognised by the fact that they already have an item
            if location.item is not None:
                rules[location.name] = All([Any([CanCraft(science_pack, surface.name) for surface in surfaces]) for science_pack in location.ingredients.keys()])
            else:
                rules[location.name] = All([Any([CanAutomate(science_pack, surface.name) for surface in surfaces]) for science_pack in location.ingredients.keys()])

    override_rules(locations, rules)

    return rules
