from collections.abc import Iterable

from rule_builder.rules import HasAny, Rule

from ..data import recipes, space_locations
from ..world.locations import FactorioLocation
from ..world.rules_classes import CanAutomate, CanCraft, HasMachine, UnlockedRecipe


def override_rules(locations: Iterable[FactorioLocation], rules: dict[str, Rule]):
    # Crafting with starting supplies
    rules['Craft crudeic-asteroid-crushing on space-platform'] = UnlockedRecipe('crudeic-asteroid-crushing') & CanCraft('crudeic-asteroid-chunk', 'space-platform')
    rules['Craft metallic-asteroid-crushing on space-platform'] = UnlockedRecipe('metallic-asteroid-crushing') & CanCraft('metallic-asteroid-chunk', 'space-platform')
    rules['Craft oxide-asteroid-crushing on space-platform'] = UnlockedRecipe('oxide-asteroid-crushing') & CanCraft('oxide-asteroid-chunk', 'space-platform')

    rules['Craft copper-plate on space-platform'] = UnlockedRecipe('copper-plate') & CanCraft('copper-ore', 'space-platform')
    rules['Craft iron-plate on space-platform'] = UnlockedRecipe('iron-plate') & CanCraft('iron-ore', 'space-platform')
    rules['Craft lithium-plate on space-platform'] = UnlockedRecipe('lithium-plate') & CanCraft('lithium', 'space-platform')
    rules['Craft steel-plate on space-platform'] = UnlockedRecipe('steel-plate') & CanCraft('iron-plate', 'space-platform')
    rules['Craft stone-brick on space-platform'] = UnlockedRecipe('stone-brick') & CanCraft('stone', 'space-platform')

    rules['Craft engine-unit on space-platform'] = UnlockedRecipe('engine-unit') & CanCraft('iron-gear-wheel', 'space-platform') & CanCraft('pipe', 'space-platform') & CanCraft('steel-plate', 'space-platform')

    # Space location rules
    can_destroy_medium_asterorid = CanCraft('gun-turret', 'space-platform') & CanAutomate('firearm-magazine', 'space-platform')
    can_destroy_big_asterorid = CanCraft('rocket-turret', 'space-platform') & CanAutomate('rocket', 'space-platform') & can_destroy_medium_asterorid
    can_destroy_huge_asterorid = CanCraft('railgun-turret', 'space-platform') & CanAutomate('railgun-ammo', 'space-platform') & can_destroy_big_asterorid

    has_truster_and_propellants = CanCraft('thruster', 'space-platform') & CanAutomate('thruster-fuel', 'space-platform') & CanAutomate('thruster-oxidizer', 'space-platform')

    rules['Reach fulgora with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach gleba with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach vulcanus with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach aquilo with space-platform'] &= can_destroy_big_asterorid & has_truster_and_propellants
    rules['Reach solar-system-edge with space-platform'] &= can_destroy_huge_asterorid & has_truster_and_propellants
    rules['Reach shattered-planet with space-platform'] &= can_destroy_huge_asterorid & has_truster_and_propellants

    # Asteroid collection
    for recipe in filter(lambda recipe: recipe.category == 'asteroid-chunk', recipes):
        space_locations_with_chunk = [space_location for space_location in space_locations if recipe.name in space_location.asteroid_chunks]

        unlocked_recipe = UnlockedRecipe(recipe.name)
        reached_location = HasAny(*[f'Reach {space_location.name} with space-platform' for space_location in space_locations_with_chunk])

        rules[f'Craft {recipe.name} on space-platform'] = unlocked_recipe & reached_location
        rules[f'Automate {recipe.name} on space-platform'] = unlocked_recipe & reached_location & HasMachine('asteroid-collector', 'space-platform')
